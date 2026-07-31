from rest_framework import serializers

from .models import Recommendation, RecommendationTemplate


class RecommendationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationTemplate
        fields = ["id", "category", "title", "description", "action_url", "trigger_conditions", "is_active"]


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = [
            "id", "title", "description", "category", "source",
            "status", "generated_at", "responded_at",
        ]
        read_only_fields = ["id", "title", "description", "category", "source", "generated_at", "responded_at"]


class RecommendationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ["status"]
