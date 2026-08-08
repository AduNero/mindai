from django.contrib import admin

from .models import AdminActionLog


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ["admin_user", "action", "target_model", "target_id", "created_at"]
    list_filter = ["action"]
    search_fields = ["admin_user__email", "target_id"]
