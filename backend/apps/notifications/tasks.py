import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification, NotificationPreference

logger = logging.getLogger("apps")

REMINDER_SPECS = [
    # (preference_flag, notification_type, title, body)
    ("daily_reminder", "daily_reminder", "How are you feeling today?",
     "Take a moment to check in with yourself on MindCare AI."),
    ("mood_reminder", "mood_reminder", "Log today's mood",
     "You haven't logged a mood entry today — it only takes a few seconds."),
    ("journal_reminder", "journal_reminder", "Time to journal",
     "Writing a few lines about your day can help you process how you're feeling."),
    ("meditation_reminder", "meditation_reminder", "Take a mindful break",
     "A short meditation or breathing exercise could help you reset."),
    ("assessment_reminder", "assessment_reminder", "Check in with an assessment",
     "It's been a while since your last mental health assessment."),
]


@shared_task
def send_notification_email(notification_id):
    notification = Notification.objects.filter(id=notification_id).select_related("user").first()
    if not notification:
        return

    send_mail(
        subject=f"{settings.SITE_NAME} — {notification.title}",
        message=notification.body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[notification.user.email],
        fail_silently=True,
    )
    notification.email_sent_at = timezone.now()
    notification.save(update_fields=["email_sent_at"])


@shared_task
def send_due_reminders():
    """
    Runs hourly (see apps.notifications.management.commands.setup_periodic_tasks).
    Sends each enabled reminder type to users whose preferred_reminder_time
    falls in the current hour, skipping mood/journal reminders for users
    who already logged one today.
    """

    from .services import notify

    current_hour = timezone.localtime().hour
    preferences = NotificationPreference.objects.filter(
        preferred_reminder_time__hour=current_hour
    ).select_related("user")

    sent = 0
    for preference in preferences:
        user = preference.user
        today = timezone.localdate()

        for flag, notification_type, title, body in REMINDER_SPECS:
            if not getattr(preference, flag):
                continue
            if notification_type == "mood_reminder" and user.mood_entries.filter(entry_date=today).exists():
                continue
            if notification_type == "journal_reminder" and user.journal_entries.filter(entry_date=today).exists():
                continue

            notify(user, notification_type, title, body)
            sent += 1

    logger.info("send_due_reminders: dispatched %s reminder(s)", sent)
    return sent
