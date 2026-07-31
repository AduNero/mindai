"""
Generates the AI companion's chat replies via an OpenAI-API-compatible
provider (default: NVIDIA NIM). Replaces the LibreChat-embedded approach
from Phase 6 — MindCare now owns the whole conversation loop directly:
persisting messages, generating replies, and running sentiment/emotion/
risk analysis on them (see apps.ai_engine), all in one place.
"""

import logging

from django.conf import settings

logger = logging.getLogger("apps")

SYSTEM_PROMPT = (
    "You are the AI companion inside MindCare AI, a mental health monitoring "
    "and support platform. Be warm, empathetic, and non-judgmental. Listen "
    "actively, validate feelings, and gently encourage healthy coping "
    "strategies. You are not a licensed therapist and cannot diagnose "
    "conditions, prescribe treatment, or provide emergency assistance — if "
    "someone appears to be in crisis or describes intent to harm themselves "
    "or others, calmly encourage them to contact a crisis line or emergency "
    "services in their area, and mention that MindCare's Emergency Resources "
    "page has local contacts. Never claim to guarantee confidentiality "
    "beyond what the platform actually provides. Keep replies concise and "
    "conversational rather than clinical."
)


class ChatServiceUnavailable(Exception):
    """Raised when the LLM provider can't be reached or isn't configured."""


def _get_client():
    from openai import OpenAI

    api_key = settings.CHAT_LLM_API_KEY
    if not api_key:
        raise ChatServiceUnavailable("CHAT_LLM_API_KEY is not configured.")
    return OpenAI(base_url=settings.CHAT_LLM_BASE_URL, api_key=api_key)


def get_chat_reply(message_history: list[dict]) -> str:
    """
    message_history: prior turns as [{"role": "user"|"assistant", "content": str}, ...],
    oldest first. Returns the assistant's reply text.
    """

    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model=settings.CHAT_LLM_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *message_history],
            temperature=0.6,
            top_p=0.95,
            max_tokens=1024,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False,
        )
    except ChatServiceUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 — any provider/network failure surfaces the same way to callers
        logger.error("Chat LLM request failed: %s", exc)
        raise ChatServiceUnavailable(str(exc)) from exc

    content = completion.choices[0].message.content
    if not content:
        raise ChatServiceUnavailable("Chat LLM returned an empty response.")
    return content
