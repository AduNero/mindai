from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("admin/resources", views.AdminResourceViewSet, basename="admin-resource")
router.register("admin/emergency", views.AdminEmergencyResourceViewSet, basename="admin-emergency-resource")

urlpatterns = [
    path("categories/", views.ResourceCategoryListView.as_view(), name="resource-category-list"),
    path("emergency/", views.EmergencyResourceListView.as_view(), name="emergency-resource-list"),
    path("<uuid:id>/", views.ResourceDetailView.as_view(), name="resource-detail"),
    path("", views.ResourceListView.as_view(), name="resource-list"),
    *router.urls,
]
