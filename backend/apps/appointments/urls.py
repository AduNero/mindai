from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminAppointmentApproveView, AdminAppointmentListView, AdminAppointmentRejectView, AppointmentViewSet

router = DefaultRouter()
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("admin/list/", AdminAppointmentListView.as_view(), name="admin-appointment-list"),
    path("admin/<uuid:id>/approve/", AdminAppointmentApproveView.as_view(), name="admin-appointment-approve"),
    path("admin/<uuid:id>/reject/", AdminAppointmentRejectView.as_view(), name="admin-appointment-reject"),
    *router.urls,
]
