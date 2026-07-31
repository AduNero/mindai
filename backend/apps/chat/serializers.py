from rest_framework import serializers

from .models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = ChatSession
        fields = [
            "id", "title", "started_at", "last_message_at",
            "is_archived", "message_count",
        ]
        read_only_fields = ["id", "started_at", "last_message_at", "message_count"]


class ChatSessionDetailSerializer(ChatSessionSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta(ChatSessionSerializer.Meta):
        fields = ChatSessionSerializer.Meta.fields + ["messages"]


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField()


class ChatSyncMessageSerializer(serializers.Serializer):
    librechat_message_id = serializers.CharField()
    sender = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)


class ChatSyncSerializer(serializers.Serializer):
    """
    Contract for Phase 6's LibreChat -> MindCare mirroring job: upserts a
    ChatSession (matched on librechat_conversation_id) and appends any
    messages not already mirrored (matched on librechat_message_id).
    """

    librechat_conversation_id = serializers.CharField()
    title = serializers.CharField(required=False, allow_blank=True)
    messages = ChatSyncMessageSerializer(many=True)
