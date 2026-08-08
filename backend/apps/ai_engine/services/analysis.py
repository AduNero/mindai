"""
Synchronous analysis run inline on journal-entry create/update — see
apps.journals.views.JournalEntryViewSet. Both the sentiment classifier and
the crisis-phrase detector are local, millisecond-scale calls, so there's
no reason to route this through Celery/a broker the way the old
Hugging-Face-transformer pipeline needed to.
"""

import logging

from django.conf import settings

from .risk_detection import detect_crisis_risk
from .sentiment_classifier import ClassifierUnavailableError, classify_sentiment

logger = logging.getLogger("apps")


def analyze_journal_entry(entry):
    """
    Classifies `entry.body`'s sentiment (if the classifier artifact is
    available) and screens it for crisis language. Persists a
    SentimentResult / RiskAssessment as appropriate and returns the
    created SentimentResult (or None).
    """

    sentiment_result = None
    if settings.AI_ANALYSIS_ENABLED:
        sentiment_result = _run_classifier(entry)

    risk = detect_crisis_risk(entry.body)
    if risk:
        _handle_risk(entry, risk)
        if not entry.is_flagged:
            entry.is_flagged = True
            entry.save(update_fields=["is_flagged"])
    elif entry.is_flagged:
        # Re-analysis on edit: a previously flagged entry no longer matches
        # any crisis phrase (e.g. the user rewrote it).
        entry.is_flagged = False
        entry.save(update_fields=["is_flagged"])

    return sentiment_result


def _run_classifier(entry):
    from .. import models as ai_models

    try:
        result = classify_sentiment(entry.body)
    except ClassifierUnavailableError as exc:
        logger.warning("Sentiment classifier unavailable, skipping analysis: %s", exc)
        return None

    return ai_models.SentimentResult.objects.create(
        journal_entry=entry,
        label=result["label"],
        confidence=result["confidence"],
        model_version=result["model_version"],
    )


def _handle_risk(entry, risk):
    from apps.common.constants import DETECTION_SOURCE_JOURNAL

    from .. import models as ai_models

    risk_assessment = ai_models.RiskAssessment.objects.create(
        user=entry.user,
        journal_entry=entry,
        detection_source=DETECTION_SOURCE_JOURNAL,
        risk_level=risk["risk_level"],
        confidence_score=risk["confidence_score"],
    )

    from apps.notifications.models import NotificationChannel, NotificationType
    from apps.notifications.services import notify

    notify(
        entry.user,
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
        user=entry.user,
        risk_level=risk_assessment.risk_level,
        detection_source=risk_assessment.detection_source,
    )
