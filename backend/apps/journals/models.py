from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.constants import MOOD_CHOICES
from apps.common.models import BaseModel


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        db_table = "journal_tags"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JournalEntry(BaseModel):
    """Private by default and only ever private — no public-sharing/moderation surface."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    title = models.CharField(max_length=255)
    body = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="journal_entries")
    entry_date = models.DateField(db_index=True)

    # Set by the deterministic crisis-phrase detector (see apps.ai_engine)
    # when crisis-indicating language is found; surfaced to admins as a
    # risk alert. Never derived from the AI sentiment label.
    is_flagged = models.BooleanField(default=False)

    class Meta:
        db_table = "journal_entries"
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "entry_date"]),
            models.Index(fields=["is_flagged"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.user_id})"
