"""
Lazy, process-wide cached loading of Hugging Face pipelines.

Models are loaded on first use (not at Django startup) and cached for the
life of the process, since loading is the expensive part (hundreds of MB
of weights) and Celery workers are long-lived. Import of `transformers`
itself is deferred into these functions so the rest of the codebase (API,
tests, migrations) works without torch/transformers installed — see
`settings.AI_ANALYSIS_ENABLED` and requirements/ai.txt.
"""

import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger("apps")


class AIUnavailableError(RuntimeError):
    """Raised when AI analysis is requested but the AI stack isn't installed/enabled."""


def ai_enabled() -> bool:
    return settings.AI_ANALYSIS_ENABLED


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    if not ai_enabled():
        raise AIUnavailableError("AI_ANALYSIS_ENABLED is False.")
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise AIUnavailableError(
            "transformers/torch are not installed — see requirements/ai.txt"
        ) from exc

    logger.info("Loading sentiment model: %s", settings.HF_SENTIMENT_MODEL)
    return pipeline(
        "sentiment-analysis",
        model=settings.HF_SENTIMENT_MODEL,
        device=_device_index(),
    )


@lru_cache(maxsize=1)
def get_emotion_pipeline():
    if not ai_enabled():
        raise AIUnavailableError("AI_ANALYSIS_ENABLED is False.")
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise AIUnavailableError(
            "transformers/torch are not installed — see requirements/ai.txt"
        ) from exc

    logger.info("Loading emotion model: %s", settings.HF_EMOTION_MODEL)
    return pipeline(
        "text-classification",
        model=settings.HF_EMOTION_MODEL,
        top_k=None,  # return scores for every label, not just the top one
        device=_device_index(),
    )


def _device_index():
    # transformers' `pipeline(device=...)` wants -1 for CPU, or a CUDA index.
    return 0 if settings.HF_DEVICE == "cuda" else -1
