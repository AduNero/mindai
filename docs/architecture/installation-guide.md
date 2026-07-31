# Installation Guide

Two paths are documented: **Docker Compose** (recommended — brings up every
service, including MySQL, Redis, and Celery, with one command) and
**manual setup** (for developers who want to run the Django/React
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
```

Edit `.env` and fill in at minimum:

- `DJANGO_SECRET_KEY` — any long random string (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `MYSQL_PASSWORD` / `MYSQL_ROOT_PASSWORD`
- `JWT_SIGNING_KEY` — a separate random string from `DJANGO_SECRET_KEY`
- `CHAT_LLM_API_KEY` — an API key from an OpenAI-API-compatible provider (default config points at [NVIDIA NIM](https://build.nvidia.com), which has a free tier) — see [AI Chat Integration](ai-chat-integration.md). Without this, everything else works; the chat companion just returns an error instead of a reply.
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — optional for local dev (falls back to `EMAIL_BACKEND=console`, which just prints emails to the terminal)

## 2. Docker Compose quickstart (recommended)

```bash
docker compose up --build
```

This starts: `backend` (Django, port 8000), `frontend` (Vite dev server,
port 5173), `db` (MySQL, port 3306), `redis` (port 6379), `celery_worker`,
and `celery_beat`. See [docker-compose.yml](../../docker-compose.yml) and
[Docker documentation](docker-configuration.md) for the full service
breakdown.

Once containers are healthy, run the one-time setup commands (migrations,
seed data) inside the running `backend` container:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_assessments
docker compose exec backend python manage.py seed_recommendations
docker compose exec backend python manage.py seed_emergency_resources
docker compose exec backend python manage.py setup_periodic_tasks     # notifications app
docker compose exec backend python manage.py setup_ai_periodic_tasks  # ai_engine app
docker compose exec backend python manage.py createsuperuser
```

Visit:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000/api/v1>
- Swagger docs: <http://localhost:8000/api/docs>

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
python manage.py setup_periodic_tasks       # notifications app
python manage.py setup_ai_periodic_tasks    # ai_engine app
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

The dev server reads `VITE_API_BASE_URL` from the repo-root `.env` (see
`vite.config.ts`'s `envDir`) — no separate `frontend/.env` file needed.

## 5. Running tests

```bash
# Backend
cd backend
pip install -r requirements/development.txt
pytest                          # ~10s, no external services needed

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
| Chat companion always replies with an error | `CHAT_LLM_API_KEY` isn't set, is invalid, or `CHAT_LLM_BASE_URL`/`CHAT_LLM_MODEL` don't match what the provider actually serves — check `celery_worker`/`backend` logs for the underlying provider error. See [AI Chat Integration](ai-chat-integration.md). |
| Celery tasks never run | `celery_worker`/`celery_beat` containers not started, or `CELERY_BROKER_URL` doesn't point at the `redis` service. |
| AI analysis never populates `SentimentResult`/`EmotionResult` | `AI_ANALYSIS_ENABLED=False`, or `requirements/ai.txt` not installed in the worker — see [architecture-diagram.md](architecture-diagram.md). |
