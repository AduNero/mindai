from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "channel", "title", "body",
            "is_read", "read_at", "created_at",
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "daily_reminder", "journal_reminder", "mood_reminder", "meditation_reminder",
            "assessment_reminder", "appointment_reminder", "email_enabled", "in_app_enabled",
            "preferred_reminder_time",
        ]
