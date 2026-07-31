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
            "total_users", "active_users_30d", "total_assessments", "high_risk_users",
            "total_appointments", "pending_appointments", "ai_chat_sessions", "ai_chat_messages",
            "mood_entries_30d", "journal_entries_30d", "pending_journal_reports",
        }
        assert expected_keys.issubset(response.data.keys())

    def test_total_users_counts_only_role_user(self, admin_client, user, admin_user, counselor_user):
        response = admin_client.get("/api/v1/admin-panel/dashboard-stats/")
        assert response.data["total_users"] == 1  # only the `user` fixture has role=user


class TestReportGeneration:
    def test_user_can_generate_csv_report(self, auth_client):
        response = auth_client.post(
            "/api/v1/admin-panel/reports/",
            {"report_type": "monthly", "format": "csv", "period_start": "2026-01-01", "period_end": "2026-01-31"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "completed"

    def test_period_end_before_start_rejected(self, auth_client):
        response = auth_client.post(
            "/api/v1/admin-panel/reports/",
            {"report_type": "monthly", "format": "csv", "period_start": "2026-02-01", "period_end": "2026-01-01"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_only_sees_own_reports(self, auth_client, other_auth_client):
        auth_client.post(
            "/api/v1/admin-panel/reports/",
            {"report_type": "monthly", "format": "csv", "period_start": "2026-01-01", "period_end": "2026-01-31"},
        )
        response = other_auth_client.get("/api/v1/admin-panel/reports/")
        assert response.data["count"] == 0
