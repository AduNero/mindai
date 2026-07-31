# MindCare AI — User Manual

Welcome! This guide walks through everything you can do as a MindCare AI
user. If you're in crisis right now, skip straight to
[Getting help in a crisis](#getting-help-in-a-crisis) at the bottom.

> **MindCare AI does not diagnose medical or psychiatric conditions and is
> not a substitute for a licensed mental health professional.** It's a
> self-monitoring and support tool.

## Getting started

### Creating an account

1. Go to the **Register** page and enter your name, email, and a password
   (at least 10 characters).
2. Check your email for a verification link and click it. You can still
   log in before verifying, but verifying keeps your account fully secure
   and enables all email notifications.
3. Log in with your email and password. Check **Remember me** if you're on
   a personal device and want to stay logged in longer.

### Forgot your password?

Use **Forgot password?** on the login page. You'll get an email with a
reset link, valid for 1 hour.

## Dashboard

Your home base after logging in. Shows:

- **Current mood** and a quick mood check-in widget
- **Mood trend** chart (toggle weekly/monthly)
- **Wellness score** — a 0-100 gauge combining your mood, journaling,
  assessments, sleep, meditation activity, and chat sentiment. It defaults
  to a neutral 60 for anything you haven't logged yet, so it's not
  penalizing you for gaps — it reflects what you've told the app.
- **Recommendations** — personalized suggestions you can mark done or dismiss

## Mood Tracker

Log how you're feeling in a few taps: pick one of 8 moods (😊 Happy, 😐
Neutral, 😢 Sad, 😡 Angry, 😰 Anxious, 😴 Tired, 😍 Excited, 😞 Depressed),
set an intensity from 1–10, and optionally add a note. You can log more
than once a day. The **History** table lets you filter by mood and see
everything you've logged, with delete available if you want to remove an entry.

## Journal

Write freely — entries are **private by default**. Each entry can have a
title, body text, an associated mood, tags, and a visibility setting
(private/public). Public entries can be seen and reported by other users
(for moderation) but MindCare never shares your private entries with
anyone.

Every entry you write is automatically analyzed for sentiment and emotion
in the background — this feeds your Wellness Score and Recommendations,
but the analysis itself isn't shown as a grade or score on the entry; it's
there to help the platform help you, not to judge your writing.

Use the search box to find past entries, and edit/delete any entry from
its detail view.

## AI Chat

Talk to the AI companion directly in the page — start a new conversation
or pick up an old one from the list on the left, search past
conversations, and **export** any conversation as a plain text file.
Every message you send is analyzed in the background for sentiment/
emotion/risk, the same as journal entries.

The AI companion is supportive, not a licensed therapist — it can't
diagnose or prescribe, and if a conversation touches on crisis, it will
point you toward the Emergency Resources page and local emergency
services rather than trying to handle that itself.

## Assessments

Standardized, validated screening questionnaires:

| Assessment | Measures |
|---|---|
| PHQ-9 | Depression symptoms |
| GAD-7 | Anxiety symptoms |
| Perceived Stress Scale | General stress |
| Burnout Assessment | Exhaustion, cynicism, reduced sense of accomplishment |
| Self-Esteem Scale | Global self-worth |

Pick one from the Assessments page, answer every question, and submit.
You'll immediately see your score, severity level, and a plain-language
interpretation — **not a diagnosis**. If your answers suggest you may be
at risk (specifically, the PHQ-9's question about thoughts of self-harm),
you'll immediately see crisis support resources for your region.

Your full history is visible below the assessment picker, so you and (if
you choose to discuss it) a counselor can see how things have trended over
time.

## Reports

- A 90-day **Wellness Score chart**.
- **Generate a report**: pick a type (daily/weekly/monthly/yearly/mental
  health summary), a format (PDF or CSV), and a date range. Reports
  summarize your mood entries, journal count, appointments, and assessment
  history for that period, and are available to download once generated
  (usually instantly).

## Appointments

Browse counselors accepting new clients, pick a date/time, and optionally
add a reason for the visit. Your request goes to **pending** until a
counselor/admin approves it. From your appointments list you can cancel
(with an optional reason) or reschedule (which creates a new appointment
linked to the original, so the history is preserved) any pending or
approved appointment.

## Resources

Browse articles, videos, podcasts, guided meditations, and breathing
exercises. Filter by type or search by keyword. The **🚨 Emergency
Resources** button is always available here — it shows crisis hotlines for
your country regardless of anything else going on.

## Settings

- **Appearance**: light, dark, or match your system.
- **Notification preferences**: toggle daily/mood/journal/meditation/
  assessment/appointment reminders individually, and whether you receive
  them by email.
- **Change password**.
- **Active sessions**: see every device currently logged in and revoke any
  you don't recognize. **Log out everywhere** immediately ends all
  sessions, useful if you think your account was accessed by someone else.

## Profile

Edit your bio, date of birth, gender, phone number, country (this drives
which emergency resources you see), timezone, and emergency contact
details. Upload a profile picture (JPEG/PNG/WebP, up to 5MB).

## Getting help in a crisis

MindCare AI is not equipped to provide emergency assistance. If you are
thinking about harming yourself or are otherwise in immediate danger:

- **Contact your local emergency services immediately.**
- Visit **Resources → 🚨 Emergency Resources** for crisis hotlines specific
  to your country.
- Reach out to a trusted friend, family member, or counselor.

If MindCare AI detects language suggesting you might be in crisis (in a
journal entry, chat message, or the PHQ-9 assessment), you'll see these
same resources immediately — this is a safety net, not a replacement for
real help. See
[docs/architecture/emergency-detection.md](../architecture/emergency-detection.md)
for exactly how this works and what it does and doesn't do.
