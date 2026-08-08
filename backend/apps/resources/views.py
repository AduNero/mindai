from django.conf import settings
from django.db.models import F
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin

from .models import EmergencyResource, Resource, ResourceCategory
from .serializers import (
    EmergencyResourceSerializer,
    ResourceCategorySerializer,
    ResourceSerializer,
    ResourceWriteSerializer,
)


class ResourceCategoryListView(generics.ListAPIView):
    serializer_class = ResourceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ResourceCategory.objects.all().order_by("name")


class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    search_fields = ["title", "description"]
    filterset_fields = ["resource_type", "category"]
    ordering_fields = ["created_at", "view_count"]

    def get_queryset(self):
        return Resource.objects.filter(is_published=True).select_related("category")


class ResourceDetailView(generics.RetrieveAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Resource.objects.filter(is_published=True)
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Resource.objects.filter(id=instance.id).update(view_count=F("view_count") + 1)
        instance.refresh_from_db(fields=["view_count"])
        return Response(self.get_serializer(instance).data)


class AdminResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = Resource.objects.all().select_related("category")
    filterset_fields = ["resource_type", "is_published"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ResourceWriteSerializer
        return ResourceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmergencyResourceListView(generics.ListAPIView):
    """
    Crisis hotlines for DEFAULT_CRISIS_COUNTRY. Always visible, never
    AI-triggered — used by both the Resource Center's "Emergency Resources"
    tab and the crisis-detection flow. Profile carries no location data
    (pseudonymous by design), so this isn't personalized by country.
    """

    serializer_class = EmergencyResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmergencyResource.objects.filter(country_code=settings.DEFAULT_CRISIS_COUNTRY).order_by("name")


class AdminEmergencyResourceViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyResourceSerializer
    permission_classes = [IsAdmin]
    queryset = EmergencyResource.objects.all()
    filterset_fields = ["country_code"]
