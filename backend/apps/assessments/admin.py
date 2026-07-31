from django.contrib import admin

from .models import AssessmentAnswer, AssessmentQuestion, AssessmentResult, AssessmentType


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 0
    ordering = ["order"]


@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "max_score", "is_active"]
    inlines = [AssessmentQuestionInline]


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ["user", "assessment_type", "total_score", "severity", "taken_at"]
    list_filter = ["assessment_type", "severity"]
    search_fields = ["user__email"]


admin.site.register(AssessmentAnswer)
