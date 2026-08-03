# Changelog

All notable changes to MindCare AI are documented here. This project was
built incrementally in phases as a final-year IT project; each phase below
corresponds to a milestone in that build.

## [Unreleased]

### Email delivery moved off SMTP to Resend's HTTP API (Render free tier)
- Root-caused the OTP emails silently never arriving on Render: it
  wasn't the OTP code itself, and wasn't even a timeout — Render's
  free-tier network has **no outbound route to SMTP hosts at all**,
  confirmed live via `OSError: [Errno 101] Network is unreachable`
  connecting to `smtp.gmail.com:587`. Worse, because Django's SMTP
  backend has no connection timeout by default, this hung the sole
  synchronous Gunicorn worker on the free-tier deploy until Gunicorn's
  own timeout watchdog SIGKILLed it — taking the *entire app* down for
  every in-flight request, not just the email one. Same failure class as
  the hung-Redis-connection bug found earlier.
- Added `EMAIL_TIMEOUT` (`config/settings/base.py`, default 10s) so any
  future stalled mail connection fails fast instead of hanging the
  worker.
- Added `apps.common.email_backends.ResendBackend`, a Django
  `EMAIL_BACKEND` that sends via Resend's HTTP API (port 443, the same
  path outbound AI chat calls already use successfully) instead of raw
  SMTP sockets. `render.yaml`'s free-tier Blueprint now points
  `EMAIL_BACKEND` at it and takes `RESEND_API_KEY` instead of the old
  Gmail SMTP vars; see `docs/architecture/free-tier-hosting.md` §4 for
  setup (the VPS/Docker path is unaffected — its network isn't
  restricted, so Gmail SMTP there is untouched).

### Email verification and password reset switched to OTP codes
- Registration and forgotten-password now send a 6-digit numeric code by
  email instead of a clickable link, matching the OTP pattern users
  expect. `POST /api/v1/auth/verify-email/` and
  `POST /api/v1/auth/password-reset/confirm/` now take `{email, otp}`
  (plus `new_password`/`new_password_confirm` for the reset endpoint)
  instead of a bare `{token}`.
- `EmailVerificationToken`/`PasswordResetToken.token` now stores the
  6-digit code rather than a long random link token; codes are no longer
  globally unique (validated by `user + code` instead) and each token
  tracks failed-attempt count, locking out further guesses after 5 wrong
  attempts regardless of expiry. Verification codes expire in 15 minutes,
  reset codes in 10.
- Frontend: `RegisterPage` now routes to `VerifyEmailPage` (rewritten as
  an OTP-entry form with a resend button) instead of straight to login;
  `ForgotPasswordPage` now offers a follow-up step into
  `ResetPasswordPage` (rewritten as an email + OTP + new-password form)
  instead of relying on an emailed link.

### AI chat re-architecture — LibreChat removed
- Replaced the LibreChat-based chat integration (Phase 6) with a direct
  integration: `apps.chat.services.llm` calls any OpenAI-API-compatible
  provider (default: NVIDIA NIM) via the `openai` Python client. See
  `docs/architecture/ai-chat-integration.md`.
- Removed: the `librechat`/`librechat_mongo` Docker services and the
  `librechat/` config directory, the dev-only `oidc-proxy` TLS proxy and
  `docker/oidc-proxy/`, MindCare's OIDC provider role
  (`django-oauth-toolkit`, `apps.users.oidc`, `EstablishOIDCSessionView`,
  the `generate_oidc_rsa_key`/`setup_librechat_oidc_client` management
  commands), the `pymongo`/`cryptography`/`django-oauth-toolkit`
  dependencies, and the `librechat_conversation_id`/`librechat_message_id`
  columns on `ChatSession`/`ChatMessage`.
- `ChatSessionViewSet.send` now generates and persists the AI reply
  synchronously in the same request that saves the user's message,
  instead of relying on an external sync job; the frontend's "Live Chat"
  iframe tab and LibreChat-history-sync UI were removed accordingly.
- Fixed two bugs found while making this change: `config/settings/base.py`
  was loading the repo-root `.env` even under the test settings module,
  so a developer's local `DEFAULT_CRISIS_COUNTRY` (or any other .env
  override) could silently break "hermetic" test assertions; and
  `apps.ai_engine`/`apps.notifications` both defined a management command
  named `setup_periodic_tasks`, so only one was ever actually reachable —
  `ai_engine`'s was renamed to `setup_ai_periodic_tasks`.
- `production.py` also gained `SECURE_PROXY_SSL_HEADER` (nginx already
  sends `X-Forwarded-Proto`; this was previously untrusted, so
  `request.is_secure()` was silently `False` behind the reverse proxy even
  over real HTTPS) and `CORS_ALLOW_CREDENTIALS` was reverted to `False`
  (nothing needs cookies now that the OIDC session bridge is gone).

## [1.0.0] — Initial release

### Phase 1 — Folder structure & project scaffolding
- Established the monorepo layout: `backend/` (Django), `frontend/` (React +
  TypeScript), `librechat/` (LibreChat config), `docker/`, `docs/`.

### Phase 2 — Database schema
- Designed the normalized MySQL schema across all domains (users, moods,
  journals, assessments, chat, appointments, notifications, resources,
  admin, audit) using UUID primary keys throughout.
- Documented the full ERD and table reference in `docs/database/schema.md`.

### Phase 3 — Backend (Django REST Framework)
- Custom email-based `User` model with JWT auth (access/refresh, account
  lockout, remember-me, session tracking), RBAC permission classes, and
  Swagger/OpenAPI docs via drf-spectacular.
- REST APIs for moods, journals, assessments (PHQ-9, GAD-7, stress, burnout,
  self-esteem), notifications, appointments, resources, and admin analytics.

### Phase 4 — Frontend (React + TypeScript)
- Vite + React 18 + TypeScript (strict) + Tailwind CSS SPA with React
  Router, Axios (JWT refresh interceptor), Chart.js dashboards, Framer
  Motion transitions, dark/light theme, and code-split routes.

### Phase 5 — AI integration
- Sentiment analysis (DistilBERT SST-2) and emotion detection (RoBERTa
  go_emotions, mapped to the required 8 emotions) via Hugging Face
  Transformers, run asynchronously through Celery.
- Lexicon-based stress/anxiety/burnout/depression scoring and tiered
  crisis-phrase risk detection, chosen over black-box models for
  auditability in a safety-critical context.
- Wellness score (0–100, six equally-weighted components) and mood-trend
  prediction (OLS extrapolation).

### Phase 6 — LibreChat integration
- Self-hosted, Dockerized LibreChat wired up as MindCare's AI chat
  companion, with MindCare acting as an OIDC identity provider for
  browser-redirect SSO and a one-directional MongoDB read-sync into
  MindCare's own chat history tables for AI analysis and search/export.

### Phase 7 — Testing
- 200 backend tests (pytest-django, factory-boy, mocked AI pipelines,
  86% coverage) covering models, serializers, views, permissions, and
  security behaviour (rate limiting, RBAC, input validation).
- Frontend unit tests (Vitest + Testing Library).
- Fixed several real bugs surfaced only by end-to-end verification (see
  git history for details), including a missing `serializer_class`, an
  unreachable DB-level uniqueness constraint, and cross-test cache leakage
  from DRF's throttle counters.

### Phase 8 — Documentation
- Full documentation suite: architecture diagrams, sequence diagrams,
  flowcharts, emergency-detection design and ethics boundaries,
  LibreChat integration notes, API reference, user and admin manuals,
  a combined technical/project report, and defense presentation slides.

### Phase 9 — Docker Compose configuration
- Multi-stage Dockerfiles (backend: base/worker split for heavy AI
  dependencies; frontend: dev/build/production split).
- `docker-compose.yml` for local development and `docker-compose.prod.yml`
  for production, both with healthcheck-gated service dependencies.
- Nginx reverse proxy with subdomain-based routing (`app.` / `chat.`) so
  the LibreChat SSO session cookie can be scoped to the parent domain.

### Phase 10 — Deployment
- GitHub Actions CI (`.github/workflows/ci.yml`): backend test suite with
  coverage and a migration-drift check, frontend typecheck/lint/test/build,
  and Docker Compose config validation for both stacks.
- Operational scripts in `backend/scripts/`: `backup_db.sh`,
  `restore_db.sh`, and `smoke_test.sh` for post-deploy verification.
- `.env.production.example` — production-hardened environment template
  (HTTPS-only, subdomain cookie scoping, no debug mode).
