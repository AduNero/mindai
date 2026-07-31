"""Settings for the automated test suite (pytest-django). Fast, isolated, no external services required."""

from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Tests exercise the AI *pipeline* (task wiring, graceful degradation,
# lexicon/risk-detection logic) with the HF pipelines mocked — see
# apps/ai_engine/tests/conftest.py — rather than downloading real model
# weights on every test run.
AI_ANALYSIS_ENABLED = True

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

MEDIA_ROOT = BASE_DIR / "test_media"  # noqa: F405
