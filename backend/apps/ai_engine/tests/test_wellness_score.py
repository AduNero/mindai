from datetime import date

import pytest

from apps.ai_engine.services.wellness_score import NEUTRAL_BASELINE, compute_wellness_score, save_wellness_score
from apps.moods.models import MoodEntry
from apps.wellness.models import SleepEntry

pytestmark = pytest.mark.django_db


class TestComputeWellnessScore:
    def test_all_components_default_to_neutral_baseline_with_no_data(self, user):
        result = compute_wellness_score(user, date.today())
        assert result["overall_score"] == int(NEUTRAL_BASELINE)
        for key in ("mood_component", "journal_component", "assessment_component", "sleep_component", "activity_component", "chat_sentiment_component"):
            assert result[key] == NEUTRAL_BASELINE

    def test_high_intensity_bad_mood_lowers_mood_component_below_baseline(self, user):
        MoodEntry.objects.create(
            user=user, mood="depressed", intensity=9, entry_date=date.today(), entry_time="09:00:00"
        )
        result = compute_wellness_score(user, date.today())
        assert result["mood_component"] < NEUTRAL_BASELINE

    def test_high_intensity_good_mood_raises_mood_component_above_baseline(self, user):
        MoodEntry.objects.create(
            user=user, mood="excited", intensity=9, entry_date=date.today(), entry_time="09:00:00"
        )
        result = compute_wellness_score(user, date.today())
        assert result["mood_component"] > NEUTRAL_BASELINE

    def test_ideal_sleep_scores_higher_than_poor_sleep(self, user, other_user):
        SleepEntry.objects.create(user=user, entry_date=date.today(), hours_slept=8, quality=5)
        SleepEntry.objects.create(user=other_user, entry_date=date.today(), hours_slept=3, quality=1)

        good_sleep = compute_wellness_score(user, date.today())
        poor_sleep = compute_wellness_score(other_user, date.today())

        assert good_sleep["sleep_component"] > poor_sleep["sleep_component"]

    def test_overall_score_is_average_of_components(self, user):
        MoodEntry.objects.create(user=user, mood="happy", intensity=5, entry_date=date.today(), entry_time="09:00:00")
        result = compute_wellness_score(user, date.today())
        components = [
            result["mood_component"],
            result["journal_component"],
            result["assessment_component"],
            result["sleep_component"],
            result["activity_component"],
            result["chat_sentiment_component"],
        ]
        assert result["overall_score"] == round(sum(components) / len(components))

    def test_overall_score_bounded_0_to_100(self, user):
        MoodEntry.objects.create(user=user, mood="excited", intensity=10, entry_date=date.today(), entry_time="09:00:00")
        result = compute_wellness_score(user, date.today())
        assert 0 <= result["overall_score"] <= 100


class TestSaveWellnessScore:
    def test_creates_snapshot(self, user):
        snapshot = save_wellness_score(user, date.today())
        assert snapshot.pk is not None
        assert snapshot.user == user
        assert snapshot.score_date == date.today()

    def test_is_idempotent_per_day(self, user):
        from apps.ai_engine.models import WellnessScoreSnapshot

        save_wellness_score(user, date.today())
        MoodEntry.objects.create(user=user, mood="happy", intensity=8, entry_date=date.today(), entry_time="10:00:00")
        save_wellness_score(user, date.today())

        assert WellnessScoreSnapshot.objects.filter(user=user, score_date=date.today()).count() == 1
