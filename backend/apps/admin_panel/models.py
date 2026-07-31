from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AdminActionLog(BaseModel):
    """
    Business-level record of administrative actions (user management,
    moderation decisions, appointment/counselor approvals, resource
    publishing). Complements — but is distinct from — `apps.audit.AuditLog`,
    which is the security-focused, system-wide audit trail.
    """

    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="admin_actions")
    action = models.CharField(max_length=100, help_text="e.g. 'user_suspended', 'journal_report_actioned'.")
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "admin_action_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["admin_user", "created_at"])]

    def __str__(self):
        return f"{self.admin_user_id} - {self.action}"


class ReportType(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"
    MENTAL_HEALTH = "mental_health", "Mental Health Summary"


class ReportFormat(models.TextChoices):
    PDF = "pdf", "PDF"
    CSV = "csv", "CSV"


class ReportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class GeneratedReport(BaseModel):
    """
    A generated export — either a user's personal mental-health report or
    an admin's platform-wide analytics report. `requested_by` distinguishes
    the two (regular user vs. admin); scope is enforced at the API layer.
    """

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="generated_reports")
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    format = models.CharField(max_length=5, choices=ReportFormat.choices)
    period_start = models.DateField()
    period_end = models.DateField()
    file = models.FileField(upload_to="reports/%Y/%m/", null=True, blank=True)
    status = models.CharField(max_length=10, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    error_message = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "generated_reports"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["requested_by", "report_type"])]

    def __str__(self):
        return f"{self.report_type} report for {self.requested_by_id} ({self.status})"
