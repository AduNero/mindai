from .models import Notification, NotificationChannel, NotificationPreference


def notify(user, notification_type, title, body="", channel=None, related_object=None):
    """
    Creates a Notification for `user`, respecting their channel
    preferences unless `channel` is explicitly forced (e.g. a risk alert
    that should always reach the user in-app regardless of preferences).
    Dispatches the async email send when the resolved channel includes email.
    """

    preference, _ = NotificationPreference.objects.get_or_create(user=user)

    if channel is None:
        channel = NotificationChannel.BOTH if preference.email_enabled else NotificationChannel.IN_APP

    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        channel=channel,
        title=title,
        body=body,
        content_type=_content_type_for(related_object) if related_object else None,
        object_id=getattr(related_object, "id", None),
    )

    if channel in (NotificationChannel.EMAIL, NotificationChannel.BOTH) and preference.email_enabled:
        from .tasks import send_notification_email

        send_notification_email.delay(str(notification.id))

    return notification


def _content_type_for(obj):
    from django.contrib.contenttypes.models import ContentType

    return ContentType.objects.get_for_model(obj)
