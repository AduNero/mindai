# syntax=docker/dockerfile:1
#
# Single build target: Django API, Celery worker, and Celery Beat all run
# from the same image — the sentiment classifier (TF-IDF + logistic
# regression, scikit-learn) is light enough to live in requirements/base.txt,
# unlike the Hugging Face transformer pipeline it replaced.
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
