"""
Forecasts tomorrow's likely mood from a short-term linear trend over the
user's recent mood entries.

Uses ordinary least-squares on (day offset, mood score) pairs rather than a
trained model: with typically a handful of entries per user, a learned
model would overfit noise, while a transparent trend line is both
defensible and easy to explain on the dashboard ("trending toward X based
on the last 14 days").
"""

from datetime import date, timedelta

import numpy as np

from apps.common.constants import (
    MOOD_ANGRY,
    MOOD_ANXIOUS,
    MOOD_DEPRESSED,
    MOOD_EXCITED,
    MOOD_HAPPY,
    MOOD_NEUTRAL,
    MOOD_SAD,
    MOOD_TIRED,
)

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
_SCORE_TO_MOOD = {
    1: MOOD_DEPRESSED,
    2: MOOD_SAD,
    3: MOOD_ANXIOUS,
    4: MOOD_NEUTRAL,
    5: MOOD_HAPPY,
}

MIN_ENTRIES_REQUIRED = 3
DEFAULT_WINDOW_DAYS = 14


def predict_next_mood(user, window_days: int = DEFAULT_WINDOW_DAYS) -> dict | None:
    """
    Returns {"predicted_mood", "confidence_score", "based_on_window_days"}
    or None if there isn't enough recent data to make a reasonable call.
    """

    window_start = date.today() - timedelta(days=window_days)
    entries = list(
        user.mood_entries.filter(entry_date__gte=window_start).order_by("entry_date").values("entry_date", "mood")
    )
    if len(entries) < MIN_ENTRIES_REQUIRED:
        return None

    x = np.array([(e["entry_date"] - window_start).days for e in entries], dtype=float)
    y = np.array([_MOOD_SCORE.get(e["mood"], 3) for e in entries], dtype=float)

    if np.std(x) == 0:
        # All entries on the same day — no trend to extrapolate.
        return None

    slope, intercept = np.polyfit(x, y, 1)
    tomorrow_offset = (date.today() - window_start).days + 1
    predicted_score = slope * tomorrow_offset + intercept
    predicted_score_clamped = int(round(min(max(predicted_score, 1), 5)))

    residuals = y - (slope * x + intercept)
    fit_error = float(np.sqrt(np.mean(residuals**2))) if len(residuals) > 1 else 0.0
    # Lower residual error -> higher confidence; a perfect fit (error 0) -> ~0.95 confidence cap.
    confidence = max(0.3, min(0.95, 1 - fit_error / 2))

    return {
        "predicted_mood": _SCORE_TO_MOOD[predicted_score_clamped],
        "confidence_score": round(confidence, 3),
        "based_on_window_days": window_days,
    }


def save_mood_prediction(user, window_days: int = DEFAULT_WINDOW_DAYS):
    from apps.ai_engine.models import MoodPrediction

    prediction = predict_next_mood(user, window_days)
    if not prediction:
        return None

    tomorrow = date.today() + timedelta(days=1)
    obj, _ = MoodPrediction.objects.update_or_create(
        user=user,
        predicted_for_date=tomorrow,
        defaults={
            "predicted_mood": prediction["predicted_mood"],
            "confidence_score": prediction["confidence_score"],
            "based_on_window_days": prediction["based_on_window_days"],
        },
    )
    return obj
