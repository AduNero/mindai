from django.utils import timezone
from rest_framework import serializers

from apps.users.models import CounselorProfile
from apps.users.serializers import CounselorProfileSerializer

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    counselor = CounselorProfileSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "counselor", "scheduled_at", "duration_minutes", "status",
            "reason_for_visit", "cancellation_reason", "rescheduled_from", "created_at",
        ]
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.ModelSerializer):
    counselor_id = serializers.PrimaryKeyRelatedField(
        source="counselor", queryset=CounselorProfile.objects.filter(is_accepting_appointments=True, approved_by_admin=True)
    )

    class Meta:
        model = Appointment
        fields = ["counselor_id", "scheduled_at", "duration_minutes", "reason_for_visit"]

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment time must be in the future.")
        return value

    def validate(self, attrs):
        counselor = attrs["counselor"]
        scheduled_at = attrs["scheduled_at"]
        duration = attrs.get("duration_minutes", 45)
        new_start, new_end = scheduled_at, scheduled_at + timezone.timedelta(minutes=duration)

        active = Appointment.objects.filter(
            counselor=counselor,
            status__in=["pending", "approved"],
            scheduled_at__date=scheduled_at.date(),
        )
        for existing in active:
            existing_start = existing.scheduled_at
            existing_end = existing_start + timezone.timedelta(minutes=existing.duration_minutes)
            if existing_start < new_end and existing_end > new_start:
                raise serializers.ValidationError("This counselor already has an appointment at that time.")

        return attrs


class AppointmentCancelSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(required=False, allow_blank=True, default="")


class AppointmentRescheduleSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment time must be in the future.")
        return value


class AdminAppointmentSerializer(AppointmentSerializer):
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ["notes", "approved_by"]
        read_only_fields = fields


class AdminAppointmentDecisionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="")
