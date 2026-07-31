from django.urls import path

from . import views

urlpatterns = [
    path("", views.RecommendationListView.as_view(), name="recommendation-list"),
    path("<uuid:id>/", views.RecommendationUpdateView.as_view(), name="recommendation-update"),
    path("generate/", views.GenerateRecommendationsView.as_view(), name="recommendation-generate"),
    path("admin/templates/", views.AdminRecommendationTemplateListCreateView.as_view(), name="admin-recommendation-template-list"),
    path("admin/templates/<uuid:id>/", views.AdminRecommendationTemplateDetailView.as_view(), name="admin-recommendation-template-detail"),
]
