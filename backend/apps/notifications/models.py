from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BaseModel


class NotificationPreference(BaseModel):
    """Per-user opt-in/opt-out + delivery-channel settings for each reminder type."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")

    daily_reminder = models.BooleanField(default=True)
    journal_reminder = models.BooleanField(default=True)
    mood_reminder = models.BooleanField(default=True)
    meditation_reminder = models.BooleanField(default=False)
    assessment_reminder = models.BooleanField(default=True)
    appointment_reminder = models.BooleanField(default=True)

    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    preferred_reminder_time = models.TimeField(default="09:00")

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"NotificationPreference<{self.user_id}>"


class NotificationType(models.TextChoices):
    DAILY_REMINDER = "daily_reminder", "Daily Reminder"
    JOURNAL_REMINDER = "journal_reminder", "Journal Reminder"
    MOOD_REMINDER = "mood_reminder", "Mood Reminder"
    MEDITATION_REMINDER = "meditation_reminder", "Meditation Reminder"
    ASSESSMENT_REMINDER = "assessment_reminder", "Assessment Reminder"
    APPOINTMENT_REMINDER = "appointment_reminder", "Appointment Reminder"
    SYSTEM = "system", "System Message"
    RISK_ALERT = "risk_alert", "Risk Alert"


class NotificationChannel(models.TextChoices):
    IN_APP = "in_app", "In-app"
    EMAIL = "email", "Email"
    BOTH = "both", "In-app + Email"


class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

    # Optional link to the object the notification is about (e.g. a specific Appointment).
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read"])]

    def __str__(self):
        return f"{self.user_id} - {self.title}"
