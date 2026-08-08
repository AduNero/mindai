from rest_framework import serializers

from apps.common.constants import SENTIMENT_CHOICES

from .models import RiskAssessment, SentimentResult


class SentimentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentResult
        fields = [
            "id", "label", "confidence", "model_version",
            "user_action", "corrected_label", "actioned_at", "created_at",
        ]
        read_only_fields = fields


class SentimentActionSerializer(serializers.Serializer):
    """Accept / reject / correct the classifier's tentative label on a journal entry."""

    user_action = serializers.ChoiceField(choices=["accepted", "rejected", "corrected"])
    corrected_label = serializers.ChoiceField(choices=[c[0] for c in SENTIMENT_CHOICES], required=False)

    def validate(self, attrs):
        if attrs["user_action"] == "corrected" and not attrs.get("corrected_label"):
            raise serializers.ValidationError("corrected_label is required when user_action is 'corrected'.")
        return attrs


class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = [
            "id", "risk_level", "detection_source", "confidence_score",
            "resources_shown_at", "acknowledged_at", "created_at",
        ]
        read_only_fields = fields
