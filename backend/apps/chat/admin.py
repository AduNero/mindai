from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["sender", "content", "created_at"]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "started_at", "last_message_at", "is_archived"]
    list_filter = ["is_archived"]
    search_fields = ["title", "user__email"]
    inlines = [ChatMessageInline]
