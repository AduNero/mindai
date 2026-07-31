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


class Visibility(models.TextChoices):
    PRIVATE = "private", "Private"
    PUBLIC = "public", "Public"


class JournalEntry(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    title = models.CharField(max_length=255)
    body = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="journal_entries")
    entry_date = models.DateField(db_index=True)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)

    # Set by the AI risk-detection pipeline (see apps.ai_engine) when
    # crisis-indicating language is found; surfaced to admins as a risk alert.
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


class JournalReportReason(models.TextChoices):
    SELF_HARM = "self_harm", "Self-harm / crisis content"
    HARASSMENT = "harassment", "Harassment or abuse"
    SPAM = "spam", "Spam"
    INAPPROPRIATE = "inappropriate", "Inappropriate content"
    OTHER = "other", "Other"


class JournalReportStatus(models.TextChoices):
    PENDING = "pending", "Pending review"
    REVIEWED = "reviewed", "Reviewed"
    ACTIONED = "actioned", "Actioned"
    DISMISSED = "dismissed", "Dismissed"


class JournalReport(BaseModel):
    """
    A moderation flag on a journal entry — either raised automatically by
    the AI risk-detection pipeline (`reported_by=None`) or manually by a
    user on a public entry.
    """

    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="journal_reports_filed",
    )
    reason = models.CharField(max_length=20, choices=JournalReportReason.choices)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=JournalReportStatus.choices, default=JournalReportStatus.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="journal_reports_reviewed",
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "journal_reports"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"Report<{self.journal_entry_id}> - {self.reason}"
