# Deployment Guide

This guide covers deploying MindCare AI to a production-like environment.
It assumes the Docker Compose setup from
[installation-guide.md](installation-guide.md) as the baseline and layers
on the hardening/operational concerns that only matter once real user data
is involved.

## 1. Environment configuration

Use `config.settings.production` (`DJANGO_SETTINGS_MODULE=config.settings.production`
in `.env`). Compared to development, this enables:

- `DEBUG=False`, strict `ALLOWED_HOSTS`
- HTTPS enforcement (`SECURE_SSL_REDIRECT`), HSTS, secure/HttpOnly cookies
- `SESSION_COOKIE_SAMESITE="None"` (required for the LibreChat iframe SSO
  bridge to work cross-site over HTTPS — see
  [librechat-integration.md](librechat-integration.md))
- WhiteNoise for static file serving (or serve `staticfiles/` via Nginx directly — see below)

**Secrets that must be real, unique values in production** (never reuse
the `.env.example` placeholders): `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`,
`OIDC_RSA_PRIVATE_KEY`, `MYSQL_PASSWORD`/`MYSQL_ROOT_PASSWORD`,
`LIBRECHAT_OIDC_CLIENT_SECRET`, `LIBRECHAT_JWT_SECRET`,
`LIBRECHAT_JWT_REFRESH_SECRET`, `LIBRECHAT_CREDS_KEY`/`LIBRECHAT_CREDS_IV`.
Manage these via your platform's secret store (Docker secrets, a cloud
provider's secrets manager, etc.) rather than a committed `.env` file.

## 2. Domain and reverse-proxy topology

**Recommended**: put the frontend/API and LibreChat on **subdomains of the
same parent domain** — this avoids the third-party-cookie limitation
discussed in [librechat-integration.md](librechat-integration.md) without
depending on LibreChat supporting being served under a URL subpath (not
guaranteed for every SPA without explicit base-path build support).
Subdomains of one parent domain are still the same *site* for SameSite
cookie purposes (the boundary is the registrable domain, not the
subdomain), so a cookie scoped to `Domain=mindcare.example.com` is sent on
requests to either subdomain:

```
https://app.mindcare.example.com/    → frontend (static build) + backend under /api/, /o/, /admin/
https://chat.mindcare.example.com/   → librechat
```

No frontend code changes are needed either way — `VITE_LIBRECHAT_URL`
(the iframe's `src` in `AIChatPage.tsx`) is just an env var; point it at
whichever URL you route LibreChat to. See `docker/nginx/` for the
reverse-proxy config implementing this (Phase
9). Obtain TLS certificates via Let's Encrypt/Certbot or your cloud
provider's managed certificates — this project does not include a
particular ACME client, since that choice is host-environment-specific.

## 3. Database

- Run MySQL with persistent volumes (already configured in
  `docker-compose.yml`'s `db` service) — never `tmpfs` in production.
- Take regular backups. `backend/scripts/backup_db.sh` wraps `mysqldump`
  against the running `db` service and writes a timestamped, gzipped dump
  to `backend/scripts/backups/`; run it on a cron schedule (or use your
  cloud provider's managed-MySQL backup feature if you're not self-hosting
  the database container). `backend/scripts/restore_db.sh <file>` restores
  a dump back into a running stack — it requires typing the database name
  to confirm before overwriting data.
- Run migrations as a release step, before traffic is routed to a new
  version: `python manage.py migrate --noinput`.
- Consider a managed MySQL service (RDS, Cloud SQL, etc.) instead of the
  `db` container for production — swap `MYSQL_HOST`/`MYSQL_PORT` in `.env`
  and drop the `db` service from your production compose override.

## 4. Background workers

Celery worker and beat must run as long-lived processes, restarted on
failure:

- **Docker Compose**: already defined as `celery_worker`/`celery_beat`
  services with `restart: unless-stopped` (see `docker-compose.yml`).
- **Bare metal/VM**: run both under `systemd` or a process supervisor
  (`supervisord`) rather than `nohup`, so they restart automatically.

Re-run `python manage.py setup_periodic_tasks` (once, per app that defines
one — `notifications`, `ai_engine`, `chat`) after each fresh deployment of
a new database, since periodic task schedules are stored in the database
(`django_celery_beat`), not in code.

## 5. AI worker sizing

`requirements/ai.txt` (torch + transformers) is only needed on the
container(s) actually running `analyze_content` tasks. For a small
deployment, running it in the same `celery_worker` container is simplest.
At larger scale, split into a dedicated `celery_worker_ai` service/queue so
CPU-heavy model inference doesn't starve latency-sensitive tasks (email,
notifications). This project ships the simpler single-worker setup;
splitting queues is a straightforward Celery routing change
(`task_routes` in `config/settings/base.py`) if you need it.

## 6. LibreChat

- Set real `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/etc. in
  `librechat/config/librechat.env` — without a model provider configured,
  the chat UI loads but can't generate responses.
- `librechat_mongo` needs the same backup discipline as MySQL if
  conversation history matters to your deployment.
- Confirm `OPENID_ISSUER` in `librechat.env` points at the *publicly
  reachable* URL for `/o` (not `http://backend:8000/o`, which only
  resolves inside the Docker network) if LibreChat and MindCare's backend
  aren't on the same Docker network in your topology.

## 7. Observability

Not bundled by default (kept out of scope to avoid mandating a specific
vendor), but the codebase is structured to make adding it straightforward:

- **Logging**: `LOGGING` in `config/settings/base.py` already routes
  Django/`apps.*` logs to stdout — any log aggregator (CloudWatch, Loki,
  Datadog) that scrapes container stdout works without code changes.
  `requirements/production.txt` includes `sentry-sdk` — set `SENTRY_DSN`
  and add the SDK's Django integration in `production.py` to enable it.
- **Audit trail**: `apps.audit.AuditLog` and `apps.admin_panel.AdminActionLog`
  are already the durable, queryable record of security-relevant and
  administrative events — export these periodically if you need
  longer retention than your database backup window.

## 8. Release checklist

```
[ ] .env copied from .env.production.example, all secrets production-unique
[ ] CI green on the commit being deployed (.github/workflows/ci.yml)
[ ] DJANGO_SETTINGS_MODULE=config.settings.production
[ ] SESSION_COOKIE_SAMESITE=None only paired with real HTTPS
[ ] docker compose exec backend python manage.py migrate --noinput
[ ] docker compose exec backend python manage.py collectstatic --noinput
[ ] docker compose exec backend python manage.py setup_periodic_tasks (each app)
[ ] docker compose exec backend python manage.py setup_librechat_oidc_client
[ ] OIDC_RSA_PRIVATE_KEY set and backend/celery restarted after
[ ] TLS certificates valid and auto-renewing
[ ] Database backups scheduled and tested — backend/scripts/backup_db.sh /
    restore_db.sh (restore, not just backup)
[ ] At least one LLM provider key set in librechat.env
[ ] Emergency resources seeded for every country you expect users from
[ ] backend/scripts/smoke_test.sh BASE_URL=https://app.<domain> passes
    against the freshly deployed stack
```
