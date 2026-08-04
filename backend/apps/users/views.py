import logging
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.audit.models import AuditAction
from apps.audit.utils import log_audit_event
from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin

from .models import CounselorProfile, Profile, Role, User, UserSession
from .serializers import (
    AdminPromoteCounselorSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    CounselorProfileSerializer,
    EmailVerificationConfirmSerializer,
    MindCareTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfilePictureUploadSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserSessionSerializer,
)
from .tasks import send_password_reset_email, send_verification_email
from .tokens import issue_email_verification_token, issue_password_reset_token

logger = logging.getLogger("apps")


def _send_email_safely(send_fn, *args):
    """
    Email delivery is an external dependency that has already failed
    outright on Render's free tier once (SMTP unreachable) — under
    CELERY_TASK_ALWAYS_EAGER, `.delay()` runs inline and re-raises
    whatever the real send failure is, which would otherwise 500 the
    whole request (registration, resend, password-reset) just because
    the notification email didn't go out. The token is already issued
    either way, so the user can still retry "Resend code" once delivery
    is fixed rather than being blocked outright.
    """
    try:
        send_fn.delay(*args)
    except Exception:  # noqa: BLE001 - any email backend failure shouldn't fail the request
        logger.exception("Failed to send email via %s", send_fn.__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = issue_email_verification_token(user)
        _send_email_safely(send_verification_email, user.email, user.first_name, token.token)
        log_audit_event(AuditAction.PROFILE_UPDATED, user=user, request=request, event="account_created")

        from apps.notifications.models import NotificationChannel, NotificationType
        from apps.notifications.services import notify

        notify(
            user,
            NotificationType.SYSTEM,
            "Welcome to MindCare AI",
            "Your account has been created. Check your email for a verification code to get started.",
            channel=NotificationChannel.IN_APP,
        )

        return Response(
            {"message": "Account created. Check your email for a verification code.", "user_id": str(user.id)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = MindCareTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        incoming = request.data.get("refresh")
        old_jti = None
        if incoming:
            try:
                old_jti = str(RefreshToken(incoming)["jti"])
            except TokenError:
                old_jti = None

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and old_jti:
            new_refresh = response.data.get("refresh")
            if new_refresh:
                new_token = RefreshToken(new_refresh)
                UserSession.objects.filter(refresh_token_jti=old_jti).update(
                    refresh_token_jti=str(new_token["jti"]),
                    expires_at=datetime.fromtimestamp(new_token["exp"], tz=dt_timezone.utc),
                )
        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            jti = str(token["jti"])
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or already-expired token."}, status=status.HTTP_400_BAD_REQUEST)

        UserSession.objects.filter(user=request.user, refresh_token_jti=jti).update(revoked_at=timezone.now())
        log_audit_event(AuditAction.LOGOUT, user=request.user, request=request)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class LogoutAllView(APIView):
    """Revoke every active session/refresh token for the current user (e.g. "sign out everywhere")."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        for outstanding in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
        UserSession.objects.filter(user=request.user, revoked_at__isnull=True).update(revoked_at=timezone.now())
        log_audit_event(AuditAction.LOGOUT, user=request.user, request=request, scope="all_sessions")
        return Response(status=status.HTTP_205_RESET_CONTENT)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        from .models import EmailVerificationToken

        user = User.objects.filter(email__iexact=email).first()
        pending = (
            EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).order_by("-created_at").first()
            if user
            else None
        )

        if not pending or not pending.is_valid():
            return Response({"detail": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)

        if pending.token != otp:
            pending.attempts += 1
            pending.save(update_fields=["attempts"])
            return Response({"detail": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        pending.used_at = timezone.now()
        pending.save(update_fields=["used_at"])

        log_audit_event(AuditAction.EMAIL_VERIFIED, user=user, request=request)
        return Response({"message": "Email verified successfully."})


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()

        if user and not user.is_email_verified:
            token = issue_email_verification_token(user)
            _send_email_safely(send_verification_email, user.email, user.first_name, token.token)

        # Always return a generic message — do not reveal whether the email exists.
        return Response({"message": "If that account exists and is unverified, a new email has been sent."})


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()

        if user:
            from apps.common.utils import get_client_ip

            token = issue_password_reset_token(user, requested_ip=get_client_ip(request))
            _send_email_safely(send_password_reset_email, user.email, user.first_name, token.token)
            log_audit_event(AuditAction.PASSWORD_RESET_REQUESTED, user=user, request=request)

        return Response({"message": "If that account exists, a password reset email has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from .models import PasswordResetToken

        user = User.objects.filter(email__iexact=data["email"]).first()
        pending = (
            PasswordResetToken.objects.filter(user=user, used_at__isnull=True).order_by("-created_at").first()
            if user
            else None
        )

        if not pending or not pending.is_valid():
            return Response({"detail": "Invalid or expired reset code."}, status=status.HTTP_400_BAD_REQUEST)

        if pending.token != data["otp"]:
            pending.attempts += 1
            pending.save(update_fields=["attempts"])
            return Response({"detail": "Invalid or expired reset code."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data["new_password"])
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        pending.used_at = timezone.now()
        pending.save(update_fields=["used_at"])

        # Force re-authentication everywhere after a password reset.
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
        UserSession.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())

        log_audit_event(AuditAction.PASSWORD_RESET_COMPLETED, user=user, request=request)
        return Response({"message": "Password reset successfully. Please log in again."})


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        log_audit_event(AuditAction.PASSWORD_CHANGED, user=user, request=request)
        return Response({"message": "Password changed successfully."})


class UserSessionListView(generics.ListAPIView):
    """A user typically has a handful of active sessions — unpaginated so the Settings page gets them all in one call."""

    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user).order_by("-created_at")


class RevokeSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, session_id):
        session = UserSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        outstanding = OutstandingToken.objects.filter(jti=session.refresh_token_jti).first()
        if outstanding:
            BlacklistedToken.objects.get_or_create(token=outstanding)
        session.revoked_at = timezone.now()
        session.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save()
        log_audit_event(AuditAction.PROFILE_UPDATED, user=self.request.user, request=self.request)


class ProfilePictureUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfilePictureUploadSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data)


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["role", "is_active", "is_email_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "last_login", "email"]
    queryset = User.objects.all().order_by("-created_at")


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdmin]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return AdminUserUpdateSerializer
        return AdminUserSerializer

    def perform_update(self, serializer):
        from apps.admin_panel.models import AdminActionLog

        target = self.get_object()
        before = {"role": target.role, "is_active": target.is_active}
        user = serializer.save()
        AdminActionLog.objects.create(
            admin_user=self.request.user,
            action="user_updated",
            target_model="User",
            target_id=str(user.id),
            description=f"Changed {before} -> role={user.role}, is_active={user.is_active}",
        )
        log_audit_event(AuditAction.ADMIN_ACTION, user=self.request.user, request=self.request, target_user=str(user.id))


class CounselorListView(generics.ListAPIView):
    """Public-to-authenticated-users listing of counselors available for booking."""

    serializer_class = CounselorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return CounselorProfile.objects.filter(
            is_accepting_appointments=True, approved_by_admin=True
        ).select_related("user")


class AdminCounselorListView(generics.ListAPIView):
    serializer_class = CounselorProfileSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = CounselorProfile.objects.all().select_related("user")


class AdminCounselorDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CounselorProfileSerializer
    permission_classes = [IsAdmin]
    queryset = CounselorProfile.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        from apps.admin_panel.models import AdminActionLog

        instance = serializer.save()
        AdminActionLog.objects.create(
            admin_user=self.request.user,
            action="counselor_updated",
            target_model="CounselorProfile",
            target_id=str(instance.id),
            description=f"approved={instance.approved_by_admin}, accepting={instance.is_accepting_appointments}",
        )


class PromoteToCounselorView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = AdminPromoteCounselorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.get(id=data["user_id"])
        user.role = Role.COUNSELOR
        user.save(update_fields=["role"])

        counselor_profile = CounselorProfile.objects.create(
            user=user,
            specialization=data["specialization"],
            license_number=data["license_number"],
            years_of_experience=data["years_of_experience"],
            bio=data["bio"],
            approved_by_admin=True,
        )

        from apps.admin_panel.models import AdminActionLog

        AdminActionLog.objects.create(
            admin_user=request.user,
            action="user_promoted_to_counselor",
            target_model="User",
            target_id=str(user.id),
        )
        return Response(CounselorProfileSerializer(counselor_profile).data, status=status.HTTP_201_CREATED)


