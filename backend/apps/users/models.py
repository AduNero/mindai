import uuid
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.common.constants import GENDER_CHOICES, THEME_CHOICES
from apps.common.models import BaseModel, TimeStampedModel, UUIDPrimaryKeyModel


class Role(models.TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Administrator"
    COUNSELOR = "counselor", "Counselor"


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

    `role` drives coarse-grained access (User / Administrator / Counselor);
    fine-grained permissions still use Django's built-in permission system
    where useful (e.g. Django admin site access via `is_staff`).
    """

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # Security / audit fields
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())


def profile_picture_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile_pictures/{instance.user_id}/{uuid.uuid4().hex}.{ext}"


class Profile(BaseModel):
    """Extended, non-authentication profile data — one-to-one with User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to=profile_picture_path, null=True, blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)

    phone_regex = RegexValidator(regex=r"^\+?[1-9]\d{6,14}$", message="Enter a valid phone number.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # ISO 3166-1 alpha-2 country code — drives localized emergency/crisis resources.
    country_code = models.CharField(max_length=2, blank=True, db_index=True)
    timezone = models.CharField(max_length=50, default="UTC")

    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)

    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default="system")

    class Meta:
        db_table = "profiles"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile<{self.user.email}>"


class CounselorProfile(BaseModel):
    """Additional fields for users with role=COUNSELOR, managed by admins."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="counselor_profile",
        limit_choices_to={"role": Role.COUNSELOR},
    )
    specialization = models.CharField(max_length=255, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(max_length=2000, blank=True)
    is_accepting_appointments = models.BooleanField(default=True)
    approved_by_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "counselor_profiles"
        verbose_name = "Counselor Profile"
        verbose_name_plural = "Counselor Profiles"

    def __str__(self):
        return f"Counselor<{self.user.email}>"


class EmailVerificationToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "email_verification_tokens"

    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(hours=24)


class PasswordResetToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "password_reset_tokens"

    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(hours=1)


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
