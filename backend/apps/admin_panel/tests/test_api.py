import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestDashboardStats:
    def test_regular_user_forbidden(self, auth_client):
        response = auth_client.get("/api/v1/admin-panel/dashboard-stats/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_gets_stats_shape(self, admin_client, user):
        response = admin_client.get("/api/v1/admin-panel/dashboard-stats/")
        assert response.status_code == status.HTTP_200_OK
        expected_keys = {
            "total_users", "active_users_30d", "high_risk_users",
            "mood_entries_30d", "journal_entries_30d",
        }
        assert expected_keys.issubset(response.data.keys())

    def test_total_users_counts_only_role_user(self, admin_client, user, admin_user):
        response = admin_client.get("/api/v1/admin-panel/dashboard-stats/")
        assert response.data["total_users"] == 1  # only the `user` fixture has role=user
