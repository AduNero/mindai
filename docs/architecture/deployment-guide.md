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
- WhiteNoise for static file serving (or serve `staticfiles/` via Nginx directly — see below)

**Secrets that must be real, unique values in production** (never reuse
the `.env.example` placeholders): `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`,
`MYSQL_PASSWORD`/`MYSQL_ROOT_PASSWORD`, `CHAT_LLM_API_KEY`.
Manage these via your platform's secret store (Docker secrets, a cloud
provider's secrets manager, etc.) rather than a committed `.env` file.

## 2. Domain and reverse-proxy topology

A single domain in front of the frontend + API is all this needs — see
`docker/nginx/nginx.conf` for the reverse-proxy config
(`app.mindcare.example.com` by default; swap in your real domain). Obtain
TLS certificates via Let's Encrypt/Certbot or your cloud provider's
managed certificates — this project does not include a particular ACME
client, since that choice is host-environment-specific.

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

Re-run `python manage.py setup_periodic_tasks` (notifications app) and
`python manage.py setup_ai_periodic_tasks` (ai_engine app) after each
fresh deployment of a new database, since periodic task schedules are
stored in the database (`django_celery_beat`), not in code.

## 5. AI worker sizing

`requirements/ai.txt` (torch + transformers) is only needed on the
container(s) actually running `analyze_content` tasks. For a small
deployment, running it in the same `celery_worker` container is simplest.
At larger scale, split into a dedicated `celery_worker_ai` service/queue so
CPU-heavy model inference doesn't starve latency-sensitive tasks (email,
notifications). This project ships the simpler single-worker setup;
splitting queues is a straightforward Celery routing change
(`task_routes` in `config/settings/base.py`) if you need it.

## 6. AI chat companion

Set a real `CHAT_LLM_API_KEY` (and `CHAT_LLM_BASE_URL`/`CHAT_LLM_MODEL` if
not using the NVIDIA NIM default) — without it, the chat companion still
loads but every message gets an "AI companion is temporarily unavailable"
error instead of a reply. See [AI Chat Integration](ai-chat-integration.md).

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
[ ] docker compose exec backend python manage.py migrate --noinput
[ ] docker compose exec backend python manage.py collectstatic --noinput
[ ] docker compose exec backend python manage.py setup_periodic_tasks
[ ] docker compose exec backend python manage.py setup_ai_periodic_tasks
[ ] TLS certificates valid and auto-renewing
[ ] Database backups scheduled and tested — backend/scripts/backup_db.sh /
    restore_db.sh (restore, not just backup)
[ ] CHAT_LLM_API_KEY set to a real provider key
[ ] Emergency resources seeded for every country you expect users from
[ ] backend/scripts/smoke_test.sh BASE_URL=https://app.<domain> passes
    against the freshly deployed stack
```
