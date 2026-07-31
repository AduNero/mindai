from django.conf import settings

from apps.common.constants import EMOTION_CHOICES

from .model_loader import get_emotion_pipeline

# GoEmotions (the default HF_EMOTION_MODEL) has 28 fine-grained labels; this
# platform tracks 8 (see apps.common.constants.EMOTION_CHOICES, chosen to
# match the spec). Rather than force an unrelated model to fit a custom
# label set, we use a model whose labels are a superset of ours and
# filter+renormalize down to just the 8 we track.
_TARGET_LABELS = {value for value, _ in EMOTION_CHOICES}


def analyze_emotion(text: str) -> dict:
    """
    Returns {"dominant_emotion": ..., "scores": {...}} — scores are the
    model's raw per-label confidences for our 8 tracked emotions,
    renormalized to sum to 1 across just those labels.
    """

    text = (text or "").strip()
    if not text:
        return {"dominant_emotion": None, "scores": {}, "model_version": "empty-input"}

    classifier = get_emotion_pipeline()
    raw_scores = classifier(text, truncation=True, max_length=512)[0]  # list of {"label", "score"}

    filtered = {item["label"]: float(item["score"]) for item in raw_scores if item["label"] in _TARGET_LABELS}

    if not filtered:
        # None of our 8 tracked labels scored — fall back to "neutral"-ish: no dominant emotion.
        return {"dominant_emotion": None, "scores": {}, "model_version": settings.HF_EMOTION_MODEL}

    total = sum(filtered.values()) or 1.0
    normalized = {label: round(score / total, 4) for label, score in filtered.items()}
    dominant = max(normalized, key=normalized.get)

    return {"dominant_emotion": dominant, "scores": normalized, "model_version": settings.HF_EMOTION_MODEL}
