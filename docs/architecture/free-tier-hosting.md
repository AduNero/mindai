# Free-Tier Hosting (Render + Vercel + Upstash)

This is the **$0/month** way to put MindCare AI online, for demos and
portfolios rather than real user traffic. It's a genuinely different
deployment shape from [deployment-guide.md](deployment-guide.md) (which
covers a VPS running `docker-compose.prod.yml` as designed) — no free
platform runs a multi-service Docker Compose stack, so this path splits
the app across three free services and makes a few real compromises
along the way. Read [Limitations](#limitations) before committing to it
for anything beyond a demo.

| Piece | Service | Free tier |
|---|---|---|
| Frontend (static build) | [Vercel](https://vercel.com) | Yes, no meaningful limit for this |
| Backend (Django) | [Render](https://render.com) | Yes — spins down after 15 min idle |
| Database | Render's managed Postgres | Yes — not MySQL (see below) |
| Redis (cache + rate limiting) | [Upstash](https://upstash.com) | Yes |
| Background jobs (AI analysis, chat, email) | *(none — see below)* | Run synchronously instead |

## 1. Backend — Render

1. Push to GitHub (already done if you're reading this from the repo).
2. In the Render dashboard: **New → Blueprint**, connect this repo. Render
   reads [`render.yaml`](../../render.yaml) at the repo root automatically —
   it defines the free web service and free Postgres database, and
   generates `DJANGO_SECRET_KEY`/`JWT_SIGNING_KEY` for you.
3. Render deploys immediately, but several env vars are intentionally left
   blank (`sync: false` in `render.yaml`) since they depend on accounts
   you haven't created yet — come back and fill these in per the steps
   below: `CHAT_LLM_API_KEY`, `REDIS_URL`, `CORS_ALLOWED_ORIGINS`,
   `CSRF_TRUSTED_ORIGINS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`,
   `DEFAULT_FROM_EMAIL`.
4. **The free plan has no Shell access**, so `render.yaml`'s `startCommand`
   chains in everything installation-guide.md normally has you run by
   hand — `migrate`, `collectstatic`, all three seed commands, both
   `setup_periodic_tasks`/`setup_ai_periodic_tasks`, and
   `bootstrap_admin` (creates your login from `DJANGO_SUPERUSER_EMAIL`/
   `DJANGO_SUPERUSER_PASSWORD`, both also `sync: false` — set them in
   Settings → Environment Variables, same as the others). All of it is
   idempotent, so it's safe that this reruns on every deploy.

## 2. Redis — Upstash

1. Create a free database at [upstash.com](https://upstash.com) (any region).
2. Copy the **TLS-enabled** connection string (starts `rediss://`).
3. Back in Render: set `REDIS_URL` to that value. Same value also works
   for `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` if you ever turn real
   background workers back on — not needed while `CELERY_TASK_ALWAYS_EAGER=True`.

## 3. Frontend — Vercel

1. Import this repo in Vercel. Set **Root Directory** to `frontend` —
   Vercel auto-detects the Vite build from there.
2. Add an environment variable: `VITE_API_BASE_URL` =
   `https://mindcare-backend.onrender.com/api/v1` (swap in your actual
   Render service URL if you renamed it in `render.yaml`).
3. Deploy. `frontend/vercel.json` handles the SPA rewrite so client-side
   routes (React Router) don't 404 on refresh.

## 4. Email — Brevo (HTTP API, not SMTP)

Without this, `EMAIL_BACKEND` falls back to Django's console backend
(base.py's default) — verification and password-reset emails get
silently printed to Render's log output instead of actually being sent,
which just looks like registration is broken.

**SMTP does not work on Render's free tier — confirmed live, three
separate times**, always the same way: connecting to
`smtp.gmail.com:587` fails immediately with `OSError: [Errno 101]
Network is unreachable`. This is a platform-level network restriction,
not a credentials or config problem — Render's free-tier network simply
has no outbound route to SMTP hosts, while normal HTTPS calls (port
443) work fine. Don't spend time debugging an SMTP backend here.

Three HTTP-API backends are available in `apps/common/email_backends.py`
— which one to use depends on what you have access to:

- **No domain, default choice** (this project's case):
  `apps.common.email_backends.BrevoBackend`, what `render.yaml` is set
  up for by default. Brevo's "single sender" verification confirms one
  plain email address (click a link they email you — a Gmail address
  works fine) with no DNS/domain ownership needed, and lets that
  address send to *any* recipient.
  1. Sign up at [brevo.com](https://brevo.com) (free tier: 300
     emails/day).
  2. Settings (gear icon) → Senders, Domains & Dedicated IPs → **Senders**
     → add the email address you want to send from → click the
     verification link Brevo emails to it.
  3. Settings → SMTP & API → API Keys → **Generate a new API key**.
  4. In Render, set `BREVO_API_KEY` = that key, and `DEFAULT_FROM_EMAIL`
     = `MindCare AI <the-verified-address>` (must match the address
     verified in step 2 exactly, or Brevo rejects the send).
- **No domain, alternative**: `SendGridBackend` works the same way
  (single sender verification, `SENDGRID_API_KEY`) — but their
  free-tier signup fraud check has been known to flag and disable fresh
  accounts outright before they can even be used. Worth trying if
  Brevo's signup doesn't go through for you either, otherwise skip it.
- **Own a domain**: `ResendBackend` — Resend's sandbox mode (no domain)
  only delivers to the email on your own Resend account, rejecting
  every other recipient outright, so it needs a verified domain
  (Domains tab in Resend) to send to real users. Swap `EMAIL_BACKEND`
  to it and set `RESEND_API_KEY` instead if that fits better.

## 5. Close the loop

Back in Render, fill in the remaining env vars that needed the Vercel URL:

- `CORS_ALLOWED_ORIGINS` = `https://your-app.vercel.app`
- `CSRF_TRUSTED_ORIGINS` = `https://your-app.vercel.app`
- `CHAT_LLM_API_KEY` = your NVIDIA NIM (or other OpenAI-API-compatible
  provider) key — see [AI Chat Integration](ai-chat-integration.md)

Redeploy the backend for these to take effect. Visit the Vercel URL —
that's the live site.

## Limitations

Being upfront about what's different from a real deployment:

- **Cold starts**: Render's free web service spins down after 15 minutes
  of no traffic. The first request after that takes 30–60s while it
  wakes back up.
- **No background workers**: `CELERY_TASK_ALWAYS_EAGER=True` runs AI
  analysis, chat replies, and email dispatch synchronously inside the
  request instead of on a separate worker. Fine for demo traffic; not how
  the app is designed to behave under real load (see
  [architecture-diagram.md](architecture-diagram.md)).
- **`AI_ANALYSIS_ENABLED=False` by default**: real Hugging Face inference
  (sentiment/emotion models) is too heavy for the free tier's 512MB RAM
  running synchronously in-request. The rest of the app works normally;
  sentiment/emotion results just won't populate unless you flip this on
  and confirm it fits your plan.
- **Postgres, not MySQL**: no realistic free managed MySQL exists today,
  so this path uses `DATABASE_URL` (Postgres) instead — see
  `config/settings/base.py`. Nothing in the app is MySQL-specific beyond
  that one settings block.
- **Ephemeral filesystem**: `SERVE_MEDIA_VIA_DJANGO=True` (see
  `config/urls.py`) makes uploaded/generated files (profile pictures,
  generated reports) downloadable within a running instance's lifetime —
  without it they 404, since there's no reverse proxy here to serve
  `/media/` the way `docker/nginx/nginx.conf` does for the VPS path. They
  still don't *survive* a deploy/restart, though — Render's free tier
  filesystem resets then. Real persistence needs S3-compatible object
  storage (Cloudflare R2, Backblaze B2, etc.), which isn't wired up here.
- **Free Postgres/Redis have their own limits** (row/connection/storage
  caps) — check current limits on each provider's pricing page before
  relying on this for anything beyond a demo.

For anything beyond a demo, [deployment-guide.md](deployment-guide.md)'s
VPS + Docker Compose path is the one this project is actually designed
around.
