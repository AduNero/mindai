"""Settings for the automated test suite (pytest-django). Fast, isolated, no external services required."""

from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Tests exercise the analysis pipeline (synchronous journal-entry wiring,
# risk-detection logic) with the sentiment classifier mocked — see
# conftest.py's `_mock_sentiment_classifier` — rather than requiring a
# trained joblib artifact to be present for every test run.
AI_ANALYSIS_ENABLED = True

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# base.py's CACHES points at Redis (needed in real deployments so rate
# limiting works correctly across multiple worker processes — see base.py)
# but the test suite shouldn't require a real Redis server to run.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

MEDIA_ROOT = BASE_DIR / "test_media"  # noqa: F405
