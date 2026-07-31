import uuid

from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
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
    ChatSyncSerializer,
    SendMessageSerializer,
)

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
        serializer.save(user=self.request.user, librechat_conversation_id=f"local-{uuid.uuid4()}")

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.order_by("created_at")
        return Response(ChatMessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """
        Persists a user message locally. Standalone-testable today; once
        Phase 6 wires the embedded LibreChat UI, actual conversational
        turns flow through LibreChat directly and are mirrored back here
        via the /sync/ endpoint instead of this one.
        """

        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = ChatMessage.objects.create(
            session=session, sender=MessageSender.USER, content=serializer.validated_data["content"]
        )
        session.last_message_at = message.created_at
        if session.messages.count() == 1:
            session.title = message.content[:AUTO_TITLE_MAX_LENGTH]
        session.save(update_fields=["last_message_at", "title"])

        from apps.ai_engine.tasks import analyze_content

        analyze_content.delay("chat", "chatmessage", str(message.id))

        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)

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


class LibreChatSyncNowView(APIView):
    """
    On-demand sync so the AI Chat page shows fresh LibreChat history
    immediately on load, rather than waiting for the periodic 5-minute
    sweep (apps.chat.tasks.sync_all_librechat_conversations).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .services.librechat_sync import sync_user_conversations

        synced = sync_user_conversations(request.user)
        return Response({"synced_conversations": synced})


class ChatSyncView(APIView):
    """
    Phase 6 hook: upserts a ChatSession + its ChatMessages from LibreChat's
    conversation store. Kept as a normal JWT-authenticated, user-scoped
    endpoint for Phase 3; Phase 6 documents the actual service-to-service
    auth chosen for the bridge process that calls it.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session, _ = ChatSession.objects.get_or_create(
            user=request.user,
            librechat_conversation_id=data["librechat_conversation_id"],
            defaults={"title": data.get("title") or "New conversation"},
        )
        if data.get("title"):
            session.title = data["title"]

        existing_ids = set(
            ChatMessage.objects.filter(session=session).values_list("librechat_message_id", flat=True)
        )
        new_messages = []
        latest_timestamp = session.last_message_at
        for msg in data["messages"]:
            if msg["librechat_message_id"] in existing_ids:
                continue
            created_at = msg.get("created_at") or timezone.now()
            new_messages.append(
                ChatMessage(
                    session=session,
                    librechat_message_id=msg["librechat_message_id"],
                    sender=msg["sender"],
                    content=msg["content"],
                    created_at=created_at,
                )
            )
            if latest_timestamp is None or created_at > latest_timestamp:
                latest_timestamp = created_at

        if new_messages:
            ChatMessage.objects.bulk_create(new_messages)

            from apps.ai_engine.tasks import analyze_content

            for msg in new_messages:
                if msg.sender == MessageSender.USER:
                    analyze_content.delay("chat", "chatmessage", str(msg.id))

        session.last_message_at = latest_timestamp
        session.save()

        return Response(ChatSessionDetailSerializer(session).data, status=status.HTTP_200_OK)
