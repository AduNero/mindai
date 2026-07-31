from django.contrib import admin

from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "mood", "intensity", "entry_date", "entry_time"]
    list_filter = ["mood", "entry_date"]
    search_fields = ["user__email", "notes"]
