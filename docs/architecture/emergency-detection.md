# Emergency / Crisis Detection

## Purpose and boundaries

MindCare AI is **not a diagnostic tool, not a therapist, and not an emergency
service**. This document describes exactly what the platform does when it
detects language suggesting a user may be in crisis, and — just as
importantly — what it deliberately does **not** do.

Non-negotiable rules the implementation follows:

1. **Never claim to provide emergency assistance.** The UI always directs
   users to real emergency services or crisis lines, never implies the AI
   itself can help in a crisis.
2. **Never pretend to be a therapist or guarantee confidentiality.** Risk
   detections are visible to admins for safety review (see below) — this is
   disclosed, not hidden.
3. **Never automatically notify third parties** (family, emergency
   contacts, authorities) without the user's explicit, separate consent.
   The current implementation does not implement third-party notification
   at all — flagged content surfaces to platform admins only, who are
   bound by the same duty-of-care judgment any moderator would exercise
   with reported content.
4. **Always show localized resources.** Crisis contacts are filtered by the
   user's `Profile.country_code`, falling back to `DEFAULT_CRISIS_COUNTRY`.

## Detection sources

Three independent mechanisms feed into `apps.ai_engine.models.RiskAssessment`,
each tagged with a `detection_source` so admins can see how a flag was raised:

| Source | Mechanism | Code |
|---|---|---|
| `assessment` | PHQ-9 item 9 ("thoughts that you would be better off dead, or of hurting yourself") — **any non-zero answer** is flagged, independent of total score, following standard clinical screening practice. | `apps.assessments.views.AssessmentSubmitView._flag_crisis_risk_if_needed` |
| `journal` | Curated crisis-phrase matching against journal entry text, run asynchronously after every create/update. | `apps.ai_engine.services.risk_detection.detect_crisis_risk`, dispatched via `apps.ai_engine.tasks.analyze_content` |
| `chat` | Same phrase matching against user-authored chat messages (both locally-sent and LibreChat-synced). | Same as above, dispatched from `apps.chat.views` and `apps.chat.services.librechat_sync` |

### Why phrase-matching instead of a learned classifier

`apps.ai_engine.services.risk_detection` uses a curated, tiered phrase list
(critical / high / moderate) rather than a trained model. This is a
deliberate choice for a safety-critical signal: phrase matching is fully
auditable (an admin can see the *exact* phrase that triggered a flag),
deterministic, and doesn't carry the risk of a model silently drifting or
producing an inexplicable false negative. It's a supplementary safety net,
not the system's only line of defense — the PHQ-9 item 9 check runs
independently and doesn't depend on free-text analysis at all.

This is explicitly **not** a substitute for a validated clinical
instrument. A production deployment handling real users at scale should
pair this with professional review and a properly validated NLP model —
see the [Technical Report](../reports/technical-report.md#limitations) for
this discussed as a known limitation.

## What happens when risk is detected

1. A `RiskAssessment` row is created with `risk_level` (`moderate` /
   `high` / `critical`), the triggering phrase(s) or PHQ-9 item, and a
   `confidence_score`.
2. The user receives an **in-app notification** (never email, to avoid a
   crisis-related message landing in a possibly-shared inbox) pointing
   them to the Resources page's Emergency Resources section.
3. The frontend's assessment-results screen (for assessment-sourced flags)
   immediately displays localized crisis contacts inline — the user
   doesn't have to navigate away to see help.
4. An `AuditLog` entry (`action=risk_detected`) is written for the
   security/compliance trail.
5. The flag appears on the **Admin Dashboard → Risk Alerts** page
   (`apps.admin_panel`), where an admin can review it, add notes, and mark
   it reviewed. Reviewing is a human judgment step — the system does not
   auto-escalate.
6. If the source was a public journal entry, it's also marked
   `is_flagged=True` for moderation visibility.

## What the platform does **not** do

- It does not contact emergency services, family members, or emergency
  contacts on the user's behalf.
- It does not lock the user out of the platform or restrict their account.
- It does not present the crisis-resources message as coming from a
  licensed professional or claim any confidentiality guarantee.
- It does not use the flag to deny service, insurance-style — flags are a
  support signal, not a punitive mechanism.

## Data model

See `apps.ai_engine.models.RiskAssessment` (fields: `user`, polymorphic
`content_type`/`object_id` link to the triggering journal entry, chat
message, or assessment result; `risk_level`; `detection_source`;
`triggered_phrases`; `resources_shown_at`; `acknowledged_at`;
`reviewed_by`; `admin_notes`) and
[docs/database/schema.md](../database/schema.md) for the full schema.

## Configuration

| Setting | Purpose |
|---|---|
| `DEFAULT_CRISIS_COUNTRY` | ISO country code fallback when a user's profile has no country set, or no `EmergencyResource` rows exist for their country. |
| `apps.resources.models.EmergencyResource` | Per-country hotlines, managed by admins via `/admin-panel` → Resources, or seeded via `python manage.py seed_emergency_resources`. |
