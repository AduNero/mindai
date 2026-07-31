from unittest.mock import MagicMock, patch

from apps.ai_engine.services import emotion


class TestAnalyzeEmotion:
    def test_empty_text_returns_no_dominant_emotion(self):
        result = emotion.analyze_emotion("")
        assert result["dominant_emotion"] is None
        assert result["scores"] == {}

    def test_filters_to_tracked_labels_and_renormalizes(self):
        """GoEmotions returns 28 labels; only our 8 tracked ones should survive, renormalized to sum to 1."""

        fake_output = [
            [
                {"label": "optimism", "score": 0.42},
                {"label": "joy", "score": 0.25},
                {"label": "neutral", "score": 0.15},  # not tracked — should be dropped
                {"label": "approval", "score": 0.08},  # not tracked
                {"label": "sadness", "score": 0.03},
            ]
        ]
        mock_classifier = MagicMock(return_value=fake_output)

        with patch("apps.ai_engine.services.emotion.get_emotion_pipeline", return_value=mock_classifier):
            result = emotion.analyze_emotion("Things are looking up.")

        assert result["dominant_emotion"] == "optimism"
        assert set(result["scores"].keys()) == {"optimism", "joy", "sadness"}
        assert abs(sum(result["scores"].values()) - 1.0) < 0.001

    def test_no_tracked_labels_present_returns_none_dominant(self):
        fake_output = [[{"label": "neutral", "score": 0.9}, {"label": "approval", "score": 0.1}]]
        mock_classifier = MagicMock(return_value=fake_output)

        with patch("apps.ai_engine.services.emotion.get_emotion_pipeline", return_value=mock_classifier):
            result = emotion.analyze_emotion("Sounds fine I guess.")

        assert result["dominant_emotion"] is None
