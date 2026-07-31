from rest_framework import serializers

from .models import MoodEntry


class MoodEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodEntry
        fields = ["id", "mood", "intensity", "entry_date", "entry_time", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyMoodStatSerializer(serializers.Serializer):
    date = serializers.DateField()
    average_intensity = serializers.FloatField(allow_null=True)
    dominant_mood = serializers.CharField(allow_null=True)
    entry_count = serializers.IntegerField()
