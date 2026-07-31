from django.urls import path

from apps.users import views

urlpatterns = [
    path("me/", views.MeView.as_view(), name="user-me"),
    path("me/picture/", views.ProfilePictureUploadView.as_view(), name="user-me-picture"),
    path("counselors/", views.CounselorListView.as_view(), name="counselor-list"),
    path("admin/list/", views.AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/<uuid:id>/", views.AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/counselors/", views.AdminCounselorListView.as_view(), name="admin-counselor-list"),
    path("admin/counselors/<uuid:id>/", views.AdminCounselorDetailView.as_view(), name="admin-counselor-detail"),
    path("admin/counselors/promote/", views.PromoteToCounselorView.as_view(), name="admin-counselor-promote"),
]
