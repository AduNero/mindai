from .base import *  # noqa: F401,F403

DEBUG = False

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],  # noqa: F405
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# nginx (docker/nginx/nginx.conf) always sets X-Forwarded-Proto and is the
# only ingress to the backend container (not port-mapped to the host in
# docker-compose.prod.yml), so trusting this header here is safe — without
# it, request.is_secure() is False even over real HTTPS, which throws off
# CSRF, redirects, and any absolute-URI building (e.g. the OIDC issuer).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# None (not the base setting's Lax) so the session cookie set by
# EstablishOIDCSessionView survives the LibreChat iframe's own top-level
# navigation to /o/authorize/ — requires Secure, which is guaranteed here
# since production always runs behind HTTPS.
SESSION_COOKIE_SAMESITE = "None"
# Scopes the cookie to the parent domain (e.g. ".mindcare.example.com")
# rather than just the exact host that set it, so it's sent on requests to
# the LibreChat subdomain too — see docs/architecture/librechat-integration.md.
# Unset by default (host-only cookie) since the value is deployment-specific.
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None)  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

LOGGING["root"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "INFO"  # noqa: F405
