# MindCare AI: An AI-Powered Mental Health Monitoring and Support Platform

### Technical & Project Report

> **A note on scope**: the original project brief asked for a separate
> "Technical Report" and "Project Report." Those two documents are
> conventionally near-duplicates (system description + methodology +
> results), so they're consolidated here into one report rather than
> padding the submission with a second document that says the same thing
> differently. If your institution requires them as physically separate
> files, this document splits cleanly at the section breaks below.

---

## Abstract

MindCare AI is a full-stack, AI-augmented mental health monitoring and
support platform built as a final-year IT project. It combines mood
tracking, journaling with automated sentiment/emotion analysis, five
standardized mental health assessments (PHQ-9, GAD-7, a Perceived Stress
Scale, a Burnout Assessment, and a Self-Esteem Scale), an AI-informed
recommendation engine, counseling appointment booking, and an AI companion
chat (any OpenAI-API-compatible provider) — all behind a role-based
(user/counselor/admin) Django REST Framework API and a React/TypeScript
frontend. The system explicitly does not diagnose medical conditions; a
phrase-based and clinically-informed crisis-detection layer surfaces
localized emergency resources rather than attempting to replace
professional care. The backend is validated by an automated test suite
(90%+ line coverage) and the frontend by additional unit tests, and key
integration points — real Hugging Face model inference and the
wellness-score computation — were verified against running processes
during development, not just reviewed as code.

## 1. Introduction

### 1.1 Problem statement

Most people don't notice a decline in their mental wellbeing until it's
already hard to manage, because the small daily signals — mood swings,
disrupted sleep, withdrawal in journaling or conversation — are easy to
miss without something tracking them consistently. Separately, when
someone does decide to seek support, the tools available are usually
fragmented: a mood-tracking app doesn't talk to a journaling app, which
doesn't talk to a counseling booking system, which doesn't have any
awareness of validated clinical screening tools.

### 1.2 Objectives

1. Provide a single platform where mood, journaling, assessments, sleep,
   and conversational data are tracked together and meaningfully combined
   into one interpretable signal (the Wellness Score).
2. Apply real NLP (Hugging Face Transformers) to journal and chat content
   to surface sentiment, emotional tone, and stress/anxiety/burnout/
   depression indicators — augmented, not replaced, by an explainable
   rule-based layer.
3. Detect crisis-indicating language and respond appropriately: show
   localized help, never claim therapeutic authority, and never
   auto-notify third parties.
4. Connect self-monitoring to professional support via in-platform
   counseling appointment booking.
5. Give administrators the tools to moderate content, review safety
   flags, and manage the platform's people (users, counselors) and content
   (resources) responsibly.
6. Build all of the above to a standard defensible as production-quality
   software: tested, documented, containerized, and secure by design —
   not just a working demo.

### 1.3 Non-goals

MindCare AI does not diagnose medical or psychiatric conditions, does not
claim clinical validation for its own original assessment instruments
(only PHQ-9 and GAD-7 use their real published items and cut-offs), and
does not replace licensed mental health professionals. These boundaries
are enforced in the product (disclaimers, non-diagnostic language) and in
engineering decisions (see §6.4).

## 2. Technology choices and justification

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS | Strong typing catches integration bugs at compile time (see §7); Tailwind keeps the dark/light mode and responsive design consistent without a component library dependency. |
| Backend | Django + Django REST Framework | Batteries-included ORM/migrations/admin reduce boilerplate; DRF's serializer/permission/throttle system maps cleanly onto the role-based access control this project needs. |
| Database | MySQL 8 | Explicitly required by the project brief; UUID primary keys throughout avoid exposing sequential IDs for sensitive records. |
| Auth | JWT (`djangorestframework-simplejwt`) | Stateless bearer-token auth for the SPA; account lockout, refresh rotation, and session tracking layered on top (see §5.3). |
| AI/NLP | Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`, `SamLowe/roberta-base-go_emotions`) | Both are widely-used, well-documented, CPU-runnable models. GoEmotions was specifically chosen because its 28 fine-grained labels are a superset of the 8 emotions this project's spec requires (joy, fear, sadness, anger, love, surprise, optimism, disappointment) — rather than forcing an unrelated model's labels to fit, or fabricating a mapping. |
| Async jobs | Celery + Redis | AI inference and email are too slow for the request/response cycle; Celery Beat drives scheduled reminders and the daily wellness-score/mood-prediction sweep. |
| Chat | Direct integration with any OpenAI-API-compatible provider (`openai` Python client; default NVIDIA NIM) | The conversation loop — storage, history, search, export, analysis — lives entirely in MindCare's own Django app and MySQL; only reply generation is delegated to an external provider via one API call per message. No second chat service, database, or SSO surface to operate. |
| Deployment | Docker Compose | Matches the brief; makes the whole multi-service stack (MySQL, Redis, Celery, Nginx) reproducible with one command. |

## 3. System architecture

See [docs/architecture/architecture-diagram.md](../architecture/architecture-diagram.md)
for the full component diagram. In summary: a React SPA talks to a Django
REST API over JWT; Celery workers handle AI inference and scheduled jobs;
MySQL is the system of record for everything, including chat history —
the AI companion's replies are generated via one API call to an external
LLM provider and stored like any other message.

## 4. Database design

30+ normalized tables across 14 Django apps, using UUID primary keys
throughout. Full ERD, table reference, and normalization rationale:
[docs/database/schema.md](../database/schema.md). Key design decisions:

- **Polymorphic AI results** (`SentimentResult`, `EmotionResult`) use
  Django's `ContentType` framework to attach to either journal entries or
  chat messages without the AI app depending on either directly.
- **`WellnessScoreSnapshot` stores computed values**, not just formulas —
  a deliberate denormalization, because a historical wellness score is a
  fact about a point in time, and recomputing history retroactively every
  time an input changes would both be expensive and falsify the record.
- **`AuditLog` and `AdminActionLog` are kept separate** — one is the
  security-team-facing system-wide trail, the other is the
  business-facing record of moderation decisions shown in the admin UI.

## 5. Implementation summary

The project was built in ten phases; each is summarized here with what
was actually delivered (not just planned).

### 5.1 Backend (Django REST Framework)

Fourteen apps covering auth, mood tracking, journaling, wellness (sleep/
meditation), assessments, the AI engine, recommendations, chat,
appointments, notifications, resources, admin tooling, and audit logging.
Every endpoint enforces authentication and, where applicable, ownership
(`IsOwner`) or role (`IsAdmin`) permissions. Sensitive endpoints (login,
registration, password reset, report generation) are separately rate-limited.

### 5.2 Frontend (React + TypeScript)

~90 source files covering every page in the brief — 6 marketing pages, 5
auth pages, 10 authenticated app pages, 9 admin pages, and a 404 page —
with a shared design system (dark/light mode via a `ThemeContext`, a
reusable component library, Chart.js visualizations for mood trends and
the wellness score). Route-level code-splitting (`React.lazy`) keeps the
production bundle's largest chunk under 175KB after an initial
single-bundle build exceeded 600KB.

### 5.3 AI integration

Three layers, deliberately separated by what each is good at:

1. **Learned models** (Hugging Face) for sentiment and emotion
   classification — genuinely trained on real data, not heuristics.
2. **A transparent lexicon/rule layer** for stress/anxiety/burnout/
   depression indicator scores and crisis-phrase detection — chosen over a
   second learned model specifically *because* these are safety-adjacent
   signals where auditability (an admin can see exactly which word or
   phrase triggered a flag) matters more than marginal recall from a
   black-box classifier.
3. **Classical statistics** (ordinary least-squares trend extrapolation)
   for next-day mood prediction — appropriate given the small
   per-user sample sizes involved, where a learned model would overfit noise.

### 5.4 AI chat integration

The chat companion is implemented directly in `apps.chat` rather than by
embedding a separate chat application: a message is persisted, the full
session history plus a fixed system prompt is sent to whichever
OpenAI-API-compatible provider is configured (`CHAT_LLM_*` settings —
NVIDIA NIM by default), and the reply is persisted and returned in the
same response. If the provider is unreachable, the user's message is
still saved rather than the whole request failing. Full detail:
[docs/architecture/ai-chat-integration.md](../architecture/ai-chat-integration.md).

An earlier iteration of this project embedded LibreChat (a separate
self-hosted chat application) via an OpenID Connect SSO bridge and a
one-directional MongoDB sync into MindCare's own tables. That was later
replaced with the direct integration described above — it removed a
second Docker service, a second database, and an SSO/cookie-bridge
surface area, in exchange for a simpler (non-pluggable-UI) chat
experience.

## 6. Testing

An automated test suite covering both backend (pytest-django, 90%+ line
coverage) and frontend (Vitest). Coverage spans unit tests (scoring
algorithms, lexicon scoring, crisis detection, wellness-score math,
recommendation matching), API/integration tests (CRUD plus cross-user
ownership isolation for every user-scoped resource), authentication tests
(registration through account lockout and password reset), and security
tests (rate limiting, IDOR sweeps, JWT tampering, file upload validation).

### 6.1 What running the suite actually found

Five real bugs surfaced by running tests, not by review:

1. An admin report-listing endpoint was missing `serializer_class` and
   would have crashed on `GET`.
2. Logging two sleep entries on the same day crashed with an unhandled
   database `IntegrityError` instead of a clean validation error — DRF
   can't auto-generate a uniqueness validator for a field
   (`user`) that isn't exposed on the serializer.
3. A test-isolation bug in the test suite itself: DRF's rate-limit
   counters live in Django's cache, which — unlike the database — isn't
   rolled back between tests, so one test's requests were silently
   exhausting a later test's rate-limit budget.
4. A missing `.order_by()` surfaced as a pagination-consistency warning.
5. Two further bugs were in the tests, not the app (a fixture ID collision, a UUID/string
   comparison) — distinguishing these from real bugs before "fixing" the
   wrong thing was itself part of the exercise.

### 6.2 What was verified against running processes, not just written

- Real Hugging Face model downloads and inference (both sentiment and
  emotion models), confirmed against hand-checked expected outputs.
- A real chat completion round-trip against the configured LLM provider,
  confirming the reply is persisted and returned in the same response
  shape the frontend expects.
- Wellness-score arithmetic, hand-verified against the live API response
  for a specific mood+sleep input.
- Django's `makemigrations --check` (no drift) and full `migrate` against
  a real database after every schema-touching phase.

## 7. Security

- Password hashing via Django's default (PBKDF2); JWT access/refresh with
  rotation and blacklisting on logout/password reset.
- Account lockout after repeated failed logins, layered with endpoint-level
  rate limiting.
- UUID primary keys platform-wide to avoid enumerable sequential IDs on
  sensitive records.
- Role-based access control (`IsOwner`, `IsAdmin`) enforced at the view
  layer, verified by dedicated permission tests, not just assumed correct.
- File upload validation (content-type allowlist, size limit) for profile
  pictures and resource thumbnails.
- A structured, append-only audit log for authentication events,
  permission denials, and crisis-detection triggers.
- CORS restricted to an explicit origin allowlist (never a wildcard);
  credentials are disabled entirely, since every endpoint is bearer-token
  (JWT) auth and none of them rely on cookies.

## 8. Limitations and future work

- The stress/anxiety/burnout/depression lexicon is a transparent heuristic,
  not a clinically validated instrument — a production deployment serving
  real users at scale should pair it with a validated model and
  professional review (see [emergency-detection.md](../architecture/emergency-detection.md)).
- Crisis detection is phrase-based and will miss paraphrased or
  non-English crisis language; it is explicitly one layer of defense, not
  the only one.
- The recommendation engine's AI-informed tier depends on recent journal
  sentiment data existing — a new user with no journal history falls back
  to the mood-only tier, by design, but this means personalization ramps
  up over the first few days of use rather than being immediate.
- The AI companion chat has no streaming — replies come back as one
  complete response rather than token-by-token, which is simpler but
  means the user waits for the full generation before seeing anything.
- Real-time features (e.g., live notification push) use polling rather
  than WebSockets — a reasonable scope trade-off for this project, but a
  natural extension.

## 9. Conclusion

MindCare AI demonstrates that a mental-health-adjacent platform can
combine real machine learning, transparent rule-based safety logic, and an
external AI provider integration into a single coherent, tested, and
documented product — while being explicit throughout about what it is not
(a diagnostic tool or a replacement for professional care).
The emphasis throughout development was on verifying claims against
running systems rather than assuming correctness from code review alone,
which is reflected in the testing methodology (§6) and is, in the
author's view, the most transferable lesson from the project.

## References

- Kroenke, K., Spitzer, R.L., & Williams, J.B. (2001). The PHQ-9: validity
  of a brief depression severity measure. *Journal of General Internal
  Medicine*.
- Spitzer, R.L., Kroenke, K., Williams, J.B., & Löwe, B. (2006). A brief
  measure for assessing generalized anxiety disorder: the GAD-7. *Archives
  of Internal Medicine*.
- Cohen, S., Kamarck, T., & Mermelstein, R. (1983). A global measure of
  perceived stress. *Journal of Health and Social Behavior*.
- Rosenberg, M. (1965). *Society and the Adolescent Self-Image*. Princeton
  University Press. (Self-Esteem Scale basis.)
- Demszky, D. et al. (2020). GoEmotions: A Dataset of Fine-Grained
  Emotions. *ACL*. (`SamLowe/roberta-base-go_emotions` training data.)
- Django REST Framework, React, Celery, and Hugging Face Transformers
  project documentation (see each tool's official docs for
  version-specific API references used throughout this codebase).
