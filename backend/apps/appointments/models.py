from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending Approval"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    RESCHEDULED = "rescheduled", "Rescheduled"
    COMPLETED = "completed", "Completed"


class Appointment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    counselor = models.ForeignKey(
        "users.CounselorProfile", on_delete=models.PROTECT, related_name="appointments"
    )
    scheduled_at = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveSmallIntegerField(default=45)
    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING)

    reason_for_visit = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Counselor/admin-facing notes.")

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="appointments_cancelled",
    )
    cancellation_reason = models.TextField(blank=True)

    # Rescheduling creates a new Appointment row and links back to the original,
    # preserving history rather than mutating scheduled_at in place.
    rescheduled_from = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="rescheduled_to"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="appointments_approved",
    )

    class Meta:
        db_table = "appointments"
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["counselor", "scheduled_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} with {self.counselor_id} at {self.scheduled_at} ({self.status})"
