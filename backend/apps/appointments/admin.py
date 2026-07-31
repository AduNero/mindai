from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["user", "counselor", "scheduled_at", "status", "approved_by"]
    list_filter = ["status"]
    search_fields = ["user__email", "counselor__user__email"]
