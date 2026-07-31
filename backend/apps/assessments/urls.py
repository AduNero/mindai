from django.urls import path

from . import views

urlpatterns = [
    path("types/", views.AssessmentTypeListView.as_view(), name="assessment-type-list"),
    path("types/<str:code>/", views.AssessmentTypeDetailView.as_view(), name="assessment-type-detail"),
    path("submit/", views.AssessmentSubmitView.as_view(), name="assessment-submit"),
    path("results/", views.AssessmentResultListView.as_view(), name="assessment-result-list"),
    path("results/<uuid:id>/", views.AssessmentResultDetailView.as_view(), name="assessment-result-detail"),
]
