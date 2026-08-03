import secrets

from apps.users.models import EmailVerificationToken, PasswordResetToken


def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def issue_email_verification_token(user):
    EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).delete()
    return EmailVerificationToken.objects.create(
        user=user,
        token=_generate_otp(),
        expires_at=EmailVerificationToken.default_expiry(),
    )


def issue_password_reset_token(user, requested_ip=None):
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True).delete()
    return PasswordResetToken.objects.create(
        user=user,
        token=_generate_otp(),
        expires_at=PasswordResetToken.default_expiry(),
        requested_ip=requested_ip,
    )
