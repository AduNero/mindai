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


class SendMessageResponseSerializer(serializers.Serializer):
    user_message = ChatMessageSerializer()
    assistant_message = ChatMessageSerializer(allow_null=True)
