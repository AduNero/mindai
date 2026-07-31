"""
Keyword/phrase-based crisis detection for journal entries and chat messages.

This is intentionally a transparent, auditable phrase list rather than a
learned classifier: for a safety-critical signal like this, explainability
(admins can see exactly which phrase triggered a flag) and predictable
behavior matter more than the marginal recall a black-box model might add.
A production deployment would pair this with clinical/professional review —
see docs/architecture/emergency-detection.md.

False negatives are expected (this only catches phrasing close to the list
below); it is a supplementary safety net, not the platform's only line of
defense — assessment-based checks (e.g. PHQ-9 item 9, see
apps.assessments.views) run independently of this module.
"""

import re

from apps.common.constants import RISK_CRITICAL, RISK_HIGH, RISK_MODERATE

# Ordered from most to least severe; the first tier whose phrases match wins.
_CRITICAL_PHRASES = [
    "kill myself", "end my life", "suicide plan", "want to die", "going to kill myself",
    "better off dead", "take my own life", "ending it all", "no reason to live",
]

_HIGH_PHRASES = [
    "suicidal", "self harm", "self-harm", "hurt myself", "hurting myself",
    "cutting myself", "don't want to be here", "dont want to be here",
    "can't go on", "cant go on", "want to disappear",
]

_MODERATE_PHRASES = [
    "hopeless", "no point in anything", "nothing matters anymore",
    "giving up", "can't take it anymore", "cant take it anymore",
    "everyone would be better without me",
]

_TIERS = [
    (RISK_CRITICAL, _CRITICAL_PHRASES),
    (RISK_HIGH, _HIGH_PHRASES),
    (RISK_MODERATE, _MODERATE_PHRASES),
]


def detect_crisis_risk(text: str) -> dict | None:
    """
    Scans `text` for crisis-indicating phrases. Returns
    {"risk_level": ..., "triggered_phrases": [...], "confidence_score": ...}
    for the highest-severity tier matched, or None if nothing matched.
    """

    if not text:
        return None

    text_lower = text.lower()
    text_lower = re.sub(r"\s+", " ", text_lower)

    for risk_level, phrases in _TIERS:
        matched = [p for p in phrases if p in text_lower]
        if matched:
            return {
                "risk_level": risk_level,
                "triggered_phrases": matched,
                # Phrase matching is binary (found/not found), so confidence
                # reflects match specificity, not statistical certainty.
                "confidence_score": 1.0,
            }

    return None
