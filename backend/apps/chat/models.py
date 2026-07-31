from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class ChatSession(BaseModel):
    """
    Mirrors a LibreChat conversation. LibreChat owns the actual message
    content/streaming (its own MongoDB store); this table is the bridge
    record MindCare uses to list/search/export sessions, attribute
    sentiment analysis, and enforce that a session belongs to its user.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    librechat_conversation_id = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=255, help_text="Auto-generated from the first exchange, editable by the user.")
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "chat_sessions"
        ordering = ["-last_message_at", "-started_at"]
        indexes = [models.Index(fields=["user", "is_archived"])]

    def __str__(self):
        return f"{self.title} ({self.user_id})"


class MessageSender(models.TextChoices):
    USER = "user", "User"
    ASSISTANT = "assistant", "Assistant"


class ChatMessage(BaseModel):
    """
    Local mirror of a LibreChat message, synced via webhook/poll (Phase 6),
    kept so MindCare can run sentiment/emotion/risk analysis and full-text
    search without querying LibreChat's store on every request.
    """

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    librechat_message_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    sender = models.CharField(max_length=10, choices=MessageSender.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["session", "created_at"])]

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}"
