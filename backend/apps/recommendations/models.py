from django.conf import settings
from django.db import models

from apps.common.constants import RECOMMENDATION_SOURCE_CHOICES
from apps.common.models import BaseModel


class RecommendationCategory(models.TextChoices):
    PHYSICAL_ACTIVITY = "physical_activity", "Physical Activity"
    MINDFULNESS = "mindfulness", "Mindfulness / Meditation"
    BREATHING = "breathing", "Breathing Exercise"
    SLEEP = "sleep", "Sleep"
    NUTRITION = "nutrition", "Nutrition / Hydration"
    SOCIAL = "social", "Social Connection"
    SELF_CARE = "self_care", "Self-care"
    PROFESSIONAL_HELP = "professional_help", "Professional Help"
    ENTERTAINMENT = "entertainment", "Entertainment / Media"
    EDUCATION = "education", "Wellness Article / Education"


class RecommendationTemplate(BaseModel):
    """
    Admin-managed catalogue of candidate recommendations (spec's "Manage AI
    Resources"). The recommendation engine (Phase 5) selects/ranks from
    these using `trigger_conditions` plus the user's recent mood, journal
    sentiment, assessment scores, and chat sentiment.
    """

    category = models.CharField(max_length=30, choices=RecommendationCategory.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_url = models.URLField(blank=True)
    trigger_conditions = models.JSONField(
        default=dict, blank=True,
        help_text='e.g. {"mood_in": ["sad", "depressed"], "min_stress_score": 0.6}',
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recommendation_templates_created",
    )

    class Meta:
        db_table = "recommendation_templates"

    def __str__(self):
        return self.title


class RecommendationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    DISMISSED = "dismissed", "Dismissed"


class Recommendation(BaseModel):
    """A recommendation instance generated for a specific user at a specific time."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations")
    template = models.ForeignKey(
        RecommendationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="instances"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=RecommendationCategory.choices)
    source = models.CharField(max_length=20, choices=RECOMMENDATION_SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=RecommendationStatus.choices, default=RecommendationStatus.PENDING)
    generated_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "recommendations"
        ordering = ["-generated_at"]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self):
        return f"{self.user_id} - {self.title} ({self.status})"
