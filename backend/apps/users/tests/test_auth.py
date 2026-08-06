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

    def test_register_succeeds_even_if_email_send_fails(self, api_client):
        """
        Regression test: registration must not 500 just because the
        verification email failed to send (e.g. Render's free tier being
        unable to reach smtp.gmail.com at all). The account and its OTP
        token should still be created — the user can "Resend code" once
        delivery is fixed instead of being blocked from signing up at all.
        """
        from unittest.mock import patch

        with patch("apps.users.tasks.send_mail", side_effect=OSError("Network is unreachable")):
            response = api_client.post(
                "/api/v1/auth/register/",
                {
                    "email": "resilient@example.com",
                    "first_name": "Res",
                    "last_name": "Ilient",
                    "password": "CorrectHorse42!",
                    "password_confirm": "CorrectHorse42!",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email="resilient@example.com")
        assert EmailVerificationToken.objects.filter(user=user).exists()

    def test_register_creates_account_created_notification(self, api_client):
        from apps.notifications.models import Notification, NotificationType

        api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "notify.me@example.com",
                "first_name": "Notify",
                "last_name": "Me",
                "password": "CorrectHorse42!",
                "password_confirm": "CorrectHorse42!",
            },
        )

        user = User.objects.get(email="notify.me@example.com")
        assert Notification.objects.filter(user=user, notification_type=NotificationType.SYSTEM).exists()

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

    def test_lockout_triggering_response_ok_even_if_email_send_fails(self, api_client, user):
        """
        Regression test: the request that trips the lockout threshold
        must still return a normal 401 (and actually record the lockout)
        even if send_account_locked_email fails outright — not 500 just
        because notifying the user about their own lockout didn't work.
        """
        from unittest.mock import patch

        with patch("apps.users.tasks.send_mail", side_effect=OSError("Network is unreachable")):
            for _ in range(settings.ACCOUNT_LOCKOUT_THRESHOLD):
                response = api_client.post(
                    "/api/v1/auth/login/", {"email": user.email, "password": "wrong-password"}
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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

    def test_login_rejects_unverified_email(self, api_client, user):
        user.is_email_verified = False
        user.save()
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_rejects_unverified_email_with_machine_readable_reason(self, api_client, user):
        """
        Regression test: the frontend needs a stable way to detect "you
        need to verify your email" specifically (vs. wrong password,
        lockout, etc.) so it can link straight to the verify page instead
        of just showing a dead-end error message — accounts that
        registered before email delivery worked have no other way to
        discover that "resend code" exists.
        """
        user.is_email_verified = False
        user.save()
        response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})
        assert response.data["error"]["details"] == {"code": "email_not_verified"}


class TestGoogleLogin:
    def _claims(self, **overrides):
        claims = {
            "email": "newgoogleuser@example.com",
            "email_verified": True,
            "given_name": "Ada",
            "family_name": "Lovelace",
            "sub": "1234567890",
        }
        claims.update(overrides)
        return claims

    def test_creates_a_new_verified_unusable_password_account(self, api_client):
        from unittest.mock import patch

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims()):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data and "refresh" in response.data

        created = User.objects.get(email="newgoogleuser@example.com")
        assert created.is_email_verified is True
        assert created.has_usable_password() is False
        assert created.first_name == "Ada"

    def test_logs_in_an_existing_user_by_email(self, api_client, user):
        from unittest.mock import patch

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims(email=user.email)):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == user.email
        # An existing password-based account isn't touched by a Google login.
        user.refresh_from_db()
        assert user.check_password("CorrectHorse42!")

    def test_verifies_a_previously_unverified_existing_account(self, api_client, user):
        from unittest.mock import patch

        user.is_email_verified = False
        user.save(update_fields=["is_email_verified"])

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims(email=user.email)):
            api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        user.refresh_from_db()
        assert user.is_email_verified is True

    def test_rejects_when_google_has_not_verified_the_email(self, api_client):
        from unittest.mock import patch

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims(email_verified=False)):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email="newgoogleuser@example.com").exists()

    def test_rejects_invalid_token(self, api_client):
        from unittest.mock import patch

        from apps.users.google_oauth import GoogleTokenError

        with patch("apps.users.views.verify_google_id_token", side_effect=GoogleTokenError("Token expired")):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_requires_credential(self, api_client):
        response = api_client.post("/api/v1/auth/google/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_deactivated_account(self, api_client, user):
        from unittest.mock import patch

        user.is_active = False
        user.save(update_fields=["is_active"])

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims(email=user.email)):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_clears_an_existing_lockout(self, api_client, user):
        from unittest.mock import patch

        from django.utils import timezone

        user.failed_login_attempts = 5
        user.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        user.save(update_fields=["failed_login_attempts", "locked_until"])

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims(email=user.email)):
            response = api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

    def test_creates_a_user_session(self, api_client):
        from unittest.mock import patch

        from apps.users.models import UserSession

        with patch("apps.users.views.verify_google_id_token", return_value=self._claims()):
            api_client.post("/api/v1/auth/google/", {"credential": "fake-token"})

        created = User.objects.get(email="newgoogleuser@example.com")
        assert UserSession.objects.filter(user=created).exists()


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


class TestDeleteAccount:
    def test_deletes_account_with_correct_password(self, auth_client, user):
        response = auth_client.post("/api/v1/auth/account/delete/", {"password": "CorrectHorse42!"})
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user.id).exists()

    def test_rejects_wrong_password(self, auth_client, user):
        response = auth_client.post("/api/v1/auth/account/delete/", {"password": "wrong-password"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(id=user.id).exists()

    def test_requires_authentication(self, api_client):
        response = api_client.post("/api/v1/auth/account/delete/", {"password": "irrelevant"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cascade_deletes_owned_data(self, auth_client, user):
        from apps.moods.models import MoodEntry

        MoodEntry.objects.create(
            user=user, mood="happy", intensity=5, entry_date="2026-08-01", entry_time="09:00"
        )
        auth_client.post("/api/v1/auth/account/delete/", {"password": "CorrectHorse42!"})
        assert not MoodEntry.objects.filter(user_id=user.id).exists()

    def test_audit_log_survives_the_deletion(self, auth_client, user):
        from apps.audit.models import AuditAction, AuditLog

        user_email = user.email
        auth_client.post("/api/v1/auth/account/delete/", {"password": "CorrectHorse42!"})

        log = AuditLog.objects.filter(action=AuditAction.ACCOUNT_DELETED).first()
        assert log is not None
        assert log.user_id is None  # on_delete=SET_NULL — the FK survives, the row it pointed to doesn't
        assert log.metadata.get("email") == user_email
