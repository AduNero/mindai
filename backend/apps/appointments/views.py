from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin, IsOwner

from .models import Appointment, AppointmentStatus
from .serializers import (
    AdminAppointmentDecisionSerializer,
    AdminAppointmentSerializer,
    AppointmentCancelSerializer,
    AppointmentCreateSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    http_method_names = ["get", "post", "head", "options"]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at"]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).select_related("counselor__user")

    def get_serializer_class(self):
        if self.action == "create":
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save(user=request.user)
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED, AppointmentStatus.REJECTED):
            raise ValidationError(f"Cannot cancel an appointment with status '{appointment.status}'.")

        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_by = request.user
        appointment.cancellation_reason = serializer.validated_data["cancellation_reason"]
        appointment.save(update_fields=["status", "cancelled_by", "cancellation_reason"])
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status not in (AppointmentStatus.PENDING, AppointmentStatus.APPROVED):
            raise ValidationError(f"Cannot reschedule an appointment with status '{appointment.status}'.")

        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_appointment = Appointment.objects.create(
            user=appointment.user,
            counselor=appointment.counselor,
            scheduled_at=serializer.validated_data["scheduled_at"],
            duration_minutes=appointment.duration_minutes,
            reason_for_visit=appointment.reason_for_visit,
            rescheduled_from=appointment,
        )
        appointment.status = AppointmentStatus.RESCHEDULED
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(new_appointment).data, status=status.HTTP_201_CREATED)


class AdminAppointmentListView(generics.ListAPIView):
    serializer_class = AdminAppointmentSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["status", "counselor"]
    ordering_fields = ["scheduled_at"]
    queryset = Appointment.objects.all().select_related("counselor__user", "user")


class AdminAppointmentApproveView(generics.GenericAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminAppointmentDecisionSerializer
    queryset = Appointment.objects.all()
    lookup_field = "id"

    def post(self, request, id):
        appointment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = AppointmentStatus.APPROVED
        appointment.approved_by = request.user
        appointment.notes = serializer.validated_data["notes"]
        appointment.save(update_fields=["status", "approved_by", "notes"])
        return Response(AdminAppointmentSerializer(appointment).data)


class AdminAppointmentRejectView(generics.GenericAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminAppointmentDecisionSerializer
    queryset = Appointment.objects.all()
    lookup_field = "id"

    def post(self, request, id):
        appointment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = AppointmentStatus.REJECTED
        appointment.approved_by = request.user
        appointment.notes = serializer.validated_data["notes"]
        appointment.save(update_fields=["status", "approved_by", "notes"])
        return Response(AdminAppointmentSerializer(appointment).data)
