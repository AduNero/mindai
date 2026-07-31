import logging
from datetime import date

from celery import shared_task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from apps.common.constants import DETECTION_SOURCE_CHAT, DETECTION_SOURCE_JOURNAL

from .services.model_loader import AIUnavailableError
from .services.risk_detection import detect_crisis_risk

logger = logging.getLogger("apps")

# Maps the (app_label, model) of analyzable content to how to resolve its
# owning user and text body — keeps analyze_content generic instead of
# needing a branch per content type as new ones are added.
_CONTENT_RESOLVERS = {
    ("journals", "journalentry"): {
        "get_text": lambda obj: obj.body,
        "get_user": lambda obj: obj.user,
        "get_date": lambda obj: obj.entry_date,
        "detection_source": DETECTION_SOURCE_JOURNAL,
    },
    ("chat", "chatmessage"): {
        "get_text": lambda obj: obj.content,
        "get_user": lambda obj: obj.session.user,
        "get_date": lambda obj: obj.created_at.date(),
        "detection_source": DETECTION_SOURCE_CHAT,
    },
}


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def analyze_content(self, app_label: str, model_name: str, object_id: str):
    """
    Runs sentiment + emotion + crisis-risk analysis on a journal entry or
    chat message and persists SentimentResult/EmotionResult (and a
    RiskAssessment + notification if crisis language is detected).
    """

    if not settings.AI_ANALYSIS_ENABLED:
        logger.info("AI_ANALYSIS_ENABLED is False — skipping analyze_content for %s:%s", model_name, object_id)
        return

    resolver = _CONTENT_RESOLVERS.get((app_label, model_name))
    if not resolver:
        logger.warning("analyze_content: no resolver for %s.%s", app_label, model_name)
        return

    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    obj = content_type.model_class().objects.filter(id=object_id).first()
    if not obj:
        return

    text = resolver["get_text"](obj)
    user = resolver["get_user"](obj)

    try:
        from .services.emotion import analyze_emotion
        from .services.sentiment import analyze_sentiment

        sentiment_data = analyze_sentiment(text)
        emotion_data = analyze_emotion(text)
    except AIUnavailableError as exc:
        logger.warning("AI analysis unavailable, retrying later: %s", exc)
        raise self.retry(exc=exc)

    from .models import EmotionResult, RiskAssessment, SentimentResult

    SentimentResult.objects.create(content_type=content_type, object_id=obj.id, **sentiment_data)
    if emotion_data.get("dominant_emotion"):
        EmotionResult.objects.create(
            content_type=content_type,
            object_id=obj.id,
            dominant_emotion=emotion_data["dominant_emotion"],
            scores=emotion_data["scores"],
            model_version=emotion_data["model_version"],
        )

    risk = detect_crisis_risk(text)
    if risk:
        risk_assessment = RiskAssessment.objects.create(
            user=user,
            content_type=content_type,
            object_id=obj.id,
            detection_source=resolver["detection_source"],
            **risk,
        )
        _notify_risk_detected(user, risk_assessment)

    # Journal entries surface a risk flag via `is_flagged` for admin visibility.
    if risk and app_label == "journals":
        obj.is_flagged = True
        obj.save(update_fields=["is_flagged"])

    recompute_wellness_score.delay(str(user.id), resolver["get_date"](obj).isoformat())


def _notify_risk_detected(user, risk_assessment):
    from apps.notifications.models import NotificationChannel, NotificationType
    from apps.notifications.services import notify

    notify(
        user,
        NotificationType.RISK_ALERT,
        title="We noticed something in your recent activity",
        body=(
            "Some of what you wrote suggests you might be going through a "
            "difficult time. Please check the Resources page for crisis "
            "support options — you don't have to go through this alone."
        ),
        channel=NotificationChannel.IN_APP,
        related_object=risk_assessment,
    )

    from apps.audit.models import AuditAction
    from apps.audit.utils import log_audit_event

    log_audit_event(
        AuditAction.RISK_DETECTED,
        user=user,
        risk_level=risk_assessment.risk_level,
        detection_source=risk_assessment.detection_source,
    )


@shared_task
def recompute_wellness_score(user_id: str, target_date_iso: str | None = None):
    from apps.users.models import User

    from .services.wellness_score import save_wellness_score

    user = User.objects.filter(id=user_id).first()
    if not user:
        return

    target_date = date.fromisoformat(target_date_iso) if target_date_iso else date.today()
    save_wellness_score(user, target_date)


@shared_task
def generate_mood_prediction(user_id: str):
    from apps.users.models import User

    from .services.mood_prediction import save_mood_prediction

    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    save_mood_prediction(user)


@shared_task
def daily_wellness_and_prediction_sweep():
    """
    Runs once a day (see setup_ai_periodic_tasks): recomputes yesterday's final
    wellness score and generates a fresh mood prediction for every active user.
    """

    from apps.users.models import Role, User

    if not settings.AI_ANALYSIS_ENABLED:
        return 0

    count = 0
    for user_id in User.objects.filter(role=Role.USER, is_active=True).values_list("id", flat=True):
        recompute_wellness_score.delay(str(user_id))
        generate_mood_prediction.delay(str(user_id))
        count += 1

    logger.info("daily_wellness_and_prediction_sweep: dispatched for %s users", count)
    return count
