from rest_framework import serializers

from .models import AssessmentAnswer, AssessmentQuestion, AssessmentResult, AssessmentType


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ["id", "order", "text", "options"]


class AssessmentTypeSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentType
        fields = ["id", "code", "name", "description", "instructions", "max_score", "questions"]


class AssessmentTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType
        fields = ["id", "code", "name", "description", "max_score"]


class AssessmentAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_value = serializers.IntegerField(min_value=0)


class AssessmentSubmitSerializer(serializers.Serializer):
    assessment_type = serializers.SlugRelatedField(
        slug_field="code", queryset=AssessmentType.objects.filter(is_active=True)
    )
    answers = AssessmentAnswerInputSerializer(many=True)

    def validate(self, attrs):
        assessment_type = attrs["assessment_type"]
        questions = {str(q.id): q for q in assessment_type.questions.all()}
        answered_ids = {str(a["question_id"]) for a in attrs["answers"]}

        if set(questions.keys()) != answered_ids:
            raise serializers.ValidationError("All questions for this assessment must be answered exactly once.")

        for answer in attrs["answers"]:
            question = questions[str(answer["question_id"])]
            valid_values = {opt["value"] for opt in question.options}
            if answer["selected_value"] not in valid_values:
                raise serializers.ValidationError(
                    f"'{answer['selected_value']}' is not a valid option for question {question.order}."
                )
        return attrs


class AssessmentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    question_order = serializers.IntegerField(source="question.order", read_only=True)

    class Meta:
        model = AssessmentAnswer
        fields = ["id", "question", "question_order", "question_text", "selected_value"]


class AssessmentResultSerializer(serializers.ModelSerializer):
    assessment_type = AssessmentTypeSummarySerializer(read_only=True)
    answers = AssessmentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentResult
        fields = ["id", "assessment_type", "total_score", "severity", "interpretation", "taken_at", "answers"]
        read_only_fields = fields
