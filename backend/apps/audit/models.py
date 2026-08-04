from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AuditAction(models.TextChoices):
    LOGIN_SUCCESS = "login_success", "Login Success"
    LOGIN_FAILED = "login_failed", "Login Failed"
    LOGOUT = "logout", "Logout"
    PASSWORD_CHANGED = "password_changed", "Password Changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested", "Password Reset Requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed", "Password Reset Completed"
    EMAIL_VERIFIED = "email_verified", "Email Verified"
    PROFILE_UPDATED = "profile_updated", "Profile Updated"
    DATA_EXPORTED = "data_exported", "Data Exported"
    PERMISSION_DENIED = "permission_denied", "Permission Denied"
    ACCOUNT_LOCKED = "account_locked", "Account Locked"
    ACCOUNT_DELETED = "account_deleted", "Account Deleted"
    ADMIN_ACTION = "admin_action", "Administrative Action"
    RISK_DETECTED = "risk_detected", "Crisis/Risk Language Detected"


class AuditLog(BaseModel):
    """
    Security-focused, append-only audit trail (auth events, data access,
    permission failures, crisis-detection triggers). `user` is nullable to
    cover anonymous events such as failed logins against unknown emails.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.user_id} @ {self.created_at}"
