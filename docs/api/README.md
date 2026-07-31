# API Documentation

The authoritative, always-up-to-date API reference is generated directly
from the code via [drf-spectacular](https://drf-spectacular.readthedocs.io/)
and served live:

| Format | URL (local dev) |
|---|---|
| Swagger UI (interactive) | <http://localhost:8000/api/docs> |
| ReDoc | <http://localhost:8000/api/redoc> |
| Raw OpenAPI 3 schema (JSON) | <http://localhost:8000/api/schema> |

This document is a map of the API's structure and conventions — use the
live docs above for exact request/response shapes per endpoint.

## Base URL

All endpoints are versioned under `/api/v1/`. `docs/database/schema.md`
and each app's `serializers.py`/`views.py` are the ground truth for exact
field names; this is a structural overview.

## Authentication

JWT bearer tokens (`djangorestframework-simplejwt`). Obtain a token pair
via `POST /api/v1/auth/login/`, then send
`Authorization: Bearer <access_token>` on every subsequent request.
Access tokens are short-lived (`JWT_ACCESS_TOKEN_LIFETIME_MIN`, default 15
minutes); use `POST /api/v1/auth/refresh/` with the refresh token to get a
new one. See `apps.users.views` and
[sequence-diagrams.md](../architecture/sequence-diagrams.md) for the full
auth flow including account lockout, email verification, and password reset.

## Response envelope

Errors follow a consistent shape (`apps.common.exceptions.custom_exception_handler`):

```json
{
  "success": false,
  "error": {
    "code": "ValidationError",
    "message": "Human-readable summary",
    "details": { "field_name": ["Specific error."] }
  }
}
```

List endpoints are paginated (`apps.common.pagination.StandardResultsSetPagination`)
unless explicitly documented otherwise:

```json
{
  "count": 42,
  "total_pages": 3,
  "current_page": 1,
  "page_size": 20,
  "next": "http://.../?page=2",
  "previous": null,
  "results": [ ... ]
}
```

A few chart-data endpoints (mood weekly/monthly series, wellness score
history, mood predictions) are intentionally **unpaginated** — they return
a plain array, since a frontend chart needs the whole series, not one page
of it.

## Endpoint groups

| Prefix | App | Covers |
|---|---|---|
| `/auth/` | `apps.users` | Register, login, refresh, logout, email verification, password reset, sessions |
| `/users/` | `apps.users` | Profile, avatar upload, counselor directory, admin user/counselor management |
| `/moods/` | `apps.moods` | Mood entry CRUD, current/weekly/monthly series, mood choices |
| `/journals/` | `apps.journals` | Journal entry CRUD, tags, stats, moderation reports |
| `/wellness/` | `apps.wellness` | Sleep entries, meditation sessions, meditation progress |
| `/assessments/` | `apps.assessments` | Instrument list/detail, submission, results history |
| `/ai/` | `apps.ai_engine` | Sentiment/emotion analysis lookup, wellness score, mood predictions, risk assessments |
| `/recommendations/` | `apps.recommendations` | Recommendation list/update/generate, admin template management |
| `/chat/` | `apps.chat` | Session CRUD, send message (persists + generates AI reply), search, export |
| `/appointments/` | `apps.appointments` | Booking, cancel, reschedule, admin approve/reject |
| `/notifications/` | `apps.notifications` | List, unread count, mark read, preferences |
| `/resources/` | `apps.resources` | Resource browsing, categories, emergency resources, admin CRUD |
| `/admin-panel/` | `apps.admin_panel` | Dashboard stats, action logs, journal moderation, risk alerts, reports |
| `/audit/` | `apps.audit` | Security audit log (admin-only) |

## Rate limiting

Scoped throttles (`apps.common` settings, `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`)
apply to specific sensitive endpoints rather than globally:

| Scope | Applies to | Default rate |
|---|---|---|
| `auth` | Login, register, password reset, email verification | 5/min |
| `ai_analysis` | (reserved for direct AI endpoints) | 30/min |
| `report_generation` | Report generation | 10/min |

Most CRUD endpoints are not separately throttled beyond authentication —
see `apps.common.pagination`/`apps.common.permissions` for the
authorization layer that gates them instead.

## Permissions model

- **Anonymous**: public marketing content only (not part of this API — served by the frontend).
- **`IsAuthenticated`**: default for nearly everything; combined with **`IsOwner`** on
  user-scoped resources (moods, journals, appointments, chat, wellness) so users can
  only read/modify their own data.
- **`IsAdmin`**: admin-only endpoints (`/admin-panel/`, `/audit/`, user/counselor management).

See `apps.common.permissions` for the permission class implementations.
