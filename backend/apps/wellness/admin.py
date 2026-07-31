from django.contrib import admin

from .models import MeditationSession, SleepEntry


@admin.register(SleepEntry)
class SleepEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "entry_date", "hours_slept", "quality"]
    list_filter = ["quality"]


@admin.register(MeditationSession)
class MeditationSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "duration_minutes", "completed", "started_at"]
    list_filter = ["completed"]
