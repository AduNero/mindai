from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.constants import (
    DETECTION_SOURCE_CHOICES,
    EMOTION_CHOICES,
    MOOD_CHOICES,
    RISK_LEVEL_CHOICES,
    SENTIMENT_CHOICES,
)
from apps.common.models import BaseModel

# Analyzable content is either a JournalEntry (apps.journals) or a
# ChatMessage (apps.chat). A GenericForeignKey lets SentimentResult /
# EmotionResult attach to either without the ai_engine app importing them
# directly, and leaves room for future analyzable content types.
_SCORE_VALIDATORS = [MinValueValidator(0.0), MaxValueValidator(1.0)]


class SentimentResult(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    confidence_score = models.FloatField(validators=_SCORE_VALIDATORS)

    # 0.0-1.0 indicator scores derived from the analyzed text.
    stress_score = models.FloatField(validators=_SCORE_VALIDATORS, default=0)
    anxiety_score = models.FloatField(validators=_SCORE_VALIDATORS, default=0)
    burnout_score = models.FloatField(validators=_SCORE_VALIDATORS, default=0)
    depression_indicator_score = models.FloatField(validators=_SCORE_VALIDATORS, default=0)

    keywords = models.JSONField(default=list, help_text="Salient keywords/phrases extracted from the text.")
    model_version = models.CharField(max_length=100, help_text="Hugging Face model id + version used.")
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sentiment_results"
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"Sentiment<{self.content_type}:{self.object_id}> = {self.sentiment}"


class EmotionResult(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    dominant_emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    scores = models.JSONField(
        default=dict, help_text='Full distribution, e.g. {"joy": 0.72, "sadness": 0.05, ...}'
    )
    model_version = models.CharField(max_length=100)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "emotion_results"
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"Emotion<{self.content_type}:{self.object_id}> = {self.dominant_emotion}"


class RiskAssessment(BaseModel):
    """
    Output of the crisis/emergency-language detection pipeline. Distinct
    from SentimentResult/EmotionResult because it drives a specific,
    non-diagnostic safety workflow (see docs/architecture/emergency-detection.md)
    rather than general analytics.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_assessments")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    detection_source = models.CharField(max_length=20, choices=DETECTION_SOURCE_CHOICES)
    triggered_phrases = models.JSONField(default=list, blank=True)
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


class WellnessScoreSnapshot(BaseModel):
    """
    One computed Wellness Score per user per day (0-100), decomposed into
    its contributing components so the dashboard can show why the score
    moved, not just the number.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wellness_snapshots")
    score_date = models.DateField(db_index=True)
    overall_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])

    mood_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)
    journal_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)
    assessment_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)
    sleep_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)
    activity_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)
    chat_sentiment_component = models.FloatField(validators=[MaxValueValidator(100)], default=0)

    class Meta:
        db_table = "wellness_score_snapshots"
        ordering = ["-score_date"]
        unique_together = ("user", "score_date")

    def __str__(self):
        return f"{self.user_id} - {self.score_date}: {self.overall_score}"


class MoodPrediction(BaseModel):
    """Forward-looking mood forecast for the dashboard's "Anxiety Trend" / trend-prediction widgets."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mood_predictions")
    predicted_for_date = models.DateField()
    predicted_mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    confidence_score = models.FloatField(validators=_SCORE_VALIDATORS)
    based_on_window_days = models.PositiveSmallIntegerField(default=14)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mood_predictions"
        ordering = ["-predicted_for_date"]
        indexes = [models.Index(fields=["user", "predicted_for_date"])]

    def __str__(self):
        return f"{self.user_id} predicted {self.predicted_mood} for {self.predicted_for_date}"
