from django.contrib import admin

from .models import EmotionResult, MoodPrediction, RiskAssessment, SentimentResult, WellnessScoreSnapshot


@admin.register(SentimentResult)
class SentimentResultAdmin(admin.ModelAdmin):
    list_display = ["content_type", "object_id", "sentiment", "confidence_score", "analyzed_at"]
    list_filter = ["sentiment"]


@admin.register(EmotionResult)
class EmotionResultAdmin(admin.ModelAdmin):
    list_display = ["content_type", "object_id", "dominant_emotion", "analyzed_at"]
    list_filter = ["dominant_emotion"]


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ["user", "risk_level", "detection_source", "acknowledged_at", "created_at"]
    list_filter = ["risk_level", "detection_source"]
    search_fields = ["user__email"]


@admin.register(WellnessScoreSnapshot)
class WellnessScoreSnapshotAdmin(admin.ModelAdmin):
    list_display = ["user", "score_date", "overall_score"]
    list_filter = ["score_date"]


admin.site.register(MoodPrediction)
