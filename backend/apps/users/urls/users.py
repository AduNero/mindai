from django.urls import path

from apps.users import views

urlpatterns = [
    path("me/", views.MeView.as_view(), name="user-me"),
    path("me/picture/", views.ProfilePictureUploadView.as_view(), name="user-me-picture"),
    path("admin/list/", views.AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/<uuid:id>/", views.AdminUserDetailView.as_view(), name="admin-user-detail"),
]
