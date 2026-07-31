# MindCare AI

**AI-Powered Mental Health Monitoring and Support Platform**
Final-year IT project — a web platform that helps users track mood, journal,
chat with an AI companion, take validated mental-health assessments, and
receive personalized wellness recommendations, while giving administrators
tools to moderate content and monitor risk at an aggregate level.

> ⚠️ **Not a medical device.** MindCare AI does not diagnose medical or
> psychiatric conditions and is not a substitute for a licensed mental
> health professional. See [Emergency Detection & Crisis Handling](docs/architecture/emergency-detection.md).

---

## Tech Stack

| Layer          | Technology |
|----------------|------------|
| Frontend       | React 18, TypeScript, Tailwind CSS, React Router, Axios, Chart.js, Framer Motion |
| Backend        | Python, Django, Django REST Framework |
| Database       | MySQL 8 |
| Auth           | JWT (djangorestframework-simplejwt), email verification, refresh tokens |
| AI / NLP       | Hugging Face Transformers (sentiment & emotion classification), custom recommendation & risk-scoring logic |
| AI Chat        | [LibreChat](https://github.com/danny-avila/LibreChat) (self-hosted, Dockerized, SSO-bridged) |
| Async / Jobs   | Celery + Redis (reminders, AI analysis, email) |
| Docs           | drf-spectacular (OpenAPI/Swagger) |
| Deployment     | Docker, Docker Compose, Nginx reverse proxy |

---

## Repository Structure

```
mindcare-ai/
├── backend/                 Django REST Framework API
│   ├── config/               settings, urls, celery app, wsgi/asgi
│   ├── apps/
│   │   ├── users/             accounts, profiles, JWT auth, RBAC
│   │   ├── moods/              mood tracker
│   │   ├── journals/           journal entries
│   │   ├── ai_engine/          sentiment, emotion, risk, recommendation services
│   │   ├── assessments/        PHQ-9, GAD-7, stress, burnout, self-esteem
│   │   ├── recommendations/    recommendation persistence & delivery
│   │   ├── chat/               LibreChat session bridge, history, analysis
│   │   ├── appointments/       counseling session booking
│   │   ├── notifications/      in-app + email notifications, reminders
│   │   ├── resources/          articles, videos, podcasts, meditations
│   │   ├── admin_panel/        admin analytics, moderation, reports
│   │   ├── audit/               audit logging middleware & models
│   │   └── common/             shared permissions, pagination, exceptions
│   └── requirements/
├── frontend/                 React + TypeScript SPA
│   └── src/
│       ├── pages/ components/ features/ api/ hooks/ context/
│       ├── routes/ types/ utils/ styles/
├── librechat/                 LibreChat config overrides + auth-bridge scripts
├── docker/                    Dockerfiles & service configs (backend, frontend, nginx, mysql)
├── docs/                       architecture, API, database, diagrams, manuals, reports, slides
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

---

## Development Roadmap (Phases)

This project is being built in phases; each phase is completed and reviewed
before the next begins.

- [x] **Phase 1 — Folder structure & project scaffolding**
- [x] **Phase 2 — Database schema (MySQL / Django models)**
- [x] **Phase 3 — Backend (Django REST Framework APIs)**
- [x] **Phase 4 — Frontend (React + TypeScript)**
- [x] **Phase 5 — AI integration (sentiment, emotion, recommendations, risk)**
- [x] **Phase 6 — LibreChat integration (Docker + SSO bridge)**
- [x] **Phase 7 — Testing (unit, integration, API, auth, security)**
- [x] **Phase 8 — Documentation (guides, diagrams, manuals, reports)**
- [x] **Phase 9 — Docker Compose configuration**
- [x] **Phase 10 — Deployment**

---

## Getting Started

See **[docs/architecture/installation-guide.md](docs/architecture/installation-guide.md)**
for full setup instructions (Docker Compose and manual paths). Quick preview:

```bash
cp .env.example .env      # fill in real secrets
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- Swagger docs: http://localhost:8000/api/docs
- LibreChat: http://localhost:3080

For a production deployment, see the [Deployment Guide](docs/architecture/deployment-guide.md)
and copy `.env.production.example` instead of `.env.example`.

---

## CI & Operations

- **Continuous integration** — `.github/workflows/ci.yml` runs the backend
  test suite (pytest, coverage, migration-drift check), the frontend
  toolchain (typecheck, lint, unit tests, production build), and validates
  both Docker Compose files on every push/PR to `main`/`master`.
- **Operational scripts** — `backend/scripts/backup_db.sh` and
  `restore_db.sh` back up and restore the MySQL database against a running
  compose stack; `backend/scripts/smoke_test.sh` checks a deployed stack's
  health/docs/API endpoints after release.
- **[CHANGELOG.md](CHANGELOG.md)** — phase-by-phase history of what was built.

---

## Documentation

| Document | Covers |
|---|---|
| [Installation Guide](docs/architecture/installation-guide.md) | Docker & manual setup, one-time management commands, troubleshooting |
| [Docker Configuration](docs/architecture/docker-configuration.md) | Dockerfile targets, compose service breakdown, volumes, networking |
| [Deployment Guide](docs/architecture/deployment-guide.md) | Production hardening, reverse-proxy topology, secrets, release checklist |
| [Architecture Diagram](docs/architecture/architecture-diagram.md) | Component overview and layer responsibilities |
| [Sequence Diagrams](docs/architecture/sequence-diagrams.md) | Auth, journal→AI→risk, assessment crisis flag, appointment approval |
| [Flowcharts](docs/architecture/flowcharts.md) | Emergency detection, recommendation engine, wellness score computation |
| [Emergency Detection](docs/architecture/emergency-detection.md) | Crisis-detection design, ethics boundaries, what the system does and doesn't do |
| [LibreChat Integration](docs/architecture/librechat-integration.md) | OIDC SSO bridge, conversation sync, known limitations |
| [Database Schema](docs/database/schema.md) | Full ERD, table reference, normalization notes |
| [API Documentation](docs/api/README.md) | Endpoint map, auth flow, response conventions — links to live Swagger/ReDoc |
| [User Manual](docs/manuals/user-manual.md) | Feature walkthrough for end users |
| [Administrator Manual](docs/manuals/admin-manual.md) | Admin dashboard, moderation, risk alerts, seed commands |
| [Technical & Project Report](docs/reports/technical-report.md) | Objectives, design rationale, implementation summary, testing results, limitations |
| [Presentation Slides](docs/presentation/slides.md) | Marp-format defense/demo slide deck |

---

## License

Academic project — license to be finalized before any public release.
