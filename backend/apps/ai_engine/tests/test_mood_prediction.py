from datetime import date, timedelta

import pytest

from apps.ai_engine.services.mood_prediction import predict_next_mood, save_mood_prediction
from apps.common.constants import MOOD_DEPRESSED, MOOD_HAPPY, MOOD_SAD
from apps.moods.models import MoodEntry

pytestmark = pytest.mark.django_db


def _log_mood(user, mood, days_ago):
    MoodEntry.objects.create(
        user=user, mood=mood, intensity=5, entry_date=date.today() - timedelta(days=days_ago), entry_time="09:00:00"
    )


class TestPredictNextMood:
    def test_returns_none_with_insufficient_data(self, user):
        _log_mood(user, MOOD_HAPPY, 1)
        assert predict_next_mood(user) is None

    def test_returns_none_when_all_entries_on_same_day(self, user):
        for _ in range(3):
            MoodEntry.objects.create(
                user=user, mood=MOOD_HAPPY, intensity=5, entry_date=date.today(), entry_time="09:00:00"
            )
        assert predict_next_mood(user) is None

    def test_extrapolates_declining_trend_toward_lower_mood(self, user):
        _log_mood(user, MOOD_HAPPY, 6)
        _log_mood(user, "neutral", 4)
        _log_mood(user, MOOD_SAD, 2)
        _log_mood(user, MOOD_DEPRESSED, 0)

        prediction = predict_next_mood(user)

        assert prediction is not None
        assert prediction["predicted_mood"] in (MOOD_SAD, MOOD_DEPRESSED)

    def test_extrapolates_improving_trend_toward_higher_mood(self, user):
        _log_mood(user, MOOD_DEPRESSED, 6)
        _log_mood(user, MOOD_SAD, 4)
        _log_mood(user, "neutral", 2)
        _log_mood(user, MOOD_HAPPY, 0)

        prediction = predict_next_mood(user)

        assert prediction is not None
        assert prediction["predicted_mood"] in ("neutral", MOOD_HAPPY, "excited")

    def test_confidence_score_within_valid_range(self, user):
        _log_mood(user, MOOD_HAPPY, 5)
        _log_mood(user, "neutral", 3)
        _log_mood(user, MOOD_SAD, 0)

        prediction = predict_next_mood(user)
        assert 0.0 <= prediction["confidence_score"] <= 1.0


class TestSaveMoodPrediction:
    def test_creates_prediction_row_for_tomorrow(self, user):
        _log_mood(user, MOOD_HAPPY, 5)
        _log_mood(user, "neutral", 3)
        _log_mood(user, MOOD_SAD, 0)

        prediction = save_mood_prediction(user)

        assert prediction is not None
        assert prediction.predicted_for_date == date.today() + timedelta(days=1)

    def test_returns_none_and_creates_nothing_with_insufficient_data(self, user):
        from apps.ai_engine.models import MoodPrediction

        _log_mood(user, MOOD_HAPPY, 0)
        result = save_mood_prediction(user)

        assert result is None
        assert not MoodPrediction.objects.exists()
