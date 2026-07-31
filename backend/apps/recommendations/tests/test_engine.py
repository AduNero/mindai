from datetime import date

import pytest

from apps.moods.models import MoodEntry
from apps.recommendations.engine import generate_for_user
from apps.recommendations.models import Recommendation, RecommendationCategory, RecommendationTemplate

pytestmark = pytest.mark.django_db


def _log_mood(user, mood, intensity=5):
    MoodEntry.objects.create(user=user, mood=mood, intensity=intensity, entry_date=date.today(), entry_time="09:00:00")


class TestGenerateForUser:
    def test_matches_template_by_mood(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.BREATHING,
            title="Try breathing",
            description="...",
            trigger_conditions={"mood_in": ["anxious"]},
        )
        _log_mood(user, "anxious")

        created = generate_for_user(user)

        assert len(created) == 1
        assert created[0].title == "Try breathing"

    def test_does_not_match_wrong_mood(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.BREATHING,
            title="Try breathing",
            description="...",
            trigger_conditions={"mood_in": ["anxious"]},
        )
        _log_mood(user, "happy")

        created = generate_for_user(user)

        assert created == []

    def test_min_intensity_condition_respected(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.PHYSICAL_ACTIVITY,
            title="Intense mood template",
            description="...",
            trigger_conditions={"mood_in": ["angry"], "min_intensity": 7},
        )
        _log_mood(user, "angry", intensity=3)
        assert generate_for_user(user) == []

        _log_mood(user, "angry", intensity=8)
        assert len(generate_for_user(user)) == 1

    def test_falls_back_to_unconditioned_templates_when_nothing_matches(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.EDUCATION,
            title="General wellness tip",
            description="...",
            trigger_conditions={},
        )
        _log_mood(user, "happy")  # no conditioned template matches "happy"

        created = generate_for_user(user)
        assert len(created) == 1
        assert created[0].title == "General wellness tip"

    def test_dedupe_window_prevents_immediate_repeat(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.BREATHING,
            title="Try breathing",
            description="...",
            trigger_conditions={"mood_in": ["anxious"]},
        )
        _log_mood(user, "anxious")

        first_run = generate_for_user(user)
        second_run = generate_for_user(user)

        assert len(first_run) == 1
        assert second_run == []

    def test_severity_in_condition_matches_latest_assessment(self, user):
        from apps.assessments.models import AssessmentResult, AssessmentType

        assessment_type = AssessmentType.objects.create(
            code="phq9", name="PHQ-9", description="", instructions="", max_score=27
        )
        AssessmentResult.objects.create(
            user=user, assessment_type=assessment_type, total_score=18, severity="moderately_severe", interpretation=""
        )
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.PROFESSIONAL_HELP,
            title="Talk to someone",
            description="...",
            trigger_conditions={"severity_in": ["moderate", "moderately_severe", "severe"]},
        )

        created = generate_for_user(user, source="assessment")
        assert len(created) == 1
        assert created[0].source == "assessment"

    def test_respects_max_recommendations_per_run(self, user):
        for i in range(5):
            RecommendationTemplate.objects.create(
                category=RecommendationCategory.SELF_CARE,
                title=f"Template {i}",
                description="...",
                trigger_conditions={"mood_in": ["sad"]},
            )
        _log_mood(user, "sad")

        created = generate_for_user(user)
        assert len(created) <= 3

    def test_creates_recommendation_rows_in_db(self, user):
        RecommendationTemplate.objects.create(
            category=RecommendationCategory.BREATHING,
            title="Try breathing",
            description="...",
            trigger_conditions={"mood_in": ["anxious"]},
        )
        _log_mood(user, "anxious")

        generate_for_user(user)
        assert Recommendation.objects.filter(user=user).count() == 1
