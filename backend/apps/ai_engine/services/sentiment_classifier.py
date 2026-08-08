"""
Lazy, process-wide cached loading of the trained TF-IDF + logistic
regression sentiment classifier.

The fitted artifact is produced by `manage.py train_sentiment_classifier`
and committed to `apps/ai_engine/ml/artifacts/`. Loading it (not fitting
it) is what happens on the request path, and — unlike the transformer
pipelines this replaced — that's fast enough to not need a background
worker at all.
"""

import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger("apps")


class ClassifierUnavailableError(RuntimeError):
    """Raised when the trained sentiment classifier artifact isn't present."""


@lru_cache(maxsize=1)
def _load_artifact():
    import joblib

    path = settings.SENTIMENT_MODEL_ARTIFACT_PATH
    if not path.exists():
        raise ClassifierUnavailableError(
            f"No trained classifier artifact at {path} — run `manage.py train_sentiment_classifier` first."
        )
    logger.info("Loading sentiment classifier artifact: %s", path)
    return joblib.load(path)


def classify_sentiment(text: str) -> dict:
    """Returns {"label", "confidence", "model_version"} for `text`."""

    artifact = _load_artifact()
    pipeline = artifact["pipeline"]
    labels = pipeline.classes_

    probabilities = pipeline.predict_proba([text])[0]
    best_index = probabilities.argmax()

    return {
        "label": str(labels[best_index]),
        "confidence": float(probabilities[best_index]),
        "model_version": artifact["version"],
    }
