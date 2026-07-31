from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmotionResult, MoodPrediction, RiskAssessment, SentimentResult, WellnessScoreSnapshot
from .serializers import (
    ContentAnalysisSerializer,
    EmotionResultSerializer,
    MoodPredictionSerializer,
    RiskAssessmentSerializer,
    SentimentResultSerializer,
    WellnessScoreSnapshotSerializer,
)

# Content types this endpoint is allowed to resolve, mapped to a function
# that returns the owning user of an instance (for ownership enforcement).
_OWNER_RESOLVERS = {
    ("journals", "journalentry"): lambda obj: obj.user_id,
    ("chat", "chatmessage"): lambda obj: obj.session.user_id,
}


class ContentAnalysisView(APIView):
    """
    Returns the latest sentiment + emotion analysis for a specific piece of
    content the requesting user owns (a journal entry or chat message).
    Analysis is produced asynchronously by apps.ai_engine's Celery tasks
    (see Phase 5) shortly after the content is created.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, app_label, model, object_id):
        key = (app_label, model)
        if key not in _OWNER_RESOLVERS:
            raise NotFound("Unsupported content type for analysis lookup.")

        content_type = get_object_or_404(ContentType, app_label=app_label, model=model)
        obj = get_object_or_404(content_type.model_class(), id=object_id)

        owner_id = _OWNER_RESOLVERS[key](obj)
        if owner_id != request.user.id:
            raise PermissionDenied("You do not have access to this content's analysis.")

        sentiment = (
            SentimentResult.objects.filter(content_type=content_type, object_id=object_id)
            .order_by("-analyzed_at")
            .first()
        )
        emotion = (
            EmotionResult.objects.filter(content_type=content_type, object_id=object_id)
            .order_by("-analyzed_at")
            .first()
        )

        data = ContentAnalysisSerializer(
            {
                "sentiment": SentimentResultSerializer(sentiment).data if sentiment else None,
                "emotion": EmotionResultSerializer(emotion).data if emotion else None,
            }
        ).data
        return Response(data)


class WellnessScoreListView(generics.ListAPIView):
    """Feeds the dashboard's wellness-score trend chart — intentionally unpaginated so a
    `?days=N` window always returns the full series, not just the first page."""

    serializer_class = WellnessScoreSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = WellnessScoreSnapshot.objects.filter(user=self.request.user).order_by("-score_date")
        days = self.request.query_params.get("days")
        if days and days.isdigit():
            cutoff = timezone.localdate() - timezone.timedelta(days=int(days))
            qs = qs.filter(score_date__gte=cutoff)
        return qs


class WellnessScoreCurrentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        snapshot = (
            WellnessScoreSnapshot.objects.filter(user=request.user).order_by("-score_date").first()
        )
        if not snapshot:
            return Response(None)
        return Response(WellnessScoreSnapshotSerializer(snapshot).data)


class MoodPredictionListView(generics.ListAPIView):
    serializer_class = MoodPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return MoodPrediction.objects.filter(user=self.request.user).order_by("-predicted_for_date")


class RiskAssessmentOwnListView(generics.ListAPIView):
    """A user's own risk flags — transparency into what triggered a crisis-resources prompt."""

    serializer_class = RiskAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RiskAssessment.objects.filter(user=self.request.user).order_by("-created_at")


class RiskAcknowledgeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        risk = get_object_or_404(RiskAssessment, id=id, user=request.user)
        risk.acknowledged_at = timezone.now()
        risk.save(update_fields=["acknowledged_at"])
        return Response(RiskAssessmentSerializer(risk).data, status=status.HTTP_200_OK)
