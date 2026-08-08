from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.constants import DETECTION_SOURCE_CHOICES, RISK_LEVEL_CHOICES, SENTIMENT_ACTION_CHOICES, SENTIMENT_CHOICES
from apps.common.models import BaseModel
from apps.journals.models import JournalEntry

_SCORE_VALIDATORS = [MinValueValidator(0.0), MaxValueValidator(1.0)]


class SentimentResult(BaseModel):
    """
    One row per classifier run on a journal entry — history-preserving
    (not overwritten on re-analysis) since accept/reject/correct outcomes
    are themselves evaluation data.
    """

    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="sentiment_results")
    label = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    confidence = models.FloatField(validators=_SCORE_VALIDATORS)
    model_version = models.CharField(max_length=100, help_text="Identifies the trained classifier artifact used.")

    user_action = models.CharField(max_length=10, choices=SENTIMENT_ACTION_CHOICES, default="pending")
    corrected_label = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, blank=True)
    actioned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sentiment_results"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["journal_entry", "created_at"])]

    def __str__(self):
        return f"Sentiment<{self.journal_entry_id}> = {self.label}"


class RiskAssessment(BaseModel):
    """
    Output of the crisis/emergency-language detection pipeline. A
    deterministic, non-diagnostic safety signal — never the raw triggering
    text (only the risk tier is persisted; see
    docs/architecture/emergency-detection.md).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_assessments")
    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, null=True, blank=True, related_name="risk_assessments"
    )

    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    detection_source = models.CharField(max_length=20, choices=DETECTION_SOURCE_CHOICES)
    confidence_score = models.FloatField(validators=_SCORE_VALIDATORS, default=0)

    # Whether the user has been shown/acknowledged crisis resources — the
    # platform never auto-notifies third parties (see spec's Emergency
    # Detection rules); this only tracks the in-app safety-message flow.
    resources_shown_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="risk_assessments_reviewed",
    )
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = "risk_assessments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "risk_level"]),
            models.Index(fields=["risk_level", "created_at"]),
        ]

    def __str__(self):
        return f"Risk<{self.user_id}> = {self.risk_level}"
