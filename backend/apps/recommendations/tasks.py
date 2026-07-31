from celery import shared_task


@shared_task
def generate_recommendations_for_user(user_id: str, source: str = "mood"):
    from apps.users.models import User

    from .engine import generate_for_user

    user = User.objects.filter(id=user_id).first()
    if not user:
        return 0

    created = generate_for_user(user, source=source)
    return len(created)
