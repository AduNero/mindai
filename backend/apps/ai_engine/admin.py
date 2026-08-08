from django.contrib import admin

from .models import RiskAssessment, SentimentResult


@admin.register(SentimentResult)
class SentimentResultAdmin(admin.ModelAdmin):
    list_display = ["journal_entry", "label", "confidence", "user_action", "created_at"]
    list_filter = ["label", "user_action"]


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ["user", "risk_level", "detection_source", "acknowledged_at", "created_at"]
    list_filter = ["risk_level", "detection_source"]
    search_fields = ["user__email"]
