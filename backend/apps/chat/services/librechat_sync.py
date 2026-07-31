"""
Pulls a user's conversations from LibreChat's own MongoDB store into
MindCare's ChatSession/ChatMessage tables, so the rest of the platform
(search, export, sentiment analysis, wellness score's chat component) can
work with LibreChat data the same way it works with the locally-created
messages from Phase 3's /chat/sessions/<id>/send/ endpoint.

LibreChat owns conversation storage and streaming; this is a one-directional,
read-only mirror — nothing here writes back to LibreChat's database.

User matching: MindCare's OIDC provider (apps.users.oidc) issues the `sub`
claim as `str(user.id)`. LibreChat's OpenID passport strategy stores that
claim as `openidId` on its own user document, so that field is the shared
key between the two systems — no separate mapping table needed.
"""

import logging
from datetime import timezone as dt_timezone

from django.conf import settings

logger = logging.getLogger("apps")


def _get_mongo_db():
    from pymongo import MongoClient

    client = MongoClient(settings.LIBRECHAT_MONGO_URI, serverSelectionTimeoutMS=5000)
    return client.get_default_database()


def find_librechat_user_id(mindcare_user):
    """Returns LibreChat's Mongo _id for this user (matched via OIDC `sub` == openidId), or None if they've never signed into LibreChat."""

    db = _get_mongo_db()
    doc = db.users.find_one({"openidId": str(mindcare_user.id)}, {"_id": 1})
    return doc["_id"] if doc else None


def sync_user_conversations(mindcare_user, since=None) -> int:
    """
    Upserts ChatSession/ChatMessage rows from LibreChat's Mongo store for
    `mindcare_user`, optionally limited to conversations updated since
    `since` (a timezone-aware datetime). Dispatches AI analysis
    (apps.ai_engine.tasks.analyze_content) on newly-synced user messages.
    Returns the number of conversations synced.
    """

    from apps.chat.models import ChatMessage, ChatSession, MessageSender

    librechat_user_id = find_librechat_user_id(mindcare_user)
    if not librechat_user_id:
        return 0

    db = _get_mongo_db()
    query = {"user": str(librechat_user_id)}
    if since:
        query["updatedAt"] = {"$gte": since}

    synced = 0
    for convo in db.conversations.find(query):
        conversation_id = convo["conversationId"]
        session, _ = ChatSession.objects.get_or_create(
            user=mindcare_user,
            librechat_conversation_id=conversation_id,
            defaults={"title": convo.get("title") or "New conversation"},
        )
        if convo.get("title") and convo["title"] != session.title:
            session.title = convo["title"]

        existing_message_ids = set(
            ChatMessage.objects.filter(session=session).values_list("librechat_message_id", flat=True)
        )
        new_messages = []
        latest_timestamp = session.last_message_at

        for msg in db.messages.find({"conversationId": conversation_id}).sort("createdAt", 1):
            message_id = msg["messageId"]
            if message_id in existing_message_ids:
                continue

            created_at = msg.get("createdAt") or session.started_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=dt_timezone.utc)

            new_messages.append(
                ChatMessage(
                    session=session,
                    librechat_message_id=message_id,
                    sender=MessageSender.USER if msg.get("isCreatedByUser") else MessageSender.ASSISTANT,
                    content=msg.get("text", ""),
                    created_at=created_at,
                )
            )
            if latest_timestamp is None or created_at > latest_timestamp:
                latest_timestamp = created_at

        if new_messages:
            ChatMessage.objects.bulk_create(new_messages)

            from apps.ai_engine.tasks import analyze_content

            for message in new_messages:
                if message.sender == MessageSender.USER:
                    analyze_content.delay("chat", "chatmessage", str(message.id))

        session.last_message_at = latest_timestamp
        session.save(update_fields=["title", "last_message_at"])
        synced += 1

    return synced
