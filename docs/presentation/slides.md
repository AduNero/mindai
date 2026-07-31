---
marp: true
title: MindCare AI — Project Defense
theme: default
paginate: true
---

<!--
This file is written in Marp markdown — each "---" is a new slide.
Render to PDF/PPTX with the Marp CLI (`npx @marp-team/marp-cli slides.md -o slides.pptx`),
the Marp VS Code extension, or just copy each slide's content into
PowerPoint/Google Slides manually — the structure below is deliberately
one-idea-per-slide so that copy works directly.
-->

# MindCare AI
### AI-Powered Mental Health Monitoring and Support Platform

Final-Year IT Project
[Your Name] · [Your Institution] · [Date]

---

## The Problem

- Mental wellbeing declines are usually noticed **after** they're already hard to manage
- The early signals — mood, sleep, journaling, withdrawal — are scattered across apps that don't talk to each other
- Getting from "I should check in with myself" to "I'm talking to a counselor" has too much friction

---

## Objectives

1. One platform: mood, journaling, assessments, sleep, and chat — tracked together
2. Real NLP analysis of journal/chat content, not just self-reported numbers
3. Responsible crisis detection: help, not diagnosis
4. A direct path from self-monitoring to booking a counselor
5. Admin tooling for moderation and safety review
6. Built and **tested** to production-quality standards, not just a demo

---

## What MindCare AI Is Not

- ❌ Not a diagnostic tool
- ❌ Not a replacement for a licensed mental health professional
- ❌ Not an emergency service
- ✅ A self-monitoring and support companion, with clear guardrails

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS |
| Backend | Django REST Framework |
| Database | MySQL 8 |
| AI/NLP | Hugging Face Transformers |
| Chat | LibreChat (SSO-integrated) |
| Async | Celery + Redis |
| Deployment | Docker Compose |

---

## System Architecture

SPA → Django API → MySQL/Redis, with Celery workers handling AI inference
and async jobs, and LibreChat integrated via OIDC (auth) + a
one-directional MongoDB sync (conversation history).

*(Paste the Mermaid diagram from `docs/architecture/architecture-diagram.md`
here — most slide tools with a Mermaid plugin, or mermaid.live for a static export, render it directly.)*

---

## Database Design

- 30+ normalized tables across 14 Django apps
- UUID primary keys throughout — no enumerable sequential IDs on sensitive records
- Polymorphic AI results (via ContentType) attach to journal entries *or* chat messages
- Wellness score stored as historical snapshots, not recomputed retroactively

---

## Core Feature: Mood & Journal Tracking

- 8 moods × intensity (1–10) × notes, with weekly/monthly trend charts
- Journal entries: private by default, taggable, searchable
- Every journal entry automatically analyzed for sentiment & emotion — asynchronously, via Celery

---

## Core Feature: Mental Health Assessments

- PHQ-9 (depression) and GAD-7 (anxiety) — **real published items and severity cut-offs**
- Stress, Burnout, and Self-Esteem scales — original items, generic severity banding
- PHQ-9 item 9 (self-harm ideation) triggers an immediate, independent crisis-resource response

---

## The AI Engine — Three Layers

1. **Learned models** (Hugging Face): sentiment (DistilBERT) + emotion (GoEmotions, filtered to 8 tracked emotions)
2. **Transparent lexicon layer**: stress/anxiety/burnout/depression scores, crisis-phrase detection — auditable by design
3. **Classical statistics**: linear trend extrapolation for next-day mood prediction

*Why not one model for everything? Safety-adjacent signals need to be explainable — an admin can see exactly which phrase triggered a flag.*

---

## Wellness Score

- 0–100, six equally-weighted components: mood, journal, assessment, sleep, activity, chat sentiment
- Missing data → neutral baseline (60), never penalized
- Recomputed automatically whenever any input changes

---

## LibreChat Integration

- MindCare's backend **is** LibreChat's OpenID Connect identity provider
- Log in once → the embedded chat is already authenticated, no second login
- One-directional MongoDB sync mirrors LibreChat conversations into MindCare for search, export, and AI analysis
- Verified end-to-end: real authorization code delivered to LibreChat's callback URL

---

## Emergency Detection

- Three independent sources: PHQ-9 item 9, journal text, chat text
- On detection: in-app notification with localized crisis resources, audit log entry, admin dashboard visibility
- **Never** auto-contacts third parties — human judgment only

---

## Security

- JWT auth with rotation/blacklisting + account lockout + rate limiting
- Role-based access control (user / counselor / admin), enforced and *tested*
- UUID primary keys, file upload validation, structured audit logging
- CORS locked to an explicit origin allowlist

---

## Testing — By the Numbers

- **220 automated tests**: 200 backend (pytest), 20 frontend (Vitest)
- **86% backend line coverage**
- Real Hugging Face inference verified against actual model downloads
- Full OIDC SSO flow verified end-to-end against a running server
- 5 real bugs caught and fixed *by running tests*, not just by writing them

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| GoEmotions' 28 labels vs. the spec's 8 emotions | Chose a model whose labels are a superset, filtered + renormalized |
| Iframe SSO + browser third-party cookie restrictions | Documented limitation; same-domain reverse-proxy in production |
| DRF couldn't auto-validate a uniqueness constraint | Explicit check at the view layer, caught by testing |
| Rate-limit state leaking between tests | Cache-clearing autouse fixture |

---

## Limitations & Future Work

- Lexicon-based scoring is transparent but not clinically validated
- Crisis detection is phrase-based — one layer of defense, not the only one
- Real-time features use polling, not WebSockets
- Natural extensions: validated clinical NLP model, push notifications, mobile app

---

## Conclusion

MindCare AI shows that real machine learning, transparent safety logic,
and a genuine third-party integration can come together in one tested,
documented platform — while being explicit about what it doesn't claim to
be. The emphasis throughout was **verifying against running systems**,
not just writing code and assuming it works.

---

# Thank You
## Questions?
