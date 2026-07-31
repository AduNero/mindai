# MindCare AI — Administrator Manual

This guide covers the Admin Dashboard, available to accounts with
`role=admin`. Promote a user to admin via Django admin (`is_staff` +
`is_superuser`, or set `role=admin` directly) or
`User.objects.create_superuser(...)` — there's no self-service path to
become an admin, by design.

## Overview

`/admin` shows platform-wide statistics at a glance: total users, active
users (last 30 days), high-risk users (unacknowledged high/critical risk
flags), total assessments taken, appointments (with pending count), AI
chat sessions/messages, and mood/journal activity in the last 30 days.
Use this as your first stop to spot anything that needs attention.

## Users

`/admin/users` lists every account with search (name/email) and the
ability to **suspend** (`is_active=False`) or **reactivate** any user.
Suspending immediately blocks login without deleting any of the user's
data. Role changes beyond suspension (e.g., promoting to counselor) happen
via the Counselors page, not here — this keeps counselor promotion
auditable with its own dedicated flow.

## Journal Moderation

`/admin/journal-reports` shows reports filed against **public** journal
entries — either by other users, or automatically when the AI risk
detector flags content. Filter by status (pending/reviewed/actioned/
dismissed). For each pending report you can:

- **Take down entry** — marks the entry private and resolves the report as `actioned`.
- **Mark reviewed** — resolves without changing the entry's visibility.
- **Dismiss** — resolves the report as not actionable.

All three record review notes and who reviewed it
(`apps.journals.JournalReport.reviewed_by`/`reviewed_at`).

## Risk Alerts

`/admin/risk-alerts` is the most safety-critical page in the admin panel —
review it regularly. It lists every `RiskAssessment`: the risk level
(moderate/high/critical), where it came from (assessment/journal/chat),
the exact triggered phrase(s) for full auditability, when it was created,
and whether the *user* has acknowledged seeing crisis resources.

**What "Mark reviewed" does and doesn't do**: it records that an admin has
seen the flag and adds it to the audit trail. It does **not** contact the
user, their emergency contact, or any authority — MindCare AI never
auto-notifies third parties (see
[docs/architecture/emergency-detection.md](../architecture/emergency-detection.md)).
If your organization has a duty-of-care process for handling these flags
(e.g., a counselor follow-up), that happens outside this system, using the
information here as your starting point.

## Counselors

`/admin/counselors` is where you promote an existing user to the
counselor role — enter their name, specialization, and bio. This
immediately creates their `CounselorProfile` and makes them visible to
users booking appointments. Toggle **Accepting/Paused** on any counselor
to control whether new bookings can be made with them, without removing
their history.

## Appointments

`/admin/appointments` lists booking requests, filterable by status.
**Approve** or **Reject** pending requests; both actions are logged
(`AdminActionLog`) and visible to the user in their own Appointments page.

## Resources

`/admin/resources` manages the Resource Center's content: create articles
(with a body), or videos/podcasts/meditations/breathing exercises (with an
external URL), toggle published/draft, and delete. The same page manages
**Emergency Resources** (crisis hotlines) — add a country code, name, and
phone number; these appear to users in that country automatically (see
`DEFAULT_CRISIS_COUNTRY` for the fallback when a user's country isn't set
or has no entries yet — seed a reasonable set of countries before launch
via `python manage.py seed_emergency_resources`, then add more as needed).

## Reports

`/admin/reports` generates the same report types available to regular
users, scoped to your own admin account's data. For platform-wide
analytics beyond the Overview page's summary stats, query the database
directly or extend `apps.admin_panel.report_generation` — this is called
out explicitly in the UI copy so it isn't mistaken for an
all-users export.

## Audit Logs

`/admin/audit-logs` is the read-only security trail: logins (success and
failure), password changes/resets, email verification, profile updates,
permission denials, and crisis-detection triggers — each with the acting
user (if any), IP address, and timestamp. Filter by action type. This is
your primary tool for investigating a suspected account compromise or
demonstrating compliance/audit readiness.

## Seed data & one-time setup commands

These are typically run once per environment (see
[installation-guide.md](../architecture/installation-guide.md) for the
full sequence), not from the UI:

```bash
python manage.py seed_assessments          # PHQ-9, GAD-7, Stress, Burnout, Self-esteem question banks
python manage.py seed_recommendations       # Starter recommendation template catalogue
python manage.py seed_emergency_resources   # Starter crisis hotline set (extend via the UI)
python manage.py setup_periodic_tasks       # notifications app
python manage.py setup_ai_periodic_tasks    # ai_engine app
```
