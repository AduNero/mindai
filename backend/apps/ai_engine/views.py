from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RiskAssessment
from .serializers import RiskAssessmentSerializer


class RiskAssessmentOwnListView(generics.ListAPIView):
    """A user's own risk flags — transparency into what triggered a crisis-resources prompt."""

    serializer_class = RiskAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RiskAssessment.objects.filter(user=self.request.user).order_by("-created_at")


class RiskAcknowledgeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        risk = get_object_or_404(RiskAssessment, id=id, user=request.user)
        risk.acknowledged_at = timezone.now()
        risk.save(update_fields=["acknowledged_at"])
        return Response(RiskAssessmentSerializer(risk).data, status=status.HTTP_200_OK)
