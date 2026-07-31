from django.db.models import Count
from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsOwner

from .models import ChatMessage, ChatSession, MessageSender
from .serializers import (
    ChatMessageSerializer,
    ChatSessionDetailSerializer,
    ChatSessionSerializer,
    SendMessageSerializer,
)
from .services.llm import ChatServiceUnavailable, get_chat_reply

AUTO_TITLE_MAX_LENGTH = 60


class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    search_fields = ["title"]
    filterset_fields = ["is_archived"]
    ordering_fields = ["last_message_at", "started_at"]

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .annotate(message_count=Count("messages"))
            .order_by("-last_message_at", "-started_at")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ChatSessionDetailSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.order_by("created_at")
        return Response(ChatMessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """
        Persists the user's message, generates the AI companion's reply
        (apps.chat.services.llm), and persists that too. If the LLM
        provider is unreachable, the user's message is still saved and
        returned with assistant_message: null + an error note rather than
        losing it — the user can retry without re-typing.
        """

        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = ChatMessage.objects.create(
            session=session, sender=MessageSender.USER, content=serializer.validated_data["content"]
        )
        session.last_message_at = user_message.created_at
        if session.messages.count() == 1:
            session.title = user_message.content[:AUTO_TITLE_MAX_LENGTH]
        session.save(update_fields=["last_message_at", "title"])

        from apps.ai_engine.tasks import analyze_content

        analyze_content.delay("chat", "chatmessage", str(user_message.id))

        history = [
            {"role": m.sender, "content": m.content}
            for m in session.messages.order_by("created_at")
        ]

        response_data = {"user_message": ChatMessageSerializer(user_message).data, "assistant_message": None}
        try:
            reply_text = get_chat_reply(history)
        except ChatServiceUnavailable as exc:
            response_data["error"] = str(exc)
            return Response(response_data, status=status.HTTP_201_CREATED)

        assistant_message = ChatMessage.objects.create(
            session=session, sender=MessageSender.ASSISTANT, content=reply_text
        )
        session.last_message_at = assistant_message.created_at
        session.save(update_fields=["last_message_at"])

        response_data["assistant_message"] = ChatMessageSerializer(assistant_message).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.order_by("created_at")

        # Note: intentionally not named "format" — that query param is
        # reserved by DRF's own format-suffix content negotiation and would
        # 404 before this view ever ran (only JSONRenderer is registered).
        if request.query_params.get("export_format") == "txt":
            lines = [f"MindCare AI — Chat Export: {session.title}", ""]
            for m in messages:
                lines.append(f"[{m.created_at.isoformat()}] {m.get_sender_display()}: {m.content}")
            response = HttpResponse("\n".join(lines), content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="chat-{session.id}.txt"'
            return response

        return Response(ChatSessionDetailSerializer(session).data)


class ChatSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])

        messages = (
            ChatMessage.objects.filter(session__user=request.user, content__icontains=query)
            .select_related("session")
            .order_by("-created_at")[:50]
        )
        return Response(
            [
                {
                    "session_id": m.session_id,
                    "session_title": m.session.title,
                    "message_id": m.id,
                    "snippet": m.content[:200],
                    "created_at": m.created_at,
                }
                for m in messages
            ]
        )
