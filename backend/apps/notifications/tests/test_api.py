import pytest
from rest_framework import status

from apps.notifications.models import Notification, NotificationChannel, NotificationType

pytestmark = pytest.mark.django_db


class TestNotificationList:
    def test_lists_only_own_notifications(self, auth_client, other_auth_client, user, other_user):
        Notification.objects.create(user=user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="For me")
        Notification.objects.create(user=other_user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="Not for me")

        response = auth_client.get("/api/v1/notifications/")
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "For me"

    def test_unread_count(self, auth_client, user):
        Notification.objects.create(user=user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="A", is_read=False)
        Notification.objects.create(user=user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="B", is_read=True)

        response = auth_client.get("/api/v1/notifications/unread-count/")
        assert response.data["unread_count"] == 1

    def test_mark_read(self, auth_client, user):
        notification = Notification.objects.create(
            user=user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="A"
        )
        response = auth_client.post(f"/api/v1/notifications/{notification.id}/read/")
        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_read(self, auth_client, user):
        for i in range(3):
            Notification.objects.create(
                user=user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title=f"N{i}"
            )
        response = auth_client.post("/api/v1/notifications/read-all/")
        assert response.data["marked_read_count"] == 3
        assert Notification.objects.filter(user=user, is_read=False).count() == 0

    def test_cannot_mark_other_users_notification_read(self, auth_client, other_user):
        notification = Notification.objects.create(
            user=other_user, notification_type=NotificationType.SYSTEM, channel=NotificationChannel.IN_APP, title="A"
        )
        response = auth_client.post(f"/api/v1/notifications/{notification.id}/read/")
        assert response.data["marked_read"] is False
        notification.refresh_from_db()
        assert notification.is_read is False


class TestNotificationPreferences:
    def test_get_creates_default_preferences(self, auth_client):
        response = auth_client.get("/api/v1/notifications/preferences/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email_enabled"] is True

    def test_update_preferences(self, auth_client):
        response = auth_client.patch("/api/v1/notifications/preferences/", {"mood_reminder": False})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["mood_reminder"] is False
