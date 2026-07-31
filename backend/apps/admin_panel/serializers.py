from rest_framework import serializers

from apps.journals.models import JournalReport

from .models import AdminActionLog, GeneratedReport


class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source="admin_user.email", read_only=True)

    class Meta:
        model = AdminActionLog
        fields = ["id", "admin_user", "admin_email", "action", "target_model", "target_id", "description", "created_at"]
        read_only_fields = fields


class JournalReportModerationSerializer(serializers.ModelSerializer):
    journal_title = serializers.CharField(source="journal_entry.title", read_only=True)
    reported_by_email = serializers.EmailField(source="reported_by.email", read_only=True)

    class Meta:
        model = JournalReport
        fields = [
            "id", "journal_entry", "journal_title", "reported_by", "reported_by_email",
            "reason", "details", "status", "reviewed_by", "review_notes", "reviewed_at", "created_at",
        ]
        read_only_fields = [f for f in fields if f not in ("status", "review_notes")]


class JournalReportResolveSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["reviewed", "actioned", "dismissed"])
    review_notes = serializers.CharField(required=False, allow_blank=True, default="")
    remove_entry = serializers.BooleanField(required=False, default=False)


class GeneratedReportRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=["daily", "weekly", "monthly", "yearly", "mental_health"])
    format = serializers.ChoiceField(choices=["pdf", "csv"])
    period_start = serializers.DateField()
    period_end = serializers.DateField()

    def validate(self, attrs):
        if attrs["period_end"] < attrs["period_start"]:
            raise serializers.ValidationError("period_end must be on or after period_start.")
        return attrs


class GeneratedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedReport
        fields = [
            "id", "report_type", "format", "period_start", "period_end",
            "file", "status", "error_message", "created_at", "completed_at",
        ]
        read_only_fields = fields
