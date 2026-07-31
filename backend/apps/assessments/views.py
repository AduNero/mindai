from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsSetPagination

from .models import AssessmentAnswer, AssessmentCode, AssessmentResult, AssessmentType
from .scoring import score_assessment
from .serializers import AssessmentResultSerializer, AssessmentSubmitSerializer, AssessmentTypeSerializer


class AssessmentTypeListView(generics.ListAPIView):
    """Lists the available instruments without their full question bank (for a picker screen)."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = AssessmentType.objects.filter(is_active=True)

    def get_serializer_class(self):
        from .serializers import AssessmentTypeSummarySerializer

        return AssessmentTypeSummarySerializer


class AssessmentTypeDetailView(generics.RetrieveAPIView):
    """Retrieves one instrument with its full question bank, for the "take assessment" screen."""

    serializer_class = AssessmentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AssessmentType.objects.filter(is_active=True).prefetch_related("questions")
    lookup_field = "code"


class AssessmentSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "default"

    @transaction.atomic
    def post(self, request):
        serializer = AssessmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        assessment_type = data["assessment_type"]
        answers = data["answers"]

        total_score = sum(a["selected_value"] for a in answers)
        severity, interpretation = score_assessment(assessment_type.code, total_score, assessment_type.max_score)

        result = AssessmentResult.objects.create(
            user=request.user,
            assessment_type=assessment_type,
            total_score=total_score,
            severity=severity,
            interpretation=interpretation,
        )
        AssessmentAnswer.objects.bulk_create(
            [
                AssessmentAnswer(result=result, question_id=a["question_id"], selected_value=a["selected_value"])
                for a in answers
            ]
        )

        risk_flag = self._flag_crisis_risk_if_needed(request, assessment_type, answers, result)

        from apps.ai_engine.tasks import recompute_wellness_score
        from apps.recommendations.tasks import generate_recommendations_for_user

        recompute_wellness_score.delay(str(request.user.id))
        generate_recommendations_for_user.delay(str(request.user.id), source="assessment")

        response_data = AssessmentResultSerializer(result).data
        response_data["risk_flag"] = risk_flag is not None
        if risk_flag is not None:
            response_data["crisis_resources"] = self._crisis_resources_for(request.user)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def _flag_crisis_risk_if_needed(self, request, assessment_type, answers, result):
        """
        PHQ-9 item 9 ("thoughts of self-harm") is a standard clinical trigger:
        any non-zero response is significant regardless of total score.
        """

        if assessment_type.code != AssessmentCode.PHQ9:
            return None

        item9_question = assessment_type.questions.filter(order=9).first()
        if not item9_question:
            return None

        item9_answer = next((a for a in answers if str(a["question_id"]) == str(item9_question.id)), None)
        if not item9_answer or item9_answer["selected_value"] <= 0:
            return None

        from django.contrib.contenttypes.models import ContentType

        from apps.ai_engine.models import RiskAssessment
        from apps.common.constants import DETECTION_SOURCE_ASSESSMENT, RISK_CRITICAL, RISK_HIGH, RISK_MODERATE

        level_map = {1: RISK_MODERATE, 2: RISK_HIGH, 3: RISK_CRITICAL}
        return RiskAssessment.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(result),
            object_id=result.id,
            risk_level=level_map.get(item9_answer["selected_value"], RISK_HIGH),
            detection_source=DETECTION_SOURCE_ASSESSMENT,
            triggered_phrases=["PHQ-9 item 9: thoughts of self-harm or being better off dead"],
            confidence_score=1.0,
        )

    def _crisis_resources_for(self, user):
        from apps.resources.models import EmergencyResource

        country_code = getattr(getattr(user, "profile", None), "country_code", "") or settings.DEFAULT_CRISIS_COUNTRY
        resources = EmergencyResource.objects.filter(country_code=country_code)
        if not resources.exists():
            resources = EmergencyResource.objects.filter(country_code=settings.DEFAULT_CRISIS_COUNTRY)

        return [
            {
                "name": r.name,
                "phone_number": r.phone_number,
                "website": r.website,
                "is_24_7": r.is_24_7,
            }
            for r in resources
        ]


class AssessmentResultListView(generics.ListAPIView):
    serializer_class = AssessmentResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["assessment_type__code", "severity"]
    ordering_fields = ["taken_at"]

    def get_queryset(self):
        return (
            AssessmentResult.objects.filter(user=self.request.user)
            .select_related("assessment_type")
            .prefetch_related("answers")
        )


class AssessmentResultDetailView(generics.RetrieveAPIView):
    serializer_class = AssessmentResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return AssessmentResult.objects.filter(user=self.request.user)
