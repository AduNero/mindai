from django.contrib import admin

from .models import JournalEntry, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "mood", "entry_date", "is_flagged"]
    list_filter = ["mood", "is_flagged"]
    search_fields = ["title", "body", "user__email"]
