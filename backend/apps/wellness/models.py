from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class SleepEntry(BaseModel):
    """
    Lightweight sleep log feeding the Wellness Score's sleep component and
    the dashboard's sleep-tracking placeholder widget. Not a full sleep-lab
    style tracker — manual self-report only.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sleep_entries")
    entry_date = models.DateField(db_index=True)
    hours_slept = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
    )
    quality = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Self-reported sleep quality, 1 (poor) to 5 (excellent).",
    )
    notes = models.TextField(max_length=500, blank=True)

    class Meta:
        db_table = "sleep_entries"
        ordering = ["-entry_date"]
        unique_together = ("user", "entry_date")

    def __str__(self):
        return f"{self.user_id} slept {self.hours_slept}h on {self.entry_date}"


class MeditationSession(BaseModel):
    """A completed (or in-progress) guided meditation / breathing exercise session."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meditation_sessions")
    resource = models.ForeignKey(
        "resources.Resource", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="meditation_sessions",
    )
    duration_minutes = models.PositiveSmallIntegerField()
    completed = models.BooleanField(default=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "meditation_sessions"
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["user", "started_at"])]

    def __str__(self):
        return f"{self.user_id} - {self.duration_minutes}min meditation"
