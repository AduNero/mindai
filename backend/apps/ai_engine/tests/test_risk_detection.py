import pytest

from apps.ai_engine.services.risk_detection import detect_crisis_risk
from apps.common.constants import RISK_CRITICAL, RISK_HIGH, RISK_MODERATE


class TestDetectCrisisRisk:
    def test_returns_none_for_benign_text(self):
        assert detect_crisis_risk("Had a great day today, feeling good about things.") is None

    def test_returns_none_for_empty_text(self):
        assert detect_crisis_risk("") is None

    def test_detects_critical_phrase(self):
        result = detect_crisis_risk("I just want to end my life, nothing helps anymore.")
        assert result["risk_level"] == RISK_CRITICAL
        assert "end my life" in result["triggered_phrases"]

    def test_detects_high_phrase(self):
        result = detect_crisis_risk("Sometimes I think about hurting myself when things get bad.")
        assert result["risk_level"] == RISK_HIGH

    def test_detects_moderate_phrase(self):
        result = detect_crisis_risk("I feel so hopeless lately, like nothing matters anymore.")
        assert result["risk_level"] == RISK_MODERATE

    def test_critical_takes_precedence_over_lower_tiers_in_same_text(self):
        result = detect_crisis_risk("I feel hopeless and I want to end my life.")
        assert result["risk_level"] == RISK_CRITICAL

    def test_is_case_insensitive(self):
        result = detect_crisis_risk("I WANT TO END MY LIFE")
        assert result["risk_level"] == RISK_CRITICAL

    @pytest.mark.parametrize(
        "text",
        [
            "I love hiking and being outdoors.",
            "This project deadline is killing me, so much work to do.",  # figurative, shouldn't over-trigger critical tier
        ],
    )
    def test_common_figurative_language_does_not_falsely_trigger_critical(self, text):
        result = detect_crisis_risk(text)
        assert result is None or result["risk_level"] != RISK_CRITICAL
