import uuid
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.constants import THEME_CHOICES
from apps.common.models import BaseModel, TimeStampedModel, UUIDPrimaryKeyModel


class Role(models.TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Administrator"


class UserManager(BaseUserManager):
    """Manager for the custom, email-based User model."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.USER)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Custom user model, authenticated by email rather than username.

    Pseudonymous by design: `email` is only ever used to log in and for
    account recovery (password reset, verification codes) — it is never
    shown anywhere as the user's identity. `pseudonym` is what's actually
    displayed everywhere a name would otherwise appear.

    `role` drives coarse-grained access (User / Administrator);
    fine-grained permissions still use Django's built-in permission system
    where useful (e.g. Django admin site access via `is_staff`).
    """

    email = models.EmailField(unique=True, db_index=True)
    pseudonym = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # Required before account creation completes — see RegisterSerializer.
    age_confirmed_at = models.DateTimeField(null=True, blank=True)
    consent_accepted_at = models.DateTimeField(null=True, blank=True)

    # Security / audit fields
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["pseudonym"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.pseudonym} ({self.get_role_display()})"

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())


def profile_picture_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile_pictures/{instance.user_id}/{uuid.uuid4().hex}.{ext}"


class Profile(BaseModel):
    """
    Extended, non-authentication profile data — one-to-one with User.

    Deliberately minimal: no date of birth, gender, phone number, or
    emergency contact — those are identifying data inconsistent with a
    pseudonymous account (age is a one-time attestation on User, not a
    stored birthdate; see User.age_confirmed_at).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to=profile_picture_path, null=True, blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default="system")

    class Meta:
        db_table = "profiles"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile<{self.user.pseudonym}>"


class EmailVerificationToken(BaseModel):
    """
    Holds a one-time 6-digit OTP code (in `token`), not a link token — the
    field name is kept for migration continuity. Codes are scoped to
    (user, code) rather than globally unique, since a 6-digit space makes
    global uniqueness both unnecessary and, at scale, collision-prone.
    """

    MAX_ATTEMPTS = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token = models.CharField(max_length=6, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "email_verification_tokens"

    def is_valid(self):
        return self.used_at is None and self.attempts < self.MAX_ATTEMPTS and self.expires_at > timezone.now()

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(minutes=15)


class PasswordResetToken(BaseModel):
    """Holds a one-time 6-digit OTP code (in `token`) — see EmailVerificationToken for the naming note."""

    MAX_ATTEMPTS = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=6, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "password_reset_tokens"

    def is_valid(self):
        return self.used_at is None and self.attempts < self.MAX_ATTEMPTS and self.expires_at > timezone.now()

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(minutes=10)


class UserSession(BaseModel):
    """
    Tracks issued refresh-token sessions so users can see active sessions,
    support "Remember Me" (longer-lived session vs. default), and so
    sessions can be individually or globally revoked (logout-all-devices).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh_token_jti = models.CharField(max_length=255, unique=True, db_index=True)
    remember_me = models.BooleanField(default=False)
    device_label = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_sessions"
        indexes = [models.Index(fields=["user", "revoked_at"])]

    def is_active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()
