from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class AssessmentCode(models.TextChoices):
    PHQ9 = "phq9", "PHQ-9 (Depression)"
    GAD7 = "gad7", "GAD-7 (Anxiety)"
    STRESS = "stress", "Perceived Stress Scale"
    BURNOUT = "burnout", "Burnout Assessment"
    SELF_ESTEEM = "self_esteem", "Rosenberg Self-Esteem Scale"


class AssessmentType(BaseModel):
    """
    Definition of a standardized assessment instrument. Seeded via a data
    migration/fixture in Phase 3 with the real PHQ-9 / GAD-7 / etc. item
    text and validated severity cut-offs — this table just models the shape.
    """

    code = models.CharField(max_length=20, choices=AssessmentCode.choices, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    max_score = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "assessment_types"

    def __str__(self):
        return self.name


class AssessmentQuestion(BaseModel):
    """
    A single item in an assessment. `options` holds the Likert-style
    answer scale as [{"value": 0, "label": "Not at all"}, ...] — standard
    instruments like PHQ-9/GAD-7 share the same 0-3 "Not at all" .. "Nearly
    every day" scale, but this keeps per-question overrides possible.
    """

    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=500)
    options = models.JSONField(
        default=list,
        help_text='e.g. [{"value": 0, "label": "Not at all"}, {"value": 3, "label": "Nearly every day"}]',
    )

    class Meta:
        db_table = "assessment_questions"
        ordering = ["assessment_type", "order"]
        unique_together = ("assessment_type", "order")

    def __str__(self):
        return f"{self.assessment_type.code} Q{self.order}"


class Severity(models.TextChoices):
    MINIMAL = "minimal", "Minimal"
    MILD = "mild", "Mild"
    MODERATE = "moderate", "Moderate"
    MODERATELY_SEVERE = "moderately_severe", "Moderately Severe"
    SEVERE = "severe", "Severe"


class AssessmentResult(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessment_results")
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.PROTECT, related_name="results")
    total_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    severity = models.CharField(max_length=20, choices=Severity.choices)
    interpretation = models.TextField(
        help_text="Human-readable, non-diagnostic interpretation text shown to the user."
    )
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assessment_results"
        ordering = ["-taken_at"]
        indexes = [models.Index(fields=["user", "assessment_type", "taken_at"])]

    def __str__(self):
        return f"{self.user_id} - {self.assessment_type.code}: {self.total_score}"


class AssessmentAnswer(BaseModel):
    result = models.ForeignKey(AssessmentResult, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.PROTECT, related_name="answers")
    selected_value = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "assessment_answers"
        unique_together = ("result", "question")

    def __str__(self):
        return f"{self.result_id} - Q{self.question.order}: {self.selected_value}"
