import pytest
from django.utils import timezone
from rest_framework import status

pytestmark = pytest.mark.django_db


def _create_entry(user, title="Entry", body="Some content here."):
    from apps.journals.models import JournalEntry

    return JournalEntry.objects.create(user=user, title=title, body=body, entry_date=timezone.localdate())


class TestJournalCRUD:
    def test_create_entry_with_tags(self, auth_client):
        response = auth_client.post(
            "/api/v1/journals/",
            {
                "title": "Rough day",
                "body": "Lots on my mind.",
                "entry_date": str(timezone.localdate()),
                "tags": ["school", "STRESS"],
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert sorted(response.data["tags"]) == ["school", "stress"]

    def test_update_entry_replaces_tags(self, auth_client, user):
        entry = _create_entry(user)
        response = auth_client.patch(f"/api/v1/journals/{entry.id}/", {"tags": ["new-tag"]})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["tags"] == ["new-tag"]

    def test_list_excludes_other_users_entries(self, auth_client, user, other_user):
        _create_entry(user)
        _create_entry(other_user)
        response = auth_client.get("/api/v1/journals/")
        assert response.data["count"] == 1

    def test_cannot_retrieve_other_users_entry(self, auth_client, other_user):
        entry = _create_entry(other_user)
        response = auth_client.get(f"/api/v1/journals/{entry.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_matches_title_and_body(self, auth_client, user):
        _create_entry(user, title="Feeling anxious about exams")
        _create_entry(user, title="A calm afternoon")
        response = auth_client.get("/api/v1/journals/", {"search": "anxious"})
        assert response.data["count"] == 1

    def test_delete_entry_is_a_hard_delete(self, auth_client, user):
        from apps.journals.models import JournalEntry

        entry = _create_entry(user)
        response = auth_client.delete(f"/api/v1/journals/{entry.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not JournalEntry.objects.filter(id=entry.id).exists()

    def test_stats_endpoint(self, auth_client, user):
        _create_entry(user)
        _create_entry(user)
        response = auth_client.get("/api/v1/journals/stats/")
        assert response.data["total_entries"] == 2


class TestJournalSentimentAnalysis:
    def test_create_entry_produces_tentative_sentiment_label(self, auth_client):
        """`_mock_sentiment_classifier` (conftest.py) stubs the classifier for tests."""

        response = auth_client.post(
            "/api/v1/journals/",
            {"title": "Entry", "body": "Had a fine day.", "entry_date": str(timezone.localdate())},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["sentiment"]["label"] in ("positive", "negative", "neutral")
        assert response.data["sentiment"]["user_action"] == "pending"

    def test_accept_sentiment_label(self, auth_client, user):
        from apps.ai_engine.services.analysis import analyze_journal_entry

        entry = _create_entry(user)
        analyze_journal_entry(entry)

        response = auth_client.patch(f"/api/v1/journals/{entry.id}/sentiment/", {"user_action": "accepted"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user_action"] == "accepted"

    def test_correct_sentiment_label_requires_corrected_label(self, auth_client, user):
        from apps.ai_engine.services.analysis import analyze_journal_entry

        entry = _create_entry(user)
        analyze_journal_entry(entry)

        response = auth_client.patch(f"/api/v1/journals/{entry.id}/sentiment/", {"user_action": "corrected"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = auth_client.patch(
            f"/api/v1/journals/{entry.id}/sentiment/", {"user_action": "corrected", "corrected_label": "negative"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["corrected_label"] == "negative"


class TestJournalCrisisDetection:
    def test_crisis_phrase_flags_entry_without_storing_the_phrase(self, auth_client, user):
        response = auth_client.post(
            "/api/v1/journals/",
            {
                "title": "Entry",
                "body": "I just want to end my life, nothing helps anymore.",
                "entry_date": str(timezone.localdate()),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_flagged"] is True

        from apps.ai_engine.models import RiskAssessment

        risk = RiskAssessment.objects.get(user=user)
        assert risk.risk_level == "critical"
        assert not hasattr(risk, "triggered_phrases")
