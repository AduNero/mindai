from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.wellness.models import MeditationSession, SleepEntry

pytestmark = pytest.mark.django_db


class TestSleepEntries:
    def test_create_sleep_entry(self, auth_client):
        response = auth_client.post(
            "/api/v1/wellness/sleep/", {"entry_date": str(date.today()), "hours_slept": 7.5, "quality": 4}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert SleepEntry.objects.count() == 1

    def test_cannot_log_two_entries_same_day(self, auth_client, user):
        SleepEntry.objects.create(user=user, entry_date=date.today(), hours_slept=7, quality=3)
        response = auth_client.post(
            "/api/v1/wellness/sleep/", {"entry_date": str(date.today()), "hours_slept": 8, "quality": 4}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_only_returns_own_entries(self, auth_client, user, other_user):
        SleepEntry.objects.create(user=user, entry_date=date.today(), hours_slept=7, quality=3)
        SleepEntry.objects.create(user=other_user, entry_date=date.today(), hours_slept=6, quality=2)

        response = auth_client.get("/api/v1/wellness/sleep/")
        assert response.data["count"] == 1

    def test_rejects_quality_out_of_range(self, auth_client):
        response = auth_client.post(
            "/api/v1/wellness/sleep/", {"entry_date": str(date.today()), "hours_slept": 7, "quality": 9}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestMeditationSessions:
    def test_create_session(self, auth_client):
        response = auth_client.post(
            "/api/v1/wellness/meditation/",
            {"duration_minutes": 10, "started_at": timezone.now().isoformat(), "completed": True},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_progress_reflects_sessions_this_week(self, auth_client, user):
        MeditationSession.objects.create(
            user=user, duration_minutes=10, started_at=timezone.now(), completed=True
        )
        MeditationSession.objects.create(
            user=user, duration_minutes=15, started_at=timezone.now() - timedelta(days=10), completed=True
        )

        response = auth_client.get("/api/v1/wellness/meditation/progress/")

        assert response.data["total_sessions"] == 2
        assert response.data["total_minutes"] == 25
        assert response.data["sessions_this_week"] == 1
        assert response.data["minutes_this_week"] == 10

    def test_list_only_returns_own_sessions(self, auth_client, user, other_user):
        MeditationSession.objects.create(user=user, duration_minutes=5, started_at=timezone.now())
        MeditationSession.objects.create(user=other_user, duration_minutes=5, started_at=timezone.now())

        response = auth_client.get("/api/v1/wellness/meditation/")
        assert response.data["count"] == 1
