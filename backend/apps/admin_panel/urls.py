from django.urls import path

from . import views

urlpatterns = [
    path("dashboard-stats/", views.DashboardStatsView.as_view(), name="admin-dashboard-stats"),
    path("action-logs/", views.AdminActionLogListView.as_view(), name="admin-action-log-list"),
    path("risk-alerts/", views.RiskAlertListView.as_view(), name="admin-risk-alert-list"),
    path("risk-alerts/<uuid:id>/review/", views.RiskAlertReviewView.as_view(), name="admin-risk-alert-review"),
]
