from unittest.mock import MagicMock, patch

from apps.ai_engine.services import sentiment
from apps.common.constants import SENTIMENT_NEGATIVE, SENTIMENT_NEUTRAL, SENTIMENT_POSITIVE


def _mock_pipeline(label, score):
    return MagicMock(return_value=[{"label": label, "score": score}])


class TestAnalyzeSentiment:
    def test_empty_text_returns_neutral(self):
        result = sentiment.analyze_sentiment("")
        assert result["sentiment"] == SENTIMENT_NEUTRAL
        assert result["confidence_score"] == 0.0

    def test_high_confidence_positive_maps_correctly(self):
        with patch(
            "apps.ai_engine.services.sentiment.get_sentiment_pipeline",
            return_value=_mock_pipeline("POSITIVE", 0.98),
        ):
            result = sentiment.analyze_sentiment("Things are going great!")
        assert result["sentiment"] == SENTIMENT_POSITIVE
        assert result["confidence_score"] == 0.98

    def test_high_confidence_negative_maps_correctly(self):
        with patch(
            "apps.ai_engine.services.sentiment.get_sentiment_pipeline",
            return_value=_mock_pipeline("NEGATIVE", 0.95),
        ):
            result = sentiment.analyze_sentiment("This is terrible.")
        assert result["sentiment"] == SENTIMENT_NEGATIVE

    def test_low_confidence_falls_back_to_neutral(self):
        with patch(
            "apps.ai_engine.services.sentiment.get_sentiment_pipeline",
            return_value=_mock_pipeline("POSITIVE", 0.55),
        ):
            result = sentiment.analyze_sentiment("It was okay I suppose.")
        assert result["sentiment"] == SENTIMENT_NEUTRAL

    def test_includes_lexicon_construct_scores_and_keywords(self):
        with patch(
            "apps.ai_engine.services.sentiment.get_sentiment_pipeline",
            return_value=_mock_pipeline("NEGATIVE", 0.9),
        ):
            result = sentiment.analyze_sentiment("I am so stressed and anxious about deadlines.")

        assert result["stress_score"] > 0
        assert result["anxiety_score"] > 0
        assert "stressed" in result["keywords"] or "anxious" in result["keywords"]
        assert result["model_version"]
