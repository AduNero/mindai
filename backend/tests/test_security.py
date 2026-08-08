import io

import pytest
from django.conf import settings
from PIL import Image
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestRateLimiting:
    def test_login_endpoint_throttles_after_configured_limit(self, api_client, user):
        limit = int(settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth"].split("/")[0])

        responses = [
            api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrong"})
            for _ in range(limit + 1)
        ]

        assert responses[-1].status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_register_endpoint_throttles(self, api_client):
        limit = int(settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth"].split("/")[0])

        last_response = None
        for i in range(limit + 1):
            last_response = api_client.post(
                "/api/v1/auth/register/",
                {
                    "email": f"throttle{i}@example.com",
                    "pseudonym": f"throttle{i}",
                    "password": "CorrectHorse42!",
                    "password_confirm": "CorrectHorse42!",
                    "age_confirmed": True,
                    "consent_accepted": True,
                },
            )

        assert last_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestUnauthenticatedAccessRejected:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/moods/",
            "/api/v1/journals/",
            "/api/v1/ai/risk-assessments/",
            "/api/v1/notifications/",
            "/api/v1/users/me/",
            "/api/v1/admin-panel/dashboard-stats/",
            "/api/v1/audit/logs/",
        ],
    )
    def test_endpoint_requires_authentication(self, api_client, path):
        response = api_client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenTampering:
    def test_garbage_bearer_token_rejected(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        response = api_client.get("/api/v1/moods/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_bearer_prefix_rejected(self, api_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = str(RefreshToken.for_user(user).access_token)
        api_client.credentials(HTTP_AUTHORIZATION=token)  # no "Bearer " prefix
        response = api_client.get("/api/v1/moods/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token_rejected(self, api_client, user):
        from datetime import timedelta

        from rest_framework_simplejwt.tokens import AccessToken

        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.get("/api/v1/moods/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestFileUploadValidation:
    def _make_valid_png(self, dimensions=(10, 10)):
        """A genuinely valid, parseable PNG — large dimensions/noise make it compress poorly, so it stays large on disk."""
        import random

        buffer = io.BytesIO()
        image = Image.new("RGB", dimensions)
        image.putdata([(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(dimensions[0] * dimensions[1])])
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.read()

    def test_rejects_non_image_content_type(self, auth_client):
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_file = SimpleUploadedFile("evil.txt", b"not an image", content_type="text/plain")
        response = auth_client.post("/api/v1/users/me/picture/", {"profile_picture": fake_file}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_oversized_image(self, auth_client, settings):
        from django.core.files.uploadedfile import SimpleUploadedFile

        settings.MAX_UPLOAD_SIZE_BYTES = 1024  # 1KB — a real (noisy, poorly-compressing) 200x200 PNG easily exceeds this.
        oversized = SimpleUploadedFile("pic.png", self._make_valid_png((200, 200)), content_type="image/png")

        response = auth_client.post(
            "/api/v1/users/me/picture/", {"profile_picture": oversized}, format="multipart"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestIDORAcrossOwnedResources:
    """Spot-check that owner-scoped detail endpoints don't leak other users' objects by ID."""

    def test_cannot_retrieve_other_users_journal_entry(self, auth_client, other_user):
        from apps.journals.models import JournalEntry
        from django.utils import timezone

        entry = JournalEntry.objects.create(
            user=other_user, title="Private", body="Not yours.", entry_date=timezone.localdate()
        )
        response = auth_client.get(f"/api/v1/journals/{entry.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_action_other_users_journal_sentiment(self, auth_client, other_user):
        from apps.ai_engine.services.analysis import analyze_journal_entry
        from apps.journals.models import JournalEntry
        from django.utils import timezone

        entry = JournalEntry.objects.create(
            user=other_user, title="Private", body="Not yours.", entry_date=timezone.localdate()
        )
        analyze_journal_entry(entry)

        response = auth_client.patch(f"/api/v1/journals/{entry.id}/sentiment/", {"user_action": "accepted"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_acknowledge_other_users_risk_assessment(self, auth_client, other_user):
        from apps.ai_engine.models import RiskAssessment

        risk = RiskAssessment.objects.create(user=other_user, risk_level="high", detection_source="journal")
        response = auth_client.post(f"/api/v1/ai/risk-assessments/{risk.id}/acknowledge/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
