import logging

from celery import shared_task

logger = logging.getLogger("apps")


@shared_task
def sync_librechat_conversations_for_user(user_id: str):
    from apps.users.models import User

    from .services.librechat_sync import sync_user_conversations

    user = User.objects.filter(id=user_id).first()
    if not user:
        return 0
    return sync_user_conversations(user)


@shared_task
def sync_all_librechat_conversations():
    """Runs periodically (see setup_periodic_tasks) — syncs every active user's LibreChat conversations."""

    from apps.users.models import Role, User

    count = 0
    for user_id in User.objects.filter(role=Role.USER, is_active=True).values_list("id", flat=True):
        sync_librechat_conversations_for_user.delay(str(user_id))
        count += 1

    logger.info("sync_all_librechat_conversations: dispatched for %s users", count)
    return count
