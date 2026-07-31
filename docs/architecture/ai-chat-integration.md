# AI Chat Integration

MindCare AI's chat companion is implemented directly in the Django backend
(`apps.chat`) — there is no separate chat service to deploy or keep in sync.
The frontend talks only to MindCare's own API; MindCare's API talks to
whichever LLM provider is configured.

## 1. Request flow

1. The user sends a message: `POST /api/v1/chat/sessions/:id/send/`.
2. `ChatSessionViewSet.send` (`apps/chat/views.py`) persists the message as
   a `ChatMessage` (`sender=user`), auto-titles the session on its first
   message, and dispatches `apps.ai_engine.tasks.analyze_content` (async,
   via Celery) to run sentiment/emotion/risk analysis on it — unchanged
   from how journal entries are analyzed.
3. It then builds the full message history for the session and calls
   `apps.chat.services.llm.get_chat_reply`, which sends it (prefixed with a
   fixed system prompt) to the configured LLM provider via the `openai`
   Python client and returns the reply text.
4. The reply is persisted as a second `ChatMessage` (`sender=assistant`)
   and both messages are returned in one response:
   `{"user_message": {...}, "assistant_message": {...} | null, "error"?: string}`.

If the LLM provider is unreachable or misconfigured, the user's message is
still saved — `assistant_message` comes back `null` with an `error` string
instead of the whole request failing, so nothing the user typed is lost.

## 2. Provider configuration

Any OpenAI-API-compatible provider works — set these three variables
(`.env` / `.env.production.example`):

| Variable | Default | Notes |
|---|---|---|
| `CHAT_LLM_API_KEY` | *(empty — required)* | Provider API key. |
| `CHAT_LLM_BASE_URL` | `https://integrate.api.nvidia.com/v1` | [NVIDIA NIM](https://build.nvidia.com) by default; point this at OpenAI, OpenRouter, a self-hosted vLLM/Ollama endpoint, etc. |
| `CHAT_LLM_MODEL` | `nvidia/llama-3.3-nemotron-super-49b-v1` | Any model id the provider serves. |

No provider-specific code exists anywhere else — swapping providers is a
config change, not a code change.

## 3. System prompt

`apps.chat.services.llm.SYSTEM_PROMPT` frames the assistant consistently
with this project's stated ethical constraints (see
[Emergency Detection](emergency-detection.md)): supportive and empathetic,
explicitly not a licensed therapist, cannot diagnose or prescribe, and
directs anyone describing a crisis toward the Emergency Resources page and
local emergency services rather than claiming to help directly. It's
prepended to every request — there is no way to override it per-request
from the client.

## 4. What changed from the LibreChat-based design

Earlier phases of this project embedded [LibreChat](https://github.com/danny-avila/LibreChat)
(a full self-hosted chat UI) in an iframe, bridged via OpenID Connect SSO
so a MindCare login carried over automatically. That added real
operational weight for comparatively little benefit here — a second
Docker service, a MongoDB instance, an OIDC identity-provider role for the
Django backend, and (in local dev) a self-signed TLS proxy purely to
satisfy LibreChat's OIDC client's HTTPS requirement. It's been replaced
with the direct integration described above: one fewer service to run,
one fewer database, no SSO/cookie-bridge surface area, and MindCare owns
the full conversation loop (including analysis) directly rather than
mirroring it from an external store.

The trade-off: MindCare's chat UI (`frontend/src/pages/app/AIChatPage.tsx`)
is simpler than LibreChat's — no file uploads, plugins, or multi-provider
picker in the UI itself (multi-provider is still possible by pointing
`CHAT_LLM_BASE_URL` at a router like OpenRouter, just not selectable
per-message in the UI).
