from django.urls import path

from . import views

urlpatterns = [
    path("dashboard-stats/", views.DashboardStatsView.as_view(), name="admin-dashboard-stats"),
    path("action-logs/", views.AdminActionLogListView.as_view(), name="admin-action-log-list"),
    path("journal-reports/", views.JournalReportListView.as_view(), name="admin-journal-report-list"),
    path("journal-reports/<uuid:id>/resolve/", views.JournalReportResolveView.as_view(), name="admin-journal-report-resolve"),
    path("risk-alerts/", views.RiskAlertListView.as_view(), name="admin-risk-alert-list"),
    path("risk-alerts/<uuid:id>/review/", views.RiskAlertReviewView.as_view(), name="admin-risk-alert-review"),
    path("reports/", views.GeneratedReportListCreateView.as_view(), name="generated-report-list-create"),
    path("reports/<uuid:id>/", views.GeneratedReportDetailView.as_view(), name="generated-report-detail"),
]
