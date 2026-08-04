# Changelog

All notable changes to MindCare AI are documented here. This project was
built incrementally in phases as a final-year IT project; each phase below
corresponds to a milestone in that build.

## [Unreleased]

### Fix Vercel build failure and make email-send failures non-fatal
- `frontend/src/utils/errors.ts` referenced `payload.message`/
  `payload.detail`, which don't exist on `ApiErrorPayload` (the backend's
  `custom_exception_handler` always wraps errors as
  `{success, error: {code, message, details}}` — there's no bare
  top-level `message`/`detail` case to handle). Since `npm run build` is
  `tsc -b && vite build`, this failed the type check and broke the whole
  Vercel deploy, not just one page. Reverted to the `error.message`-only
  path.
- Registration, resend-verification, and password-reset-request all
  called their email task's `.delay()` unwrapped; under
  `CELERY_TASK_ALWAYS_EAGER=True` that runs inline and re-raises the
  real send failure, so a broken email backend (already confirmed to
  happen — Render's free tier being unable to reach smtp.gmail.com at
  all) 500'd the entire request instead of just failing to send. Worse
  combined with the newly-added "unverified accounts can't log in"
  check: if the verification email never sends, the account is stuck
  with no way to verify and no way to log in. Added
  `_send_email_safely()` (`apps/users/views.py`) so these three now
  catch and log any send failure but still complete the request/return
  the token — the user can retry "Resend code" once delivery is fixed.
  Applied the same fix to `send_account_locked_email` in the login
  serializer (was also unwrapped, would have 500'd the *lockout-tripping
  login attempt itself*). Replaced the dead `except CeleryError` guard
  that was already in `PasswordResetRequestView` — under eager mode the
  real exception is never actually a `CeleryError`, so it never caught
  anything.
- Added regression tests confirming registration and the lockout-tripping
  login attempt both still succeed when the email backend raises.

### Fix 0003 migration colliding with a leftover index on live Postgres
- `0003_emailverificationtoken_attempts_and_more` failed on Render with
  `ProgrammingError: relation "email_verification_tokens_token_d2313ce1"
  already exists`. Root cause: the *original* OTP migration (deleted
  when OTP was reverted) had already run this same unique→plain-index
  transition on Render once, dropping the 0001 unique constraint and
  creating a plain btree index. Deleting that migration file only
  erased Django's record of the transition, not the transition itself —
  and Django computes index names deterministically from table+column,
  not migration history, so the new AlterField tried to recreate that
  exact same name. Added a Postgres-only pre-step that discovers and
  drops whatever unique constraint/index currently exists on `token`
  before the AlterField runs, so it doesn't matter which of the two
  possible history states a given database is actually in. Verified by
  reproducing Render's exact current schema (post-`0002_fix_token_
  column_drift`, pre-`0003`) against a real disposable Postgres
  container and confirming the migration now applies cleanly there —
  and confirmed the sqlite/test path (which never had the drift) is
  unaffected.

### Re-added OTP verification, plus an account-created notification
- Re-introduced OTP-based email verification and password reset (link
  tokens replaced with 6-digit codes again, same shape as the earlier
  attempt): `EmailVerificationToken`/`PasswordResetToken.token` narrowed
  to 6 chars with an `attempts` counter that locks a code out after 5
  wrong guesses; codes expire in 15/10 minutes. New migration
  `0003_emailverificationtoken_attempts_and_more.py` builds on top of
  `0002_fix_token_column_drift` (rather than reviving the old, deleted
  migration) and clears any pending long-format tokens before narrowing
  the column, for the same reason `0002_fix_token_column_drift` was
  needed the first time — verified against a real disposable Postgres
  container with a stale long token seeded in first.
- `RegisterView` now also creates an in-app "Welcome to MindCare AI"
  notification (`apps.notifications.services.notify`,
  `NotificationType.SYSTEM`) alongside the verification email, forced to
  the in-app channel only (the verification email already covers the
  "email" channel, so this avoids sending a redundant second email).
- Frontend: `RegisterPage` routes into `VerifyEmailPage` (rewritten as
  an email+code form with a resend button); `ForgotPasswordPage` gets a
  follow-up step into `ResetPasswordPage` (rewritten as email + code +
  new password), replacing the emailed-link flow on both pages.

### Fix live Postgres schema drift left over from the reverted OTP migration
- Reverting the OTP feature deleted
  `0002_emailverificationtoken_attempts_and_more.py` from the repo, but
  that only removes Django's record of how to *reverse* it — it doesn't
  touch a database the migration was already applied to. Render's live
  Postgres was stuck with `token varchar(6)` and a stray `attempts`
  column from that migration forever, since there was no longer a
  migration file to run in reverse. Once link-based tokens (48+ chars)
  started being generated again, every insert failed with
  `django.db.utils.DataError: value too long for type character
  varying(6)`.
- Added `0002_fix_token_column_drift.py`: a new forward migration
  (Postgres-only; sqlite/test DBs never had the drift) that widens
  `token` back to `varchar(255)` and drops the stray `attempts` column.
  Reproduced the exact failure and verified the fix against a real
  disposable Postgres container — same `DataError` before the migration,
  clean insert of a 48-char token after.

### Render email switched back to Gmail SMTP (by request, re-testing)
- `render.yaml`'s `EMAIL_BACKEND` reverted from
  `apps.common.email_backends.ResendBackend` to
  `django.core.mail.backends.smtp.EmailBackend` against
  `smtp.gmail.com:587`, at the user's request, to re-test whether Gmail
  SMTP actually works from Render (it previously failed live with
  `OSError: [Errno 101] Network is unreachable`). `EMAIL_TIMEOUT`
  (added earlier) still applies regardless of backend, so a repeat
  failure surfaces as a fast, clear error instead of hanging Gunicorn's
  sole worker. `ResendBackend` code is untouched and still available as
  the known-working fallback if this fails again — see
  `docs/architecture/free-tier-hosting.md` §4.

### Admins can add and remove other admins
- The generic admin user-update endpoint
  (`PATCH /api/v1/users/admin/<id>/`) already allowed setting
  `role=admin` — it only ever blocked `role=counselor` (which needs the
  dedicated promotion endpoint to also create a `CounselorProfile`) — but
  there was no way to trigger it from the UI. Added "Make admin"/"Remove
  admin" actions to `AdminUsersPage`, each behind a confirmation prompt.
- Added a server-side guard (`AdminUserUpdateSerializer.validate`) so an
  admin can't remove their own admin access and lock themselves out —
  the frontend also hides "Remove admin" on the signed-in admin's own
  row, but the real enforcement is server-side. Regression tests cover
  promotion, demotion, and the self-demotion block.

### Email delivery moved off SMTP to Resend's HTTP API (Render free tier)
- Root-caused verification/password-reset emails silently never arriving
  on Render: not a timeout — Render's free-tier network has **no
  outbound route to SMTP hosts at all**, confirmed live via `OSError:
  [Errno 101] Network is unreachable` connecting to `smtp.gmail.com:587`.
  Worse, because Django's SMTP backend has no connection timeout by
  default, this hung the sole synchronous Gunicorn worker on the
  free-tier deploy until Gunicorn's own timeout watchdog SIGKILLed it —
  taking the *entire app* down for every in-flight request, not just the
  email one. Same failure class as the hung-Redis-connection bug found
  earlier.
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
