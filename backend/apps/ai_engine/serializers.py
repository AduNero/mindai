from rest_framework import serializers

from .models import EmotionResult, MoodPrediction, RiskAssessment, SentimentResult, WellnessScoreSnapshot


class SentimentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentResult
        fields = [
            "id", "sentiment", "confidence_score", "stress_score", "anxiety_score",
            "burnout_score", "depression_indicator_score", "keywords", "model_version", "analyzed_at",
        ]


class EmotionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionResult
        fields = ["id", "dominant_emotion", "scores", "model_version", "analyzed_at"]


class ContentAnalysisSerializer(serializers.Serializer):
    """Combined sentiment + emotion analysis for a single piece of content (journal entry or chat message)."""

    sentiment = SentimentResultSerializer(allow_null=True)
    emotion = EmotionResultSerializer(allow_null=True)


class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = [
            "id", "risk_level", "detection_source", "triggered_phrases", "confidence_score",
            "resources_shown_at", "acknowledged_at", "created_at",
        ]
        read_only_fields = fields


class WellnessScoreSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellnessScoreSnapshot
        fields = [
            "id", "score_date", "overall_score", "mood_component", "journal_component",
            "assessment_component", "sleep_component", "activity_component", "chat_sentiment_component",
        ]
        read_only_fields = fields


class MoodPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodPrediction
        fields = ["id", "predicted_for_date", "predicted_mood", "confidence_score", "based_on_window_days", "generated_at"]
        read_only_fields = fields
