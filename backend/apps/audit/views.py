from rest_framework import generics

from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    """Security audit trail, admin-only — auth events, permission denials, crisis-detection triggers, etc."""

    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["action", "user"]
    search_fields = ["ip_address", "model_name", "object_id"]
    ordering_fields = ["created_at"]
    queryset = AuditLog.objects.all().select_related("user").order_by("-created_at")
