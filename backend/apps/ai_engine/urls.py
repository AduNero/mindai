from django.urls import path

from . import views

urlpatterns = [
    path(
        "analysis/<str:app_label>/<str:model>/<uuid:object_id>/",
        views.ContentAnalysisView.as_view(),
        name="ai-content-analysis",
    ),
    path("wellness-score/", views.WellnessScoreListView.as_view(), name="ai-wellness-score-list"),
    path("wellness-score/current/", views.WellnessScoreCurrentView.as_view(), name="ai-wellness-score-current"),
    path("mood-predictions/", views.MoodPredictionListView.as_view(), name="ai-mood-predictions"),
    path("risk-assessments/", views.RiskAssessmentOwnListView.as_view(), name="ai-risk-assessments"),
    path("risk-assessments/<uuid:id>/acknowledge/", views.RiskAcknowledgeView.as_view(), name="ai-risk-acknowledge"),
]
