"""
Computes the daily Wellness Score (0-100) from six equally-weighted
components. Each component defaults to a neutral baseline (60) when there's
no relevant data for the day, rather than being excluded from the average
or penalized — a user who didn't log sleep isn't "failing" at sleep, they
just gave us no signal.
"""

from datetime import date, timedelta

from apps.common.constants import MOOD_ANGRY, MOOD_ANXIOUS, MOOD_DEPRESSED, MOOD_EXCITED, MOOD_HAPPY, MOOD_NEUTRAL, MOOD_SAD, MOOD_TIRED

NEUTRAL_BASELINE = 60.0

_MOOD_SCORE = {
    MOOD_DEPRESSED: 1,
    MOOD_SAD: 2,
    MOOD_ANGRY: 2,
    MOOD_ANXIOUS: 3,
    MOOD_TIRED: 3,
    MOOD_NEUTRAL: 4,
    MOOD_HAPPY: 5,
    MOOD_EXCITED: 5,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _mood_component(user, target_date: date) -> float:
    entries = list(user.mood_entries.filter(entry_date=target_date))
    if not entries:
        return NEUTRAL_BASELINE

    scores = []
    for entry in entries:
        base = _MOOD_SCORE.get(entry.mood, 3) * 20  # 20-100
        is_low_mood = _MOOD_SCORE.get(entry.mood, 3) <= 3
        direction = -1 if is_low_mood else 1
        adjustment = (entry.intensity - 5) * 4 * direction
        scores.append(_clamp(base + adjustment))
    return sum(scores) / len(scores)


def _journal_component(user, target_date: date) -> float:
    from django.contrib.contenttypes.models import ContentType

    from apps.ai_engine.models import SentimentResult

    entries = list(user.journal_entries.filter(entry_date=target_date))
    if not entries:
        return NEUTRAL_BASELINE

    score = 70.0  # journaling itself is a constructive wellness behavior
    content_type = ContentType.objects.get_for_model(entries[0])
    results = SentimentResult.objects.filter(content_type=content_type, object_id__in=[e.id for e in entries])

    if results.exists():
        avg_stress = sum(r.stress_score for r in results) / results.count()
        avg_anxiety = sum(r.anxiety_score for r in results) / results.count()
        avg_depression = sum(r.depression_indicator_score for r in results) / results.count()
        positive_ratio = sum(1 for r in results if r.sentiment == "positive") / results.count()
        score += positive_ratio * 15
        score -= (avg_stress + avg_anxiety + avg_depression) / 3 * 40

    return _clamp(score)


def _assessment_component(user, target_date: date) -> float:
    from apps.assessments.models import Severity

    severity_scores = {
        Severity.MINIMAL: 100,
        Severity.MILD: 75,
        Severity.MODERATE: 50,
        Severity.MODERATELY_SEVERE: 25,
        Severity.SEVERE: 10,
    }
    window_start = target_date - timedelta(days=30)
    recent = (
        user.assessment_results.filter(taken_at__date__gte=window_start, taken_at__date__lte=target_date)
        .order_by("-taken_at")
    )
    if not recent.exists():
        return NEUTRAL_BASELINE

    scores = [severity_scores.get(r.severity, 50) for r in recent]
    return sum(scores) / len(scores)


def _sleep_component(user, target_date: date) -> float:
    window_start = target_date - timedelta(days=3)
    entries = list(user.sleep_entries.filter(entry_date__gte=window_start, entry_date__lte=target_date))
    if not entries:
        return NEUTRAL_BASELINE

    scores = []
    for entry in entries:
        hours = float(entry.hours_slept)
        # Ideal range ~7-9h; score falls off outside it.
        if 7 <= hours <= 9:
            duration_score = 100
        else:
            duration_score = _clamp(100 - abs(hours - 8) * 15)
        quality_score = entry.quality * 20  # 1-5 -> 20-100
        scores.append((duration_score + quality_score) / 2)
    return sum(scores) / len(scores)


def _activity_component(user, target_date: date) -> float:
    window_start = target_date - timedelta(days=6)
    sessions = user.meditation_sessions.filter(started_at__date__gte=window_start, started_at__date__lte=target_date)
    if not sessions.exists():
        return NEUTRAL_BASELINE

    total_minutes = sum(s.duration_minutes for s in sessions)
    # 60+ minutes of mindfulness practice in a week maxes this component out.
    return _clamp(NEUTRAL_BASELINE + (total_minutes / 60) * 40)


def _chat_sentiment_component(user, target_date: date) -> float:
    from django.contrib.contenttypes.models import ContentType

    from apps.ai_engine.models import SentimentResult
    from apps.chat.models import ChatMessage, MessageSender

    message_ids = list(
        ChatMessage.objects.filter(
            session__user=user, sender=MessageSender.USER, created_at__date=target_date
        ).values_list("id", flat=True)
    )
    if not message_ids:
        return NEUTRAL_BASELINE

    content_type = ContentType.objects.get_for_model(ChatMessage)
    results = SentimentResult.objects.filter(content_type=content_type, object_id__in=message_ids)
    if not results.exists():
        return NEUTRAL_BASELINE

    positive_ratio = sum(1 for r in results if r.sentiment == "positive") / results.count()
    negative_ratio = sum(1 for r in results if r.sentiment == "negative") / results.count()
    return _clamp(NEUTRAL_BASELINE + positive_ratio * 40 - negative_ratio * 40)


def compute_wellness_score(user, target_date: date | None = None) -> dict:
    """Returns the six component scores plus the overall (equally-weighted average) score."""

    target_date = target_date or date.today()

    components = {
        "mood_component": _mood_component(user, target_date),
        "journal_component": _journal_component(user, target_date),
        "assessment_component": _assessment_component(user, target_date),
        "sleep_component": _sleep_component(user, target_date),
        "activity_component": _activity_component(user, target_date),
        "chat_sentiment_component": _chat_sentiment_component(user, target_date),
    }
    overall = round(sum(components.values()) / len(components))

    return {"overall_score": overall, **components}


def save_wellness_score(user, target_date: date | None = None):
    from apps.ai_engine.models import WellnessScoreSnapshot

    target_date = target_date or date.today()
    data = compute_wellness_score(user, target_date)

    snapshot, _ = WellnessScoreSnapshot.objects.update_or_create(
        user=user, score_date=target_date, defaults=data
    )
    return snapshot
