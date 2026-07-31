"""
Base Django settings shared by every environment. Environment-specific
settings (development.py / production.py) import * from this module and
override only what differs.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
)
# Local dev convenience: read the repo-root .env if present. In Docker,
# environment variables are already injected by docker-compose, so a
# missing file here is not an error.
env_file = REPO_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

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
    # OIDC provider — MindCare acts as LibreChat's SSO identity provider (Phase 6).
    "oauth2_provider",
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

# --- Database (MySQL 8) ---
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

# --- OIDC provider (django-oauth-toolkit) — MindCare as LibreChat's SSO IdP ---
# LibreChat is configured (via its own OPENID_* env vars) to trust this
# server as an OpenID Connect provider, so a user who is already logged
# into MindCare can SSO into the embedded LibreChat UI without a second
# login. See apps.users.oidc and apps/users/management/commands/setup_librechat_oidc_client.py.
OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    # .env stores this with literal \n escapes (see generate_oidc_rsa_key
    # management command) since real newlines don't survive a single .env line.
    "OIDC_RSA_PRIVATE_KEY": env("OIDC_RSA_PRIVATE_KEY", default="").replace("\\n", "\n"),
    "OAUTH2_VALIDATOR_CLASS": "apps.users.oidc.MindCareOAuth2Validator",
    # Hardcodes the issuer used in the discovery document and id_token `iss`
    # claim instead of deriving it from the request. Needed whenever the
    # externally-visible scheme/host differs from what the backend process
    # itself sees (behind a TLS-terminating reverse proxy) — avoids relying
    # on X-Forwarded-Proto trust for something as security-sensitive as the
    # OIDC issuer identity. Leave unset to fall back to request-derivation.
    "OIDC_ISS_ENDPOINT": env("OIDC_ISS_ENDPOINT", default=""),
    "SCOPES": {
        "openid": "OpenID Connect scope",
        "profile": "Access to your name",
        "email": "Access to your email address",
    },
    "PKCE_REQUIRED": False,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,
}
LIBRECHAT_OIDC_CLIENT_ID = env("LIBRECHAT_OIDC_CLIENT_ID", default="librechat")
LIBRECHAT_OIDC_CLIENT_SECRET = env("LIBRECHAT_OIDC_CLIENT_SECRET", default="")
LIBRECHAT_OIDC_REDIRECT_URI = env(
    "LIBRECHAT_OIDC_REDIRECT_URI", default=f"{env('LIBRECHAT_URL', default='http://localhost:3080')}/oauth/openid/callback"
)

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
# True (not False) because apps.users.views.EstablishOIDCSessionView sets a
# session cookie that the frontend's cross-origin XHR must be able to
# receive/send (see api/client.ts's withCredentials) — everything else on
# this API is bearer-token auth and doesn't need cookies at all. Safe with
# CORS_ALLOW_CREDENTIALS=True only because CORS_ALLOWED_ORIGINS is an
# explicit list, never "*".
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:5173"])

# The LibreChat iframe's own top-level navigations (its OpenID auto-redirect
# to /o/authorize/) happen inside a nested browsing context, which most
# browsers treat as third-party even though everything is on localhost in
# dev — SameSite=Lax cookies are commonly still sent for localhost across
# ports, but production.py switches to None+Secure to guarantee it over
# HTTPS. The most robust fix either way is deploying LibreChat behind the
# same reverse-proxy domain as the frontend (see docker/nginx, Phase 9).
SESSION_COOKIE_SAMESITE = "Lax"

# --- Email ---
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="MindCare AI <no-reply@mindcare.ai>")

# --- Redis / Celery ---
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

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

# --- LibreChat integration (see apps.chat, Phase 6) ---
LIBRECHAT_URL = env("LIBRECHAT_URL", default="http://localhost:3080")
LIBRECHAT_API_KEY = env("LIBRECHAT_API_KEY", default="")
LIBRECHAT_JWT_SECRET = env("LIBRECHAT_JWT_SECRET", default="")

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
