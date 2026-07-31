"""
Non-diagnostic scoring for the standardized instruments this platform
offers. Cut-offs for PHQ-9 and GAD-7 follow their published clinical
scoring guidance; Stress/Burnout/Self-esteem use a generic percentage-of-
max-score banding since MindCare's versions of those instruments are
original items (not a licensed proprietary scale), so no official cut-off
table applies.

None of this constitutes a diagnosis — see `interpretation` text and
apps/ai_engine's crisis-detection flow for how elevated results are
surfaced without overstepping into clinical claims.
"""

from .models import AssessmentCode, Severity

PHQ9_CUTOFFS = [
    (5, Severity.MINIMAL),
    (10, Severity.MILD),
    (15, Severity.MODERATE),
    (20, Severity.MODERATELY_SEVERE),
    (28, Severity.SEVERE),
]

GAD7_CUTOFFS = [
    (5, Severity.MINIMAL),
    (10, Severity.MILD),
    (15, Severity.MODERATE),
    (22, Severity.SEVERE),
]

_GENERIC_RATIO_BANDS = [
    (0.20, Severity.MINIMAL),
    (0.40, Severity.MILD),
    (0.60, Severity.MODERATE),
    (0.80, Severity.MODERATELY_SEVERE),
    (1.01, Severity.SEVERE),
]

INTERPRETATIONS = {
    Severity.MINIMAL: "Your responses suggest minimal symptoms right now. Keep up whatever's working for you.",
    Severity.MILD: (
        "Your responses suggest mild symptoms. Consider trying the recommended "
        "wellness activities and keep tracking how you feel."
    ),
    Severity.MODERATE: (
        "Your responses suggest moderate symptoms. Consider speaking with a "
        "counselor and using the recommended coping resources."
    ),
    Severity.MODERATELY_SEVERE: (
        "Your responses suggest moderately severe symptoms. We'd strongly "
        "encourage booking a session with a counselor soon."
    ),
    Severity.SEVERE: (
        "Your responses suggest severe symptoms. Please consider reaching out "
        "to a mental health professional soon."
    ),
}

CRISIS_APPENDIX = (
    " This is not a diagnosis. If you are in crisis or having thoughts of "
    "harming yourself, please see the Emergency Resources page or contact "
    "local emergency services immediately."
)


def _banded_severity(score, cutoffs):
    for threshold, severity in cutoffs:
        if score < threshold:
            return severity
    return cutoffs[-1][1]


def _generic_severity(ratio):
    for cutoff, severity in _GENERIC_RATIO_BANDS:
        if ratio < cutoff:
            return severity
    return Severity.SEVERE


def score_assessment(code, total_score, max_score):
    """Returns (severity, interpretation) for a completed assessment."""

    if code == AssessmentCode.PHQ9:
        severity = _banded_severity(total_score, PHQ9_CUTOFFS)
    elif code == AssessmentCode.GAD7:
        severity = _banded_severity(total_score, GAD7_CUTOFFS)
    elif code == AssessmentCode.SELF_ESTEEM:
        # Higher raw score = healthier self-esteem, so invert before banding
        # (a low ratio here should read as "more concern", like the others).
        ratio = 1 - (total_score / max_score if max_score else 0)
        severity = _generic_severity(ratio)
    else:  # STRESS, BURNOUT
        ratio = total_score / max_score if max_score else 0
        severity = _generic_severity(ratio)

    interpretation = INTERPRETATIONS[severity]
    if severity in (Severity.MODERATELY_SEVERE, Severity.SEVERE):
        interpretation += CRISIS_APPENDIX
    return severity, interpretation
