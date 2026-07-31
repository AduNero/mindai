from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification-list"),
    path("unread-count/", views.NotificationUnreadCountView.as_view(), name="notification-unread-count"),
    path("<uuid:id>/read/", views.NotificationMarkReadView.as_view(), name="notification-mark-read"),
    path("read-all/", views.NotificationMarkAllReadView.as_view(), name="notification-mark-all-read"),
    path("preferences/", views.NotificationPreferenceView.as_view(), name="notification-preferences"),
]
