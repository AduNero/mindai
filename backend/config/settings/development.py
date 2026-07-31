from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Verbose SQL logging is opt-in (noisy) — enable by setting DJANGO_LOG_SQL=1.
import os  # noqa: E402

if os.environ.get("DJANGO_LOG_SQL"):
    LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    }

INSTALLED_APPS += ["django_extensions"]  # noqa: F405
