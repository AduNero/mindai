"""
Rule-based recommendation engine. Evaluates active RecommendationTemplates
against a context built from the user's most recent signals — mood entry,
AI-analyzed journal/chat sentiment (apps.ai_engine.SentimentResult), and
latest assessment severity — and creates Recommendation rows for the
matching templates.

The mood-based tier works with zero ML dependency (Phase 3); the
sentiment/assessment tier only has data once apps.ai_engine's analysis
tasks have run (Phase 5), so early on templates naturally fall back to
mood-only matching.
"""

from django.utils import timezone

from .models import Recommendation, RecommendationTemplate

MAX_RECOMMENDATIONS_PER_RUN = 3
DEDUPE_WINDOW_HOURS = 24
SENTIMENT_LOOKBACK_DAYS = 3


def _build_context(user):
    latest_mood = user.mood_entries.order_by("-entry_date", "-entry_time").first()
    context = {
        "mood": latest_mood.mood if latest_mood else None,
        "intensity": latest_mood.intensity if latest_mood else None,
        "stress_score": None,
        "anxiety_score": None,
        "depression_score": None,
        "severity": None,
    }

    latest_sentiment = _latest_journal_sentiment(user)
    if latest_sentiment:
        context["stress_score"] = latest_sentiment.stress_score
        context["anxiety_score"] = latest_sentiment.anxiety_score
        context["depression_score"] = latest_sentiment.depression_indicator_score

    latest_result = user.assessment_results.order_by("-taken_at").first()
    if latest_result:
        context["severity"] = latest_result.severity

    return context


def _latest_journal_sentiment(user):
    from django.contrib.contenttypes.models import ContentType

    from apps.ai_engine.models import SentimentResult

    cutoff = timezone.now() - timezone.timedelta(days=SENTIMENT_LOOKBACK_DAYS)
    recent_entry_ids = list(
        user.journal_entries.filter(created_at__gte=cutoff).order_by("-created_at").values_list("id", flat=True)[:5]
    )
    if not recent_entry_ids:
        return None

    content_type = ContentType.objects.get_for_model(user.journal_entries.model)
    return (
        SentimentResult.objects.filter(content_type=content_type, object_id__in=recent_entry_ids)
        .order_by("-analyzed_at")
        .first()
    )


def _template_matches(template, context):
    conditions = template.trigger_conditions or {}

    mood_in = conditions.get("mood_in")
    if mood_in and context.get("mood") not in mood_in:
        return False

    min_intensity = conditions.get("min_intensity")
    if min_intensity is not None:
        intensity = context.get("intensity")
        if intensity is None or intensity < min_intensity:
            return False

    for key in ("min_stress_score", "min_anxiety_score", "min_depression_score"):
        threshold = conditions.get(key)
        if threshold is not None:
            context_key = key.replace("min_", "")
            value = context.get(context_key)
            if value is None or value < threshold:
                return False

    severity_in = conditions.get("severity_in")
    if severity_in and context.get("severity") not in severity_in:
        return False

    return True


def generate_for_user(user, source="mood"):
    """
    Evaluates active RecommendationTemplates against the user's current
    context and creates up to MAX_RECOMMENDATIONS_PER_RUN new Recommendation
    rows, skipping templates already recommended (and still pending) within
    the dedupe window.
    """

    context = _build_context(user)

    cutoff = timezone.now() - timezone.timedelta(hours=DEDUPE_WINDOW_HOURS)
    recently_recommended_template_ids = set(
        Recommendation.objects.filter(user=user, generated_at__gte=cutoff).values_list("template_id", flat=True)
    )

    conditioned_templates = [
        t for t in RecommendationTemplate.objects.filter(is_active=True) if t.trigger_conditions
    ]
    matches = [
        t
        for t in conditioned_templates
        if t.id not in recently_recommended_template_ids and _template_matches(t, context)
    ]

    if not matches:
        fallback = list(
            RecommendationTemplate.objects.filter(is_active=True, trigger_conditions={})
            .exclude(id__in=recently_recommended_template_ids)[:MAX_RECOMMENDATIONS_PER_RUN]
        )
        matches = fallback

    created = []
    for template in matches[:MAX_RECOMMENDATIONS_PER_RUN]:
        created.append(
            Recommendation.objects.create(
                user=user,
                template=template,
                title=template.title,
                description=template.description,
                category=template.category,
                source=source,
            )
        )
    return created
