import pytest

from apps.assessments.models import AssessmentCode, Severity
from apps.assessments.scoring import score_assessment


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, Severity.MINIMAL),
        (4, Severity.MINIMAL),
        (5, Severity.MILD),
        (9, Severity.MILD),
        (10, Severity.MODERATE),
        (14, Severity.MODERATE),
        (15, Severity.MODERATELY_SEVERE),
        (19, Severity.MODERATELY_SEVERE),
        (20, Severity.SEVERE),
        (27, Severity.SEVERE),
    ],
)
def test_phq9_severity_bands(score, expected):
    severity, _ = score_assessment(AssessmentCode.PHQ9, score, max_score=27)
    assert severity == expected


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, Severity.MINIMAL),
        (4, Severity.MINIMAL),
        (5, Severity.MILD),
        (9, Severity.MILD),
        (10, Severity.MODERATE),
        (14, Severity.MODERATE),
        (15, Severity.SEVERE),
        (21, Severity.SEVERE),
    ],
)
def test_gad7_severity_bands(score, expected):
    severity, _ = score_assessment(AssessmentCode.GAD7, score, max_score=21)
    assert severity == expected


def test_self_esteem_inverts_ratio_so_low_score_is_high_concern():
    """Unlike PHQ-9/GAD-7, a *low* raw score means *more* concern for self-esteem."""
    low_score_severity, _ = score_assessment(AssessmentCode.SELF_ESTEEM, 2, max_score=30)
    high_score_severity, _ = score_assessment(AssessmentCode.SELF_ESTEEM, 28, max_score=30)

    severity_order = [Severity.MINIMAL, Severity.MILD, Severity.MODERATE, Severity.MODERATELY_SEVERE, Severity.SEVERE]
    assert severity_order.index(low_score_severity) > severity_order.index(high_score_severity)


def test_generic_severity_scales_with_ratio_for_stress():
    low, _ = score_assessment(AssessmentCode.STRESS, 2, max_score=40)
    high, _ = score_assessment(AssessmentCode.STRESS, 38, max_score=40)

    severity_order = [Severity.MINIMAL, Severity.MILD, Severity.MODERATE, Severity.MODERATELY_SEVERE, Severity.SEVERE]
    assert severity_order.index(high) > severity_order.index(low)


def test_severe_and_moderately_severe_interpretations_include_crisis_language():
    _, interpretation = score_assessment(AssessmentCode.PHQ9, 25, max_score=27)
    assert "crisis" in interpretation.lower() or "emergency" in interpretation.lower()


def test_minimal_interpretation_has_no_crisis_language():
    _, interpretation = score_assessment(AssessmentCode.PHQ9, 2, max_score=27)
    assert "emergency services" not in interpretation.lower()
