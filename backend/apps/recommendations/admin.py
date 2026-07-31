from django.contrib import admin

from .models import Recommendation, RecommendationTemplate


@admin.register(RecommendationTemplate)
class RecommendationTemplateAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["title", "description"]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "category", "status", "generated_at"]
    list_filter = ["status", "category", "source"]
    search_fields = ["user__email", "title"]
