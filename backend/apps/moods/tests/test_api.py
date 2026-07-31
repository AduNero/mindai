import pytest
from django.utils import timezone
from rest_framework import status

from apps.moods.models import MoodEntry

pytestmark = pytest.mark.django_db


def _create_entry(user, mood="happy", intensity=7, entry_date=None):
    return MoodEntry.objects.create(
        user=user,
        mood=mood,
        intensity=intensity,
        entry_date=entry_date or timezone.localdate(),
        entry_time=timezone.localtime().time(),
    )


class TestMoodEntryCRUD:
    def test_create_mood_entry(self, auth_client):
        response = auth_client.post(
            "/api/v1/moods/",
            {
                "mood": "anxious",
                "intensity": 8,
                "entry_date": str(timezone.localdate()),
                "entry_time": "09:00:00",
                "notes": "Big exam today",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert MoodEntry.objects.count() == 1

    def test_create_rejects_intensity_out_of_range(self, auth_client):
        response = auth_client.post(
            "/api/v1/moods/",
            {"mood": "happy", "intensity": 15, "entry_date": str(timezone.localdate()), "entry_time": "09:00:00"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_only_returns_own_entries(self, auth_client, user, other_user):
        _create_entry(user)
        _create_entry(other_user)

        response = auth_client.get("/api/v1/moods/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_user_cannot_delete_others_entry(self, auth_client, other_user):
        entry = _create_entry(other_user)

        response = auth_client.delete(f"/api/v1/moods/{entry.id}/")

        assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN)
        assert MoodEntry.objects.filter(id=entry.id).exists()

    def test_owner_can_delete_own_entry(self, auth_client, user):
        entry = _create_entry(user)
        response = auth_client.delete(f"/api/v1/moods/{entry.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MoodEntry.objects.filter(id=entry.id).exists()


class TestMoodStats:
    def test_current_returns_most_recent_entry(self, auth_client, user):
        _create_entry(user, mood="sad", entry_date=timezone.localdate() - timezone.timedelta(days=1))
        latest = _create_entry(user, mood="happy")

        response = auth_client.get("/api/v1/moods/current/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(latest.id)

    def test_weekly_series_has_seven_days(self, auth_client, user):
        _create_entry(user)
        response = auth_client.get("/api/v1/moods/weekly/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 7

    def test_weekly_series_reflects_logged_intensity(self, auth_client, user):
        _create_entry(user, mood="excited", intensity=9)
        response = auth_client.get("/api/v1/moods/weekly/")
        today_entry = next(d for d in response.data if d["date"] == str(timezone.localdate()))
        assert today_entry["average_intensity"] == 9.0
        assert today_entry["dominant_mood"] == "excited"

    def test_choices_returns_all_eight_moods(self, auth_client):
        response = auth_client.get("/api/v1/moods/choices/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 8
