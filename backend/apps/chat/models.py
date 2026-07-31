from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class ChatSession(BaseModel):
    """A conversation with the AI companion — see apps.chat.services.llm."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
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
    """A single turn in a ChatSession — either the user's message or the AI companion's reply."""

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=MessageSender.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["session", "created_at"])]

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}"
