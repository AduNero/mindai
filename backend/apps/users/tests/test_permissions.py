import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAdminOnlyEndpoints:
    def test_anonymous_user_rejected(self, api_client):
        response = api_client.get("/api/v1/users/admin/list/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_forbidden(self, auth_client):
        response = auth_client.get("/api/v1/users/admin/list/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_counselor_forbidden(self, counselor_client):
        response = counselor_client.get("/api/v1/users/admin/list/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_allowed(self, admin_client):
        response = admin_client.get("/api/v1/users/admin/list/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_promote_user_to_counselor(self, admin_client, user):
        response = admin_client.post(
            "/api/v1/users/admin/counselors/promote/",
            {"user_id": str(user.id), "specialization": "Grief counseling"},
        )
        assert response.status_code == status.HTTP_201_CREATED

        user.refresh_from_db()
        assert user.role == "counselor"

    def test_regular_user_cannot_promote(self, auth_client, other_user):
        response = auth_client.post(
            "/api/v1/users/admin/counselors/promote/", {"user_id": str(other_user.id)}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_promote_user_to_admin(self, admin_client, user):
        response = admin_client.patch(f"/api/v1/users/admin/{user.id}/", {"role": "admin"})
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.role == "admin"

    def test_regular_user_cannot_promote_to_admin(self, auth_client, other_user):
        response = auth_client.patch(f"/api/v1/users/admin/{other_user.id}/", {"role": "admin"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        other_user.refresh_from_db()
        assert other_user.role != "admin"

    def test_admin_can_remove_another_admins_access(self, admin_client, user):
        user.role = "admin"
        user.save(update_fields=["role"])

        response = admin_client.patch(f"/api/v1/users/admin/{user.id}/", {"role": "user"})
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.role == "user"

    def test_admin_cannot_remove_own_admin_access(self, admin_client, admin_user):
        response = admin_client.patch(f"/api/v1/users/admin/{admin_user.id}/", {"role": "user"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        admin_user.refresh_from_db()
        assert admin_user.role == "admin"


class TestProfileOwnership:
    def test_user_can_view_own_profile(self, auth_client):
        response = auth_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_cannot_view_profile(self, api_client):
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
