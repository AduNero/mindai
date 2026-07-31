from django.contrib import admin

from .models import AdminActionLog, GeneratedReport


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ["admin_user", "action", "target_model", "target_id", "created_at"]
    list_filter = ["action"]
    search_fields = ["admin_user__email", "target_id"]


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ["requested_by", "report_type", "format", "status", "created_at"]
    list_filter = ["report_type", "format", "status"]
