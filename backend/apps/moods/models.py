from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.constants import MOOD_CHOICES
from apps.common.models import BaseModel


class MoodEntry(BaseModel):
    """A single mood check-in. Users may log more than one per day."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mood_entries")
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    intensity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Self-reported intensity of the mood, 1 (mild) to 10 (extreme).",
    )
    entry_date = models.DateField(db_index=True)
    entry_time = models.TimeField()
    notes = models.TextField(max_length=1000, blank=True)

    class Meta:
        db_table = "mood_entries"
        verbose_name = "Mood Entry"
        verbose_name_plural = "Mood Entries"
        ordering = ["-entry_date", "-entry_time"]
        indexes = [
            models.Index(fields=["user", "entry_date"]),
            models.Index(fields=["user", "mood"]),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.mood} ({self.intensity}/10) on {self.entry_date}"
