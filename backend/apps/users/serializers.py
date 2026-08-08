import logging
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.models import AuditAction
from apps.audit.utils import log_audit_event
from apps.common.utils import get_client_ip, get_user_agent
from apps.common.validators import validate_image_file

from .models import Profile, Role, User, UserSession
from .tasks import send_account_locked_email

logger = logging.getLogger("apps")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "pseudonym", "role", "is_email_verified", "created_at"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    age_confirmed = serializers.BooleanField(write_only=True)
    consent_accepted = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "pseudonym", "password", "password_confirm", "age_confirmed", "consent_accepted"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_pseudonym(self, value):
        if User.objects.filter(pseudonym__iexact=value).exists():
            raise serializers.ValidationError("This pseudonym is already taken.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        if not attrs.get("age_confirmed"):
            raise serializers.ValidationError({"age_confirmed": "You must confirm you are 18 or older to continue."})
        if not attrs.get("consent_accepted"):
            raise serializers.ValidationError({"consent_accepted": "You must accept the privacy notice to continue."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("age_confirmed")
        validated_data.pop("consent_accepted")
        password = validated_data.pop("password")
        now = timezone.now()
        user = User.objects.create_user(
            password=password, age_confirmed_at=now, consent_accepted_at=now, **validated_data
        )
        return user


class MindCareTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT's login serializer with: custom claims, "remember me"
    (extends refresh token lifetime), account lockout after repeated
    failures, `UserSession` bookkeeping, and audit logging.
    """

    remember_me = serializers.BooleanField(required=False, default=False, write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["pseudonym"] = user.pseudonym
        return token

    def _register_failed_attempt(self, user):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
            user.locked_until = timezone.now() + timezone.timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES
            )
            try:
                send_account_locked_email.delay(user.email, user.pseudonym, user.locked_until.isoformat())
            except Exception:  # noqa: BLE001 - an email backend failure shouldn't break the login attempt itself
                logger.exception("Failed to send account-locked email to %s", user.email)
        user.save(update_fields=["failed_login_attempts", "locked_until"])

    def validate(self, attrs):
        remember_me = attrs.pop("remember_me", False)
        request = self.context.get("request")
        email = attrs.get(self.username_field, "")

        candidate = User.objects.filter(email__iexact=email).first()
        if candidate and candidate.is_locked:
            log_audit_event(
                AuditAction.LOGIN_FAILED, user=candidate, request=request,
                reason="account_locked",
            )
            raise exceptions.AuthenticationFailed(
                "This account is temporarily locked due to repeated failed login attempts.",
                code="account_locked",
            )

        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed:
            if candidate:
                self._register_failed_attempt(candidate)
            log_audit_event(
                AuditAction.LOGIN_FAILED, user=candidate, request=request, email=email,
            )
            raise

        user = self.user
        if not user.is_email_verified:
            log_audit_event(
                AuditAction.LOGIN_FAILED,
                user=user,
                request=request,
                reason="email_not_verified",
            )
            raise exceptions.AuthenticationFailed(
                "This account's email address has not been verified.",
                code="email_not_verified",
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed("This account has been deactivated.", code="account_inactive")

        user.failed_login_attempts = 0
        user.locked_until = None
        if request is not None:
            user.last_login_ip = get_client_ip(request)
        user.save(update_fields=["failed_login_attempts", "locked_until", "last_login_ip"])

        refresh = RefreshToken(data["refresh"])
        if remember_me:
            refresh.set_exp(lifetime=settings.JWT_REMEMBER_ME_REFRESH_LIFETIME)
            data["refresh"] = str(refresh)

        UserSession.objects.create(
            user=user,
            refresh_token_jti=str(refresh["jti"]),
            remember_me=remember_me,
            device_label=get_user_agent(request)[:255] if request else "",
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else "",
            expires_at=datetime.fromtimestamp(refresh["exp"], tz=dt_timezone.utc),
        )
        log_audit_event(AuditAction.LOGIN_SUCCESS, user=user, request=request)

        data["user"] = UserSerializer(user).data
        return data


class EmailVerificationConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        validate_password(attrs["new_password"])
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        validate_password(attrs["new_password"])
        return attrs


class DeleteAccountSerializer(serializers.Serializer):
    """Requires the current password so a hijacked session/CSRF-style call can't delete an account silently."""

    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "profile_picture", "bio", "timezone", "theme_preference", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "profile_picture", "created_at", "updated_at"]


class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(validators=[validate_image_file])

    class Meta:
        model = Profile
        fields = ["profile_picture"]


class UserSessionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            "id", "device_label", "ip_address", "remember_me",
            "created_at", "expires_at", "revoked_at", "is_active",
        ]

    def get_is_active(self, obj):
        return obj.is_active()


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "pseudonym", "role",
            "is_active", "is_email_verified", "is_locked", "created_at", "last_login",
        ]
        read_only_fields = ["id", "email", "created_at", "last_login", "is_locked"]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role", "is_active"]

    def validate(self, attrs):
        request = self.context.get("request")
        is_self = request and self.instance and self.instance == request.user
        if is_self and attrs.get("role") not in (None, Role.ADMIN):
            raise serializers.ValidationError({"role": "You can't remove your own admin access."})
        if is_self and attrs.get("is_active") is False:
            raise serializers.ValidationError({"is_active": "You can't suspend your own account."})
        return attrs
