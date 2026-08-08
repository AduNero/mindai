from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_engine.models import RiskAssessment
from apps.ai_engine.serializers import RiskAssessmentSerializer
from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin
from apps.journals.models import JournalEntry
from apps.moods.models import MoodEntry
from apps.users.models import Role, User

from .models import AdminActionLog
from .serializers import AdminActionLogSerializer


class DashboardStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.localdate()
        thirty_days_ago = today - timezone.timedelta(days=30)

        return Response(
            {
                "total_users": User.objects.filter(role=Role.USER).count(),
                "active_users_30d": User.objects.filter(
                    role=Role.USER, last_login__date__gte=thirty_days_ago
                ).count(),
                "high_risk_users": RiskAssessment.objects.filter(
                    risk_level__in=["high", "critical"], acknowledged_at__isnull=True
                ).values("user").distinct().count(),
                "mood_entries_30d": MoodEntry.objects.filter(entry_date__gte=thirty_days_ago).count(),
                "journal_entries_30d": JournalEntry.objects.filter(entry_date__gte=thirty_days_ago).count(),
            }
        )


class AdminActionLogListView(generics.ListAPIView):
    serializer_class = AdminActionLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["admin_user", "action"]
    ordering_fields = ["created_at"]
    queryset = AdminActionLog.objects.all().select_related("admin_user").order_by("-created_at")


class RiskAlertListView(generics.ListAPIView):
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["risk_level", "detection_source"]
    ordering_fields = ["created_at"]
    queryset = RiskAssessment.objects.all().select_related("user").order_by("-created_at")


class RiskAlertReviewView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        risk = RiskAssessment.objects.filter(id=id).first()
        if not risk:
            return Response({"detail": "Risk assessment not found."}, status=404)

        risk.reviewed_by = request.user
        risk.admin_notes = request.data.get("admin_notes", "")
        risk.save(update_fields=["reviewed_by", "admin_notes"])

        AdminActionLog.objects.create(
            admin_user=request.user,
            action="risk_alert_reviewed",
            target_model="RiskAssessment",
            target_id=str(risk.id),
        )
        return Response(RiskAssessmentSerializer(risk).data)
