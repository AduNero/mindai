from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsAdmin, IsOwner

from .engine import generate_for_user
from .models import Recommendation, RecommendationTemplate
from .serializers import (
    RecommendationSerializer,
    RecommendationStatusUpdateSerializer,
    RecommendationTemplateSerializer,
)


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["status", "category", "source"]
    ordering_fields = ["generated_at"]

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user).order_by("-generated_at")


class RecommendationUpdateView(generics.UpdateAPIView):
    serializer_class = RecommendationStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Recommendation.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(responded_at=timezone.now())


class GenerateRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        created = generate_for_user(request.user)
        return Response(RecommendationSerializer(created, many=True).data)


class AdminRecommendationTemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = RecommendationTemplateSerializer
    permission_classes = [IsAdmin]
    queryset = RecommendationTemplate.objects.all().order_by("category", "title")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminRecommendationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecommendationTemplateSerializer
    permission_classes = [IsAdmin]
    queryset = RecommendationTemplate.objects.all()
    lookup_field = "id"
