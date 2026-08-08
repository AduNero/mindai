from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AdminActionLog(BaseModel):
    """
    Business-level record of administrative actions (user management,
    resource publishing). Complements — but is distinct from —
    `apps.audit.AuditLog`, which is the security-focused, system-wide
    audit trail.
    """

    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="admin_actions")
    action = models.CharField(max_length=100, help_text="e.g. 'user_suspended', 'risk_alert_reviewed'.")
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "admin_action_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["admin_user", "created_at"])]

    def __str__(self):
        return f"{self.admin_user_id} - {self.action}"
