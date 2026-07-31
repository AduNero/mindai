import pytest
from django.utils import timezone
from rest_framework import status

from apps.journals.models import JournalEntry, JournalReport

pytestmark = pytest.mark.django_db


def _create_entry(user, visibility="private", title="Entry"):
    return JournalEntry.objects.create(
        user=user, title=title, body="Some content here.", entry_date=timezone.localdate(), visibility=visibility
    )


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

    def test_cannot_retrieve_other_users_private_entry(self, auth_client, other_user):
        entry = _create_entry(other_user, visibility="private")
        response = auth_client.get(f"/api/v1/journals/{entry.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_matches_title_and_body(self, auth_client, user):
        _create_entry(user, title="Feeling anxious about exams")
        _create_entry(user, title="A calm afternoon")
        response = auth_client.get("/api/v1/journals/", {"search": "anxious"})
        assert response.data["count"] == 1

    def test_stats_endpoint_counts_by_visibility(self, auth_client, user):
        _create_entry(user, visibility="private")
        _create_entry(user, visibility="public")
        response = auth_client.get("/api/v1/journals/stats/")
        assert response.data["total_entries"] == 2
        assert response.data["private_entries"] == 1
        assert response.data["public_entries"] == 1


class TestJournalModeration:
    def test_user_can_report_public_entry(self, auth_client, other_user):
        entry = _create_entry(other_user, visibility="public")
        response = auth_client.post(
            "/api/v1/journals/reports/", {"journal_entry": str(entry.id), "reason": "self_harm"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        entry.refresh_from_db()
        assert entry.is_flagged is True

    def test_cannot_report_own_entry(self, auth_client, user):
        entry = _create_entry(user, visibility="public")
        response = auth_client.post(
            "/api/v1/journals/reports/", {"journal_entry": str(entry.id), "reason": "spam"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_report_private_entry(self, auth_client, other_user):
        entry = _create_entry(other_user, visibility="private")
        response = auth_client.post(
            "/api/v1/journals/reports/", {"journal_entry": str(entry.id), "reason": "spam"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_resolve_report(self, admin_client, auth_client, user, other_user):
        entry = _create_entry(other_user, visibility="public")
        report = JournalReport.objects.create(journal_entry=entry, reported_by=user, reason="spam")

        response = admin_client.post(
            f"/api/v1/admin-panel/journal-reports/{report.id}/resolve/",
            {"status": "dismissed", "review_notes": "Not spam"},
        )

        assert response.status_code == status.HTTP_200_OK
        report.refresh_from_db()
        assert report.status == "dismissed"
        assert report.reviewed_by is not None

    def test_non_admin_cannot_resolve_report(self, auth_client, other_user):
        entry = _create_entry(other_user, visibility="public")
        report = JournalReport.objects.create(journal_entry=entry, reason="spam")

        response = auth_client.post(
            f"/api/v1/admin-panel/journal-reports/{report.id}/resolve/", {"status": "dismissed"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
