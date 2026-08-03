"""
Base Django settings shared by every environment. Environment-specific
settings (development.py / production.py) import * from this module and
override only what differs.
"""

from datetime import timedelta
from pathlib import Path

import os

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
)
# Local dev convenience: read the repo-root .env if present. In Docker,
# environment variables are already injected by docker-compose, so a
# missing file here is not an error. Skipped under the test settings
# module — the test suite is meant to be hermetic (config/settings/test.py
# hardcodes its own DB/email/etc regardless), and a developer's local .env
# (e.g. a non-default DEFAULT_CRISIS_COUNTRY) silently overriding a
# Python-level default that tests assert against would make results depend
# on whoever's machine runs them.
env_file = REPO_ROOT / ".env"
if env_file.exists() and os.environ.get("DJANGO_SETTINGS_MODULE") != "config.settings.test":
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
# Render assigns each web service a hostname with an unpredictable random
# suffix (e.g. mindcare-backend-m3ji.onrender.com) that can't be known
# ahead of time in render.yaml — RENDER_EXTERNAL_HOSTNAME is injected
# automatically by Render itself at runtime with the real value, so this
# covers it without needing to hardcode a guess. A no-op everywhere else,
# since the env var simply won't exist off Render.
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

SITE_NAME = env("SITE_NAME", default="MindCare AI")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:5173")

# --- Applications ---
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
]

LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.moods",
    "apps.journals",
    "apps.wellness",
    "apps.assessments",
    "apps.ai_engine",
    "apps.recommendations",
    "apps.chat",
    "apps.appointments",
    "apps.notifications",
    "apps.resources",
    "apps.admin_panel",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.audit.middleware.RequestContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---
# MySQL 8 (docker-compose / VPS deployments) by default. If DATABASE_URL is
# set (e.g. Render's auto-injected Postgres connection string for the free
# managed-Postgres, docker-compose-less hosting path — see
# docs/architecture/free-tier-hosting.md), that takes over instead, since
# free MySQL hosting isn't realistically available. Both paths are fully
# supported; nothing about the app is MySQL- or Postgres-specific beyond
# this block.
if env("DATABASE_URL", default=""):
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("MYSQL_DATABASE", default="mindcare_ai"),
            "USER": env("MYSQL_USER", default="mindcare_user"),
            "PASSWORD": env("MYSQL_PASSWORD", default=""),
            "HOST": env("MYSQL_HOST", default="localhost"),
            "PORT": env("MYSQL_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_USER_MODEL = "users.User"

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static / media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
# See config/urls.py — only for deployments with no reverse proxy in
# front of Django to serve /media/ directly (e.g. Render; not the VPS
# path, which uses docker/nginx/nginx.conf for this instead).
SERVE_MEDIA_VIA_DJANGO = env.bool("SERVE_MEDIA_VIA_DJANGO", default=False)

# Uploaded file constraints (profile pictures, resource thumbnails).
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    # Without this, DRF's IP-based throttle identity (used for anonymous
    # requests, e.g. login attempts) takes the *entire* raw
    # X-Forwarded-For header verbatim as the cache key whenever one is
    # present — behind any reverse proxy (nginx on the VPS path, Render's
    # edge on the free-tier path) that value isn't guaranteed identical
    # across requests, so the throttle counter can silently never
    # accumulate and rate limiting stops working. NUM_PROXIES=1 makes it
    # correctly extract just the actual client IP instead. Safe for
    # direct/no-proxy access too (falls back to REMOTE_ADDR when no
    # X-Forwarded-For header is present at all).
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
    "DEFAULT_THROTTLE_RATES": {
        "auth": env("RATE_LIMIT_LOGIN", default="5/min"),
        "default": env("RATE_LIMIT_DEFAULT", default="100/min"),
        "ai_analysis": "30/min",
        "report_generation": "10/min",
    },
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# --- JWT ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MIN", default=15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}
# Note: the custom login serializer (apps.users.serializers.MindCareTokenObtainPairSerializer)
# is wired up via the view's `serializer_class`, not a SIMPLE_JWT setting —
# simplejwt has no such override key.

# "Remember me" extends the refresh token lifetime beyond the default above.
JWT_REMEMBER_ME_REFRESH_LIFETIME = timedelta(days=30)

# --- Account lockout (brute-force login protection) ---
ACCOUNT_LOCKOUT_THRESHOLD = env.int("ACCOUNT_LOCKOUT_THRESHOLD", default=5)
ACCOUNT_LOCKOUT_DURATION_MINUTES = env.int("ACCOUNT_LOCKOUT_DURATION_MINUTES", default=15)

# --- API documentation (Swagger / OpenAPI) ---
SPECTACULAR_SETTINGS = {
    "TITLE": "MindCare AI API",
    "DESCRIPTION": (
        "AI-Powered Mental Health Monitoring and Support Platform API. "
        "MindCare AI does not diagnose medical conditions and is not a "
        "substitute for a licensed mental health professional."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "COMPONENT_SPLIT_REQUEST": True,
}

# --- CORS / CSRF ---
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])
# The API is bearer-token (JWT) auth throughout, so cross-origin requests
# never need to carry cookies — only same-origin use of the Django admin
# relies on the session cookie at all.
CORS_ALLOW_CREDENTIALS = False
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:5173"])

# --- Email ---
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="MindCare AI <no-reply@mindcare.ai>")
# Without this, smtplib blocks with no timeout at all. On a single
# synchronous Gunicorn worker (the free-tier hosting path), a stalled SMTP
# connection — e.g. the host's outbound network can't actually reach
# EMAIL_HOST — doesn't just fail that one request: it hangs the sole
# worker until Gunicorn's own timeout watchdog SIGKILLs the process,
# taking the entire app down for every in-flight request, not just email.
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
# Used by apps.common.email_backends.ResendBackend (EMAIL_BACKEND set to
# it on the Render free-tier path, where raw SMTP has no outbound route
# at all — see that module's docstring).
RESEND_API_KEY = env("RESEND_API_KEY", default="")

# --- Redis / Celery ---
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# Runs tasks synchronously, in-process, instead of dispatching to a
# separate worker — for deployments with no persistent background-worker
# process available (e.g. free-tier PaaS hosting; see
# docs/architecture/free-tier-hosting.md). Off by default: docker-compose
# and VPS deployments run real celery_worker/celery_beat processes.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = CELERY_TASK_ALWAYS_EAGER

# DRF's ScopedRateThrottle (and anything else using django.core.cache)
# needs a cache shared across processes to work correctly — the default
# LocMemCache is per-process, so with multiple Gunicorn workers each one
# would enforce rate limits independently, effectively multiplying the
# real limit by the worker count. Django's native Redis backend (built
# in since Django 4.0, no extra package needed) fixes that.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# --- Hugging Face / AI engine (see apps.ai_engine, Phase 5) ---
# AI_ANALYSIS_ENABLED lets the backend run (migrations, API, tests) without
# torch/transformers installed — see requirements/ai.txt, only needed on
# workers that actually run inference. Analysis tasks no-op gracefully when
# this is False instead of failing on a missing import.
AI_ANALYSIS_ENABLED = env.bool("AI_ANALYSIS_ENABLED", default=True)
HUGGINGFACE_API_TOKEN = env("HUGGINGFACE_API_TOKEN", default="")
HF_SENTIMENT_MODEL = env("HF_SENTIMENT_MODEL", default="distilbert-base-uncased-finetuned-sst-2-english")
# GoEmotions' 28 fine-grained labels include all 8 emotions this platform
# tracks (joy, fear, sadness, anger, love, surprise, optimism, disappointment),
# so results are filtered/renormalized down to that set — see
# apps.ai_engine.services.emotion.
HF_EMOTION_MODEL = env("HF_EMOTION_MODEL", default="SamLowe/roberta-base-go_emotions")
HF_DEVICE = env("HF_DEVICE", default="cpu")
# Below this confidence, sentiment classification falls back to "neutral"
# rather than trusting a low-confidence positive/negative call.
HF_SENTIMENT_NEUTRAL_THRESHOLD = env.float("HF_SENTIMENT_NEUTRAL_THRESHOLD", default=0.6)

# --- AI chat companion (see apps.chat.services.llm) ---
# Any OpenAI-API-compatible provider works — default is NVIDIA NIM.
CHAT_LLM_API_KEY = env("CHAT_LLM_API_KEY", default="")
CHAT_LLM_BASE_URL = env("CHAT_LLM_BASE_URL", default="https://integrate.api.nvidia.com/v1")
CHAT_LLM_MODEL = env("CHAT_LLM_MODEL", default="nvidia/llama-3.3-nemotron-super-49b-v1")

# --- Crisis / emergency resources ---
DEFAULT_CRISIS_COUNTRY = env("DEFAULT_CRISIS_COUNTRY", default="US")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
