from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.ai_engine.models import RiskAssessment
from apps.ai_engine.serializers import RiskAssessmentSerializer
from apps.appointments.models import Appointment
from apps.assessments.models import AssessmentResult
from apps.chat.models import ChatMessage, ChatSession
from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin
from apps.journals.models import JournalEntry, JournalReport
from apps.moods.models import MoodEntry
from apps.users.models import Role, User

from .models import AdminActionLog, GeneratedReport
from .report_generation import build_csv_report, build_pdf_report
from .serializers import (
    AdminActionLogSerializer,
    GeneratedReportRequestSerializer,
    GeneratedReportSerializer,
    JournalReportModerationSerializer,
    JournalReportResolveSerializer,
)


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
                "total_assessments": AssessmentResult.objects.count(),
                "high_risk_users": RiskAssessment.objects.filter(
                    risk_level__in=["high", "critical"], acknowledged_at__isnull=True
                ).values("user").distinct().count(),
                "total_appointments": Appointment.objects.count(),
                "pending_appointments": Appointment.objects.filter(status="pending").count(),
                "ai_chat_sessions": ChatSession.objects.count(),
                "ai_chat_messages": ChatMessage.objects.count(),
                "mood_entries_30d": MoodEntry.objects.filter(entry_date__gte=thirty_days_ago).count(),
                "journal_entries_30d": JournalEntry.objects.filter(entry_date__gte=thirty_days_ago).count(),
                "pending_journal_reports": JournalReport.objects.filter(status="pending").count(),
            }
        )


class AdminActionLogListView(generics.ListAPIView):
    serializer_class = AdminActionLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["admin_user", "action"]
    ordering_fields = ["created_at"]
    queryset = AdminActionLog.objects.all().select_related("admin_user").order_by("-created_at")


class JournalReportListView(generics.ListAPIView):
    serializer_class = JournalReportModerationSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["status", "reason"]
    ordering_fields = ["created_at"]
    queryset = JournalReport.objects.all().select_related("journal_entry", "reported_by").order_by("-created_at")


class JournalReportResolveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        report = JournalReport.objects.filter(id=id).first()
        if not report:
            return Response({"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = JournalReportResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        report.status = data["status"]
        report.review_notes = data["review_notes"]
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save(update_fields=["status", "review_notes", "reviewed_by", "reviewed_at"])

        if data["remove_entry"]:
            report.journal_entry.visibility = "private"
            report.journal_entry.save(update_fields=["visibility"])

        AdminActionLog.objects.create(
            admin_user=request.user,
            action="journal_report_resolved",
            target_model="JournalReport",
            target_id=str(report.id),
            description=f"status={report.status}, remove_entry={data['remove_entry']}",
        )
        return Response(JournalReportModerationSerializer(report).data)


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
            return Response({"detail": "Risk assessment not found."}, status=status.HTTP_404_NOT_FOUND)

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


class GeneratedReportListCreateView(generics.ListCreateAPIView):
    """
    Personal report generation available to any authenticated user for
    their own data; the Admin Dashboard's platform-wide reports reuse the
    same model with `requested_by` scoped to the admin instead.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GeneratedReportSerializer
    pagination_class = StandardResultsSetPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "report_generation"

    def get_queryset(self):
        return GeneratedReport.objects.filter(requested_by=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = GeneratedReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        report = GeneratedReport.objects.create(
            requested_by=request.user,
            report_type=data["report_type"],
            format=data["format"],
            period_start=data["period_start"],
            period_end=data["period_end"],
        )

        try:
            builder = build_pdf_report if data["format"] == "pdf" else build_csv_report
            content_file = builder(request.user, data["period_start"], data["period_end"])
            report.file.save(content_file.name, content_file, save=False)
            report.status = "completed"
            report.completed_at = timezone.now()
        except Exception as exc:  # noqa: BLE001 - report generation failures shouldn't 500 the request
            report.status = "failed"
            report.error_message = str(exc)
        report.save()

        return Response(GeneratedReportSerializer(report).data, status=status.HTTP_201_CREATED)


class GeneratedReportDetailView(generics.RetrieveAPIView):
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return GeneratedReport.objects.filter(requested_by=self.request.user)
