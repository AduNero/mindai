from django.urls import path

from . import views

urlpatterns = [
    path("risk-assessments/", views.RiskAssessmentOwnListView.as_view(), name="ai-risk-assessments"),
    path("risk-assessments/<uuid:id>/acknowledge/", views.RiskAcknowledgeView.as_view(), name="ai-risk-acknowledge"),
]
