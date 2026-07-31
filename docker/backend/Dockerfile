# syntax=docker/dockerfile:1
#
# Two build targets:
#   base   — the Django API + Celery Beat. No AI dependencies (torch/transformers),
#            so it builds fast and stays small.
#   worker — everything in `base`, plus requirements/ai.txt. Used only by the
#            celery_worker service, which is the one that actually runs
#            apps.ai_engine's sentiment/emotion inference.
#
# REQUIREMENTS_FILE defaults to development.txt (includes test tooling);
# docker-compose.prod.yml overrides it to production.txt (leaner, no
# pytest/faker) via a build arg.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG REQUIREMENTS_FILE=requirements/development.txt
COPY requirements/ requirements/
RUN pip install -r ${REQUIREMENTS_FILE}

COPY . .
RUN mkdir -p /app/media/profile_pictures /app/staticfiles

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# --- AI-enabled worker image ---
FROM base AS worker

RUN pip install -r requirements/ai.txt

CMD ["celery", "-A", "config", "worker", "-l", "info"]
