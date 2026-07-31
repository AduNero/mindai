# System Architecture

## Component overview

```mermaid
graph TB
    subgraph Client["Client (Browser)"]
        SPA["React SPA\n(Vite, TypeScript, Tailwind)"]
    end

    subgraph Edge["Reverse Proxy (Nginx, production)"]
        NGINX["Nginx\nTLS termination, routing"]
    end

    subgraph App["Application Tier"]
        DJANGO["Django REST Framework API\n(Gunicorn/WSGI)"]
        OIDC["OIDC Provider\n(django-oauth-toolkit)"]
        CELERY["Celery Workers\n(AI analysis, email, sync)"]
        BEAT["Celery Beat\n(scheduled tasks)"]
    end

    subgraph AI["AI Layer"]
        HF["Hugging Face Transformers\nSentiment + Emotion models"]
        LEXICON["Lexicon / Rule Engine\n(stress, anxiety, risk, recommendations)"]
    end

    subgraph Chat["LibreChat"]
        LIBRECHAT["LibreChat App\n(Node.js)"]
        LCMONGO[("LibreChat MongoDB")]
    end

    subgraph Data["Data Tier"]
        MYSQL[("MySQL 8\nPrimary datastore")]
        REDIS[("Redis\nCache + Celery broker")]
    end

    SPA -->|"HTTPS / REST + JWT"| NGINX
    SPA -->|"iframe (embedded)"| NGINX
    NGINX --> DJANGO
    NGINX --> LIBRECHAT

    DJANGO --> MYSQL
    DJANGO --> REDIS
    DJANGO --> OIDC
    OIDC -->|"SSO: authorize/token"| LIBRECHAT

    CELERY --> MYSQL
    CELERY --> REDIS
    CELERY --> HF
    CELERY --> LEXICON
    CELERY -->|"read-only Mongo sync"| LCMONGO
    BEAT --> REDIS

    LIBRECHAT --> LCMONGO
    LIBRECHAT -->|"model provider API\n(OpenAI/Anthropic/etc.)"| EXTERNAL(["External LLM Provider"])

    style SPA fill:#4f5fee,color:#fff
    style DJANGO fill:#2c2f84,color:#fff
    style LIBRECHAT fill:#10b981,color:#fff
    style MYSQL fill:#f59e0b,color:#000
    style LCMONGO fill:#f59e0b,color:#000
    style REDIS fill:#ef4444,color:#fff
```

## Layer responsibilities

| Layer | Technology | Responsibility |
|---|---|---|
| Client | React 18 + TypeScript + Tailwind | SPA UI, JWT storage, chart rendering, dark/light mode |
| Reverse proxy | Nginx | TLS termination, routes `/api/*` and `/o/*` to Django, `/` to the frontend static build, `/ai-chat/*` to LibreChat (production same-domain setup — see [librechat-integration.md](librechat-integration.md)) |
| Application | Django REST Framework | Business logic, auth (JWT + OIDC), permissions, serialization |
| AI layer | Hugging Face Transformers + rule-based services | Sentiment/emotion classification, lexicon-based construct scoring, crisis-phrase detection, wellness score computation, trend prediction |
| Async | Celery + Redis | AI analysis dispatch, email delivery, LibreChat conversation sync, scheduled reminders and daily sweeps |
| Chat | LibreChat (Node.js) + its own MongoDB | Conversational AI UI and LLM orchestration; MindCare mirrors its data one-directionally (read-only) |
| Data | MySQL 8 | System of record for all MindCare domain data (30+ normalized tables — see [docs/database/schema.md](../database/schema.md)) |
| Cache/Queue | Redis | DRF throttle counters, Celery broker/result backend |

## Why these boundaries

- **LibreChat is not forked or modified.** MindCare treats it as an external system integrated via two narrow, well-defined interfaces: OIDC (for auth) and a read-only MongoDB sync (for conversation history). This keeps LibreChat upgradable independently of MindCare's codebase.
- **AI inference is isolated in Celery workers**, not the request/response cycle — sentiment/emotion analysis and model loading are too slow to run synchronously in an API view. `AI_ANALYSIS_ENABLED=False` lets the API run entirely without the AI dependency stack installed (see `apps.ai_engine.services.model_loader`).
- **MySQL is the single source of truth** for everything except live chat content, which is why chat messages are *mirrored* into MySQL (for search/export/analysis) rather than MindCare depending on LibreChat's Mongo store at request time.
