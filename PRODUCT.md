# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary users are individuals (e.g. students/staff at an institution)
tracking their own mental wellbeing day-to-day: logging mood, journaling,
taking validated screening assessments, talking to an AI companion, and
optionally booking a counseling appointment. A secondary role
(counselors) reviews appointment requests. A third role (admins)
moderates content, reviews aggregate risk/safety flags, and manages
users, counselors, and resources.

## Product Purpose

MindCare AI is an AI-powered mental health monitoring and support
platform, built as a final-year IT project. It combines mood tracking,
journaling with automated sentiment/emotion analysis, five standardized
clinical assessments (PHQ-9, GAD-7, a Perceived Stress Scale, a Burnout
Assessment, a Self-Esteem Scale), an AI-informed recommendation engine,
an AI companion chat, and counseling appointment booking — so that small
daily signals (mood swings, disrupted sleep, withdrawal in
journaling/conversation) are tracked consistently instead of only
noticed once things are already hard to manage. Success means a user
gets an honest, interpretable picture of their own wellbeing trend and a
low-friction path to real support when they need it.

## Positioning

Most mental-health-adjacent tools are single-purpose and fragmented — a
mood tracker doesn't talk to a journaling app, which doesn't talk to a
booking system, which has no awareness of validated clinical screening
tools. MindCare AI's mechanism is combining all of it into one
interpretable signal (the Wellness Score) plus one connected workflow,
with a crisis-detection layer that surfaces localized help rather than
attempting to replace professional care.

## Operating Context

Used via a browser, desktop or mobile width. Users authenticate (JWT)
and return repeatedly over days/weeks to log data and see trends — this
is a longitudinal self-monitoring tool, not a one-off form. Counselors
and admins use dashboard-style views (queues, tables, aggregate charts)
rather than the daily-logging flows regular users use. The AI companion
chat is a real-time-feeling conversational surface (not a form).

## Capabilities and Constraints

- Explicitly **not** a diagnostic tool and **not** a substitute for a
  licensed mental health professional — this boundary must stay visible
  in the product, not buried in a footer.
- Crisis/emergency detection (PHQ-9 item 9, journal text, chat text)
  surfaces localized emergency resources; it never claims to provide
  emergency assistance itself, never guarantees confidentiality, and
  never auto-notifies third parties without consent. This is a hard
  ethical constraint on copy and flow, not just a legal disclaimer.
- Wellness Score (0–100) combines six equally-weighted components
  (mood, journal, assessment, sleep, activity, chat sentiment); missing
  data contributes a neutral baseline rather than penalizing the user.
- AI companion chat is a direct integration with an external
  OpenAI-API-compatible LLM provider (default NVIDIA NIM) — no
  streaming currently, replies return as one complete message.
- Sentiment/emotion analysis (Hugging Face Transformers) and
  lexicon-based risk scoring run asynchronously; results populate a beat
  after the triggering action (mood log, journal save, chat message),
  not synchronously.
- Roles: user, counselor, admin — meaningfully different information
  needs and UI density per role (self-tracking vs. queue/dashboard
  work).

## Brand Commitments

Name: **MindCare AI**. No other binding visual constraints — the current
indigo/blue identity is not fixed and is open to full replacement in
this redesign.

## Evidence on Hand

None (academic project — no real user testimonials, case studies,
press, or production usage data). Future work must not fabricate any of
these.

## Product Principles

1. **Never overstate capability.** No diagnostic claims, no guaranteed
   confidentiality, no implied emergency-response capability — the
   product must read as honest about what it is and isn't, everywhere,
   not just in a disclaimer.
2. **Transparency over black-box cleverness.** Where the product scores
   or flags something (wellness score components, risk detection), the
   reasoning should be legible, not mysterious — this is a stated
   engineering value carried into the interface, not just the backend.
3. **Longitudinal calm, not daily urgency.** This is a tool people
   return to over weeks; the interface should feel steady and
   non-alarming day to day, reserving visual weight for genuinely
   important moments (a crisis flag, a milestone), not routine logging.
4. **Low friction for the core loop.** Logging a mood, writing a
   journal entry, or sending a chat message is the daily core action —
   it should never feel heavier than the least important admin screen.
5. **Role-appropriate density.** Regular users get a calmer, sparser
   surface; counselors/admins get denser, queue/table-oriented views —
   the same visual system should flex to both without feeling like two
   different products.

## Accessibility & Inclusion

Design and audit against **WCAG 2.1 AA**, given this is a
mental-health-adjacent product — sufficient color contrast (including
for status/mood colors, which must not rely on hue alone), full keyboard
operability, and semantic markup are required, not optional polish.
