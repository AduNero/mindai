# Docker Configuration

MindCare AI ships two Compose files and three Dockerfiles, covering both a
hot-reloading development stack and a production-oriented one.

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Development stack — source bind-mounted for hot reload, dev servers (`runserver`, Vite), MySQL/Redis ports exposed to the host for local tooling. |
| `docker-compose.prod.yml` | Production stack — baked images, Gunicorn, static frontend build served by Nginx, a reverse-proxy Nginx in front of everything. |
| `docker/backend/Dockerfile` | Two targets: `base` (Django + Celery Beat, no AI deps) and `worker` (adds `requirements/ai.txt` — used only by `celery_worker`). |
| `docker/frontend/Dockerfile` | Three targets: `development` (Vite dev server), `build` (intermediate, produces the static bundle), `production` (that bundle served by a minimal Nginx). |
| `docker/frontend/nginx.conf` | Static-file server config for the frontend's own production-target Nginx (SPA fallback routing). |
| `docker/nginx/nginx.conf` | The main reverse proxy, in front of everything in production — see [deployment-guide.md](deployment-guide.md). |

## Why the backend image is split into two targets

`requirements/ai.txt` includes PyTorch, which is a multi-hundred-MB
download and meaningfully slows every image rebuild. Only the process that
actually runs `apps.ai_engine`'s sentiment/emotion inference —
`celery_worker` — needs it. The API server (`backend`) and the scheduler
(`celery_beat`) only ever *read* AI results from the database; they never
import `transformers` themselves, so keeping them on the lighter `base`
target measurably speeds up the everyday development loop (`docker compose up --build`
without touching AI code doesn't reinstall torch).

## Why the frontend has three targets instead of two

`development` and `production` could theoretically share more, but they
have fundamentally different runtime models — one is a long-running Node
process serving live-reloaded source, the other is static files served by
Nginx with no Node runtime at all. Splitting `build` out as its own stage
(rather than folding it into `production`) is standard Docker multi-stage
practice: it lets the final `production` image contain only Nginx + the
built `dist/` folder, not the entire `node_modules` tree used to produce it.

## Networking

Both compose files rely on Docker Compose's default network — every
service can reach every other service by its service name (`db`, `redis`,
`backend`, etc.), which is why `.env.example`'s `MYSQL_HOST` and
`REDIS_URL` reference service names rather than `localhost`. No custom
network definitions were needed for this project's scale; splitting into
multiple networks (e.g. isolating the database from the reverse proxy) is
a reasonable production hardening step beyond this project's scope.

## Health checks and startup ordering

`db` and `redis` have `healthcheck` blocks; every service that depends on
them uses `depends_on: ... condition: service_healthy` rather than the
default `service_started`, so `backend`/`celery_worker`/`celery_beat`
don't attempt to connect to a MySQL server that's still initializing.

## Volumes

| Volume | Contains |
|---|---|
| `mysql_data` | MySQL's data directory — the durable system of record |
| `redis_data` | Celery broker/result backend + cache (safe to lose; nothing durable is only in Redis) |
| `media_data` | User-uploaded files (profile pictures, resource thumbnails, generated reports) |
| `static_data` | `collectstatic` output (production only — `WhiteNoise`/Nginx serve from here) |
| `frontend_node_modules` | Dev-only, keeps the container's `node_modules` from being shadowed by a bind-mounted host directory of a different OS/architecture |

## Building and running

See [installation-guide.md](installation-guide.md) for the full command
sequence (including one-time setup commands). Quick reference:

```bash
# Development
docker compose up --build
docker compose exec backend python manage.py migrate

# Production
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```
