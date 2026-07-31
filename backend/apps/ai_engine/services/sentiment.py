from django.conf import settings

from apps.common.constants import SENTIMENT_NEGATIVE, SENTIMENT_NEUTRAL, SENTIMENT_POSITIVE

from . import lexicon
from .model_loader import get_sentiment_pipeline

_LABEL_MAP = {
    "POSITIVE": SENTIMENT_POSITIVE,
    "NEGATIVE": SENTIMENT_NEGATIVE,
    "LABEL_1": SENTIMENT_POSITIVE,  # some sst2 checkpoints use LABEL_0/LABEL_1
    "LABEL_0": SENTIMENT_NEGATIVE,
}


def analyze_sentiment(text: str) -> dict:
    """
    Runs the configured Hugging Face sentiment model, downgrades low-confidence
    calls to "neutral", and layers on lexicon-based stress/anxiety/burnout/
    depression indicator scores plus extracted keywords.

    Returns a dict matching apps.ai_engine.models.SentimentResult's fields
    (minus the polymorphic content_type/object_id, set by the caller).
    """

    text = (text or "").strip()
    if not text:
        return {
            "sentiment": SENTIMENT_NEUTRAL,
            "confidence_score": 0.0,
            "keywords": [],
            "model_version": "empty-input",
            **lexicon.score_constructs("", SENTIMENT_NEUTRAL),
        }

    classifier = get_sentiment_pipeline()
    # Most sentiment checkpoints cap at 512 tokens; truncate at the pipeline level.
    result = classifier(text, truncation=True, max_length=512)[0]

    raw_label = result["label"].upper()
    confidence = float(result["score"])

    if confidence < settings.HF_SENTIMENT_NEUTRAL_THRESHOLD:
        sentiment = SENTIMENT_NEUTRAL
    else:
        sentiment = _LABEL_MAP.get(raw_label, SENTIMENT_NEUTRAL)

    construct_scores = lexicon.score_constructs(text, sentiment)
    keywords = lexicon.extract_keywords(text)

    return {
        "sentiment": sentiment,
        "confidence_score": round(confidence, 4),
        "keywords": keywords,
        "model_version": settings.HF_SENTIMENT_MODEL,
        **construct_scores,
    }
