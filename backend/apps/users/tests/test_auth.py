import pytest
from django.conf import settings
from rest_framework import status

from apps.users.models import EmailVerificationToken, PasswordResetToken, User

pytestmark = pytest.mark.django_db


class TestRegistration:
    def test_register_creates_inactive_unverified_user_and_sends_email(self, api_client, mailoutbox):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new.user@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "CorrectHorse42!",
                "password_confirm": "CorrectHorse42!",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email="new.user@example.com")
        assert user.is_email_verified is False
        assert user.check_password("CorrectHorse42!")
        assert EmailVerificationToken.objects.filter(user=user).exists()
        assert len(mailoutbox) == 1
        assert "verify" in mailoutbox[0].subject.lower()

    def test_register_rejects_duplicate_email(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": user.email,
                "first_name": "Dup",
                "last_name": "User",
                "password": "CorrectHorse42!",
                "password_confirm": "CorrectHorse42!",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_rejects_mismatched_passwords(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "mismatch@example.com",
                "first_name": "A",
                "last_name": "B",
                "password": "CorrectHorse42!",
                "password_confirm": "SomethingElse99!",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_rejects_weak_password(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "weak@example.com",
                "first_name": "A",
                "last_name": "B",
                "password": "password",
                "password_confirm": "password",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    def test_login_succeeds_with_correct_credentials(self, api_client, user):
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == user.email

    def test_login_fails_with_wrong_password(self, api_client, user):
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrong-password"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_locks_account_after_repeated_failures(self, api_client, user):
        for _ in range(settings.ACCOUNT_LOCKOUT_THRESHOLD):
            api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrong-password"})

        user.refresh_from_db()
        assert user.is_locked is True

        # By this point the "auth" scope's rate limit may *also* be
        # exhausted (both defenses default to the same threshold) — either
        # 401 (lockout) or 429 (rate limit) correctly means "denied", and
        # this test only cares that a locked account can't log in, not
        # which of the two layered defenses catches it first.
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_successful_login_resets_failed_attempts(self, api_client, user):
        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrong-password"})
        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})

        user.refresh_from_db()
        assert user.failed_login_attempts == 0

    def test_login_creates_user_session(self, api_client, user):
        from apps.users.models import UserSession

        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert UserSession.objects.filter(user=user).count() == 1

    def test_remember_me_extends_refresh_token_lifetime(self, api_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        response = api_client.post(
            "/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!", "remember_me": True}
        )
        refresh = RefreshToken(response.data["refresh"])
        lifetime = refresh["exp"] - refresh["iat"]
        assert lifetime == int(settings.JWT_REMEMBER_ME_REFRESH_LIFETIME.total_seconds())

    def test_login_rejects_inactive_user(self, api_client, user):
        user.is_active = False
        user.save()
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    def test_logout_blacklists_refresh_token(self, api_client, user):
        login = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        access, refresh = login.data["access"], login.data["refresh"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = api_client.post("/api/v1/auth/logout/", {"refresh": refresh})
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

        refresh_response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh})
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEmailVerification:
    def test_verify_email_with_valid_otp(self, api_client, user):
        user.is_email_verified = False
        user.save()
        token = EmailVerificationToken.objects.create(
            user=user, token="123456", expires_at=EmailVerificationToken.default_expiry()
        )

        response = api_client.post("/api/v1/auth/verify-email/", {"email": user.email, "otp": token.token})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_email_verified is True

    def test_verify_email_with_wrong_otp_fails(self, api_client, user):
        EmailVerificationToken.objects.create(
            user=user, token="123456", expires_at=EmailVerificationToken.default_expiry()
        )
        response = api_client.post("/api/v1/auth/verify-email/", {"email": user.email, "otp": "000000"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_for_unknown_email_fails(self, api_client):
        response = api_client.post(
            "/api/v1/auth/verify-email/", {"email": "nobody@example.com", "otp": "123456"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_with_expired_otp_fails(self, api_client, user):
        from django.utils import timezone

        token = EmailVerificationToken.objects.create(
            user=user, token="123456", expires_at=timezone.now() - timezone.timedelta(hours=1)
        )
        response = api_client.post("/api/v1/auth/verify-email/", {"email": user.email, "otp": token.token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_otp_is_locked_out_after_max_attempts(self, api_client, user):
        from django.core.cache import cache

        token = EmailVerificationToken.objects.create(
            user=user, token="123456", expires_at=EmailVerificationToken.default_expiry()
        )

        for _ in range(EmailVerificationToken.MAX_ATTEMPTS):
            api_client.post("/api/v1/auth/verify-email/", {"email": user.email, "otp": "000000"})

        # Clear the throttle's own request-count cache — it isn't what this
        # test targets, and would otherwise 429 before the model-level
        # attempts lockout (asserted below) even gets exercised.
        cache.clear()
        response = api_client.post("/api/v1/auth/verify-email/", {"email": user.email, "otp": token.token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPasswordReset:
    def test_request_reset_does_not_reveal_whether_email_exists(self, api_client):
        known = api_client.post("/api/v1/auth/password-reset/request/", {"email": "unknown@example.com"})
        assert known.status_code == status.HTTP_200_OK

    def test_confirm_reset_with_valid_otp_changes_password(self, api_client, user):
        token = PasswordResetToken.objects.create(
            user=user, token="123456", expires_at=PasswordResetToken.default_expiry()
        )

        response = api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "email": user.email,
                "otp": token.token,
                "new_password": "BrandNewPass99!",
                "new_password_confirm": "BrandNewPass99!",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("BrandNewPass99!")

    def test_confirm_reset_with_wrong_otp_fails(self, api_client, user):
        PasswordResetToken.objects.create(
            user=user, token="123456", expires_at=PasswordResetToken.default_expiry()
        )
        response = api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "email": user.email,
                "otp": "000000",
                "new_password": "BrandNewPass99!",
                "new_password_confirm": "BrandNewPass99!",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_revokes_existing_sessions(self, api_client, user):
        from apps.users.models import UserSession

        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert UserSession.objects.filter(user=user, revoked_at__isnull=True).exists()

        token = PasswordResetToken.objects.create(
            user=user, token="123456", expires_at=PasswordResetToken.default_expiry()
        )
        api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "email": user.email,
                "otp": token.token,
                "new_password": "BrandNewPass99!",
                "new_password_confirm": "BrandNewPass99!",
            },
        )

        assert not UserSession.objects.filter(user=user, revoked_at__isnull=True).exists()
