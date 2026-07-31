from rest_framework import serializers

from .models import MeditationSession, SleepEntry


class SleepEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepEntry
        fields = ["id", "entry_date", "hours_slept", "quality", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class MeditationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationSession
        fields = [
            "id", "resource", "duration_minutes", "completed",
            "started_at", "completed_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
