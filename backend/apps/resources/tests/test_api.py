import pytest
from rest_framework import status

from apps.resources.models import EmergencyResource, Resource

pytestmark = pytest.mark.django_db


class TestResourceList:
    def test_only_published_resources_visible(self, auth_client):
        Resource.objects.create(title="Public article", resource_type="article", is_published=True)
        Resource.objects.create(title="Draft article", resource_type="article", is_published=False)

        response = auth_client.get("/api/v1/resources/")

        titles = [r["title"] for r in response.data["results"]]
        assert "Public article" in titles
        assert "Draft article" not in titles

    def test_filter_by_resource_type(self, auth_client):
        Resource.objects.create(title="An article", resource_type="article", is_published=True)
        Resource.objects.create(title="A video", resource_type="video", is_published=True)

        response = auth_client.get("/api/v1/resources/", {"resource_type": "video"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "A video"

    def test_retrieve_increments_view_count(self, auth_client):
        resource = Resource.objects.create(title="Popular", resource_type="article", is_published=True)
        auth_client.get(f"/api/v1/resources/{resource.id}/")
        resource.refresh_from_db()
        assert resource.view_count == 1

    def test_unpublished_resource_returns_404(self, auth_client):
        resource = Resource.objects.create(title="Hidden", resource_type="article", is_published=False)
        response = auth_client.get(f"/api/v1/resources/{resource.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAdminResourceManagement:
    def test_regular_user_cannot_create_resource(self, auth_client):
        response = auth_client.post(
            "/api/v1/resources/admin/resources/", {"title": "New", "resource_type": "article"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_resource(self, admin_client):
        response = admin_client.post(
            "/api/v1/resources/admin/resources/", {"title": "New", "resource_type": "article", "is_published": True}
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestEmergencyResources:
    def test_falls_back_to_default_country_when_user_country_unset(self, auth_client, settings):
        settings.DEFAULT_CRISIS_COUNTRY = "US"
        EmergencyResource.objects.create(country_code="US", name="988 Lifeline", phone_number="988")
        EmergencyResource.objects.create(country_code="GH", name="Ghana Helpline", phone_number="0800")

        response = auth_client.get("/api/v1/resources/emergency/")

        assert response.data["count"] == 1
        assert response.data["results"][0]["country_code"] == "US"

    def test_uses_profile_country_when_set(self, auth_client, user):
        user.profile.country_code = "GH"
        user.profile.save()
        EmergencyResource.objects.create(country_code="US", name="988 Lifeline", phone_number="988")
        EmergencyResource.objects.create(country_code="GH", name="Ghana Helpline", phone_number="0800")

        response = auth_client.get("/api/v1/resources/emergency/")

        assert response.data["count"] == 1
        assert response.data["results"][0]["country_code"] == "GH"
