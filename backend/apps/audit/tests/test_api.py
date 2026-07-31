import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAuditLogAccess:
    def test_regular_user_forbidden(self, auth_client):
        response = auth_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_rejected(self, api_client):
        response = api_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_view_logs(self, admin_client):
        response = admin_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_login_creates_audit_log_entry(self, admin_client, api_client, user):
        from apps.audit.models import AuditAction, AuditLog

        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "CorrectHorse42!"})

        assert AuditLog.objects.filter(user=user, action=AuditAction.LOGIN_SUCCESS).exists()

    def test_failed_login_creates_audit_log_entry(self, api_client, user):
        from apps.audit.models import AuditAction, AuditLog

        api_client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrong"})

        assert AuditLog.objects.filter(user=user, action=AuditAction.LOGIN_FAILED).exists()
