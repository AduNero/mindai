# Installation Guide

Two paths are documented: **Docker Compose** (recommended — brings up every
service, including MySQL, Redis, Celery, and LibreChat, with one command)
and **manual setup** (for developers who want to run the Django/React
processes directly on their machine while still using Docker for just the
stateful services).

## Prerequisites

| Tool | Version | Needed for |
|---|---|---|
| Docker & Docker Compose | 24+ | Full-stack quickstart |
| Python | 3.12+ | Manual backend setup |
| Node.js | 20+ | Manual frontend setup |
| MySQL | 8.0+ | Manual setup only (Docker provides this otherwise) |
| Git | any recent | Cloning the repo |

## 1. Clone and configure

```bash
git clone <repository-url> mindcare-ai
cd mindcare-ai
cp .env.example .env
cp librechat/config/librechat.env.example librechat/config/librechat.env
```

Both files are required before `docker compose up` — `docker-compose.yml`'s
`librechat` service references `librechat/config/librechat.env` directly,
and Compose fails immediately if it's missing (this isn't optional the way
`environment:` defaults are).

Also add this line to your hosts file (`C:\Windows\System32\drivers\etc\hosts`
on Windows — needs an admin-elevated editor; `/etc/hosts` on macOS/Linux):

```
127.0.0.1  oidc-proxy
```

Required for LibreChat's SSO login redirect to work — see
[librechat-integration.md](librechat-integration.md) for why. Everything
else works without it; only the "Continue with MindCare AI" auto-login
inside LibreChat needs it.

Edit `.env` and fill in at minimum:

- `DJANGO_SECRET_KEY` — any long random string (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `MYSQL_PASSWORD` / `MYSQL_ROOT_PASSWORD`
- `JWT_SIGNING_KEY` — a separate random string from `DJANGO_SECRET_KEY`
- `OIDC_RSA_PRIVATE_KEY` — generate after the backend is up (see step 4 below); leave the placeholder for now
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — optional for local dev (falls back to `EMAIL_BACKEND=console`, which just prints emails to the terminal)

## 2. Docker Compose quickstart (recommended)

```bash
docker compose up --build
```

This starts: `backend` (Django, port 8000), `frontend` (Vite dev server,
port 5173), `db` (MySQL, port 3306), `redis` (port 6379), `celery_worker`,
`celery_beat`, `librechat` (port 3080), and `librechat_mongo`. See
[docker-compose.yml](../../docker-compose.yml) and
[Phase 9's Docker documentation](docker-configuration.md) for the full
service breakdown.

Once containers are healthy, run the one-time setup commands (migrations,
seed data, OIDC keys) inside the running `backend` container:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_assessments
docker compose exec backend python manage.py seed_recommendations
docker compose exec backend python manage.py seed_emergency_resources
docker compose exec backend python manage.py generate_oidc_rsa_key   # copy output into .env as OIDC_RSA_PRIVATE_KEY
docker compose exec backend python manage.py setup_librechat_oidc_client
docker compose exec backend python manage.py setup_periodic_tasks    # notifications app
docker compose exec backend python manage.py createsuperuser
```

After adding `OIDC_RSA_PRIVATE_KEY` to `.env`, restart the backend so it
picks up the new value:

```bash
docker compose restart backend celery_worker celery_beat
```

Visit:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000/api/v1>
- Swagger docs: <http://localhost:8000/api/docs>
- LibreChat: <http://localhost:3080>

## 3. Manual setup (backend)

Run MySQL and Redis via Docker even in manual mode, to avoid installing
them natively:

```bash
docker compose up -d db redis
```

Then, in `backend/`:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt
# Optional — only if you want real AI inference locally (large download):
# pip install -r requirements/ai.txt

python manage.py migrate
python manage.py seed_assessments
python manage.py seed_recommendations
python manage.py seed_emergency_resources
python manage.py generate_oidc_rsa_key   # paste output into .env
python manage.py setup_librechat_oidc_client
python manage.py setup_periodic_tasks
python manage.py createsuperuser
python manage.py runserver
```

In separate terminals, from `backend/` with the venv active:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

Without `requirements/ai.txt` installed, set `AI_ANALYSIS_ENABLED=False` in
`.env` — the API and all non-AI features work normally; sentiment/emotion
analysis tasks no-op gracefully (see `apps.ai_engine.services.model_loader`).

## 4. Manual setup (frontend)

```bash
cd frontend
npm install
npm run dev
```

The dev server reads `VITE_API_BASE_URL` and `VITE_LIBRECHAT_URL` from the
repo-root `.env` (see `vite.config.ts`'s `envDir`) — no separate
`frontend/.env` file needed.

## 5. LibreChat (manual setup)

LibreChat is a separate Node.js application; running it manually means
cloning it separately and pointing it at `librechat_mongo`. For local
development, it's simpler to run just that one service via Docker even in
an otherwise-manual setup:

```bash
docker compose up -d librechat_mongo librechat
```

Copy `librechat/config/librechat.env.example` to
`librechat/config/librechat.env` and fill in the values that match your
root `.env` (see the comments in that file for which vars must match
exactly) before starting the container.

## 6. Running tests

```bash
# Backend
cd backend
pip install -r requirements/development.txt
pytest                          # 200 tests, ~10s, no external services needed

# Frontend
cd frontend
npm test                        # Vitest, ~3s
npm run typecheck
npm run lint
npm run build
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `django.db.utils.OperationalError` on startup | MySQL container isn't ready yet — Django doesn't wait/retry; restart the `backend` service after `db` reports healthy. |
| OIDC discovery 500s | `OIDC_RSA_PRIVATE_KEY` not set or malformed — re-run `generate_oidc_rsa_key` and check the `\n` escaping was preserved when pasting into `.env`. |
| LibreChat shows its own login form instead of auto-redirecting | `OPENID_AUTO_REDIRECT` not set to `true` in `librechat.env`, or `OPENID_CLIENT_ID`/`SECRET` don't match what `setup_librechat_oidc_client` registered. |
| `[openidStrategy] only requests to HTTPS are allowed` in `librechat` logs | `OPENID_ISSUER` points at plain HTTP — LibreChat's OIDC client refuses that outright. The dev stack already routes this through `oidc-proxy` (a self-signed local TLS proxy); make sure `librechat` actually came up healthy and after `oidc-proxy` (`docker compose ps`), and that `OPENID_ISSUER=https://oidc-proxy/o` / `OIDC_ISS_ENDPOINT=https://oidc-proxy/o` weren't reverted to the plain-HTTP value. See [librechat-integration.md](librechat-integration.md). |
| Browser shows "server not found" / can't reach the site when LibreChat redirects for login | `oidc-proxy` is a Docker-internal DNS name — it only resolves for containers, not your browser. Add `127.0.0.1  oidc-proxy` to your hosts file (`C:\Windows\System32\drivers\etc\hosts` on Windows, `/etc/hosts` on macOS/Linux) so the browser can resolve it too. |
| `[openidStrategy] fetch failed` in `librechat` logs | `oidc-proxy` isn't reachable on port 443 from inside the `librechat` container — usually because `oidc-proxy`'s `443:443` port mapping failed to bind (something else on the host is already using port 443; check `docker compose logs oidc-proxy` for a bind error) or `OPENID_ISSUER`/`OIDC_ISS_ENDPOINT` got an explicit port added. Both must stay as plain `https://oidc-proxy/o` — see [librechat-integration.md](librechat-integration.md) for why a custom port breaks this. |
| Celery tasks never run | `celery_worker`/`celery_beat` containers not started, or `CELERY_BROKER_URL` doesn't point at the `redis` service. |
| AI analysis never populates `SentimentResult`/`EmotionResult` | `AI_ANALYSIS_ENABLED=False`, or `requirements/ai.txt` not installed in the worker — see [architecture-diagram.md](architecture-diagram.md). |
