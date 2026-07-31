import uuid

import pytest
from rest_framework import status

from apps.chat.models import ChatMessage, ChatSession, MessageSender

pytestmark = pytest.mark.django_db


def _create_session(user, title="A conversation"):
    return ChatSession.objects.create(user=user, librechat_conversation_id=f"local-{uuid.uuid4()}", title=title)


class TestChatSessions:
    def test_create_session(self, auth_client):
        response = auth_client.post("/api/v1/chat/sessions/", {"title": "New conversation"})
        assert response.status_code == status.HTTP_201_CREATED
        assert ChatSession.objects.count() == 1

    def test_list_only_returns_own_sessions(self, auth_client, user, other_user):
        _create_session(user)
        _create_session(other_user)
        response = auth_client.get("/api/v1/chat/sessions/")
        assert response.data["count"] == 1

    def test_cannot_retrieve_other_users_session(self, auth_client, other_user):
        session = _create_session(other_user)
        response = auth_client.get(f"/api/v1/chat/sessions/{session.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_message_persists_and_auto_titles_first_message(self, auth_client, user):
        session = _create_session(user, title="New conversation")
        response = auth_client.post(
            f"/api/v1/chat/sessions/{session.id}/send/", {"content": "I've been feeling anxious lately."}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert ChatMessage.objects.filter(session=session, sender=MessageSender.USER).count() == 1

        session.refresh_from_db()
        assert session.title == "I've been feeling anxious lately."

    def test_cannot_send_message_to_other_users_session(self, auth_client, other_user):
        session = _create_session(other_user)
        response = auth_client.post(f"/api/v1/chat/sessions/{session.id}/send/", {"content": "hi"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_export_returns_plain_text_transcript(self, auth_client, user):
        session = _create_session(user)
        ChatMessage.objects.create(session=session, sender=MessageSender.USER, content="Hello there")

        response = auth_client.get(f"/api/v1/chat/sessions/{session.id}/export/", {"export_format": "txt"})

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/plain"
        assert b"Hello there" in response.content

    def test_search_finds_matching_message_content(self, auth_client, user):
        session = _create_session(user)
        ChatMessage.objects.create(session=session, sender=MessageSender.USER, content="I feel overwhelmed by exams")

        response = auth_client.get("/api/v1/chat/search/", {"q": "overwhelmed"})

        assert len(response.data) == 1
        assert response.data[0]["session_id"] == session.id

    def test_search_does_not_leak_other_users_messages(self, auth_client, other_user):
        session = _create_session(other_user)
        ChatMessage.objects.create(session=session, sender=MessageSender.USER, content="a private secret")

        response = auth_client.get("/api/v1/chat/search/", {"q": "secret"})
        assert response.data == []
