from django.contrib import admin

from .models import JournalEntry, JournalReport, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "mood", "visibility", "entry_date", "is_flagged"]
    list_filter = ["visibility", "mood", "is_flagged"]
    search_fields = ["title", "body", "user__email"]


@admin.register(JournalReport)
class JournalReportAdmin(admin.ModelAdmin):
    list_display = ["journal_entry", "reason", "status", "reported_by", "reviewed_by", "created_at"]
    list_filter = ["status", "reason"]
