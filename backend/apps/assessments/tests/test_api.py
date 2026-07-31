import pytest
from rest_framework import status

from apps.ai_engine.models import RiskAssessment
from apps.assessments.models import AssessmentQuestion, AssessmentType

pytestmark = pytest.mark.django_db

STANDARD_OPTIONS = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]


@pytest.fixture
def phq9(db):
    assessment_type = AssessmentType.objects.create(
        code="phq9", name="PHQ-9", description="", instructions="", max_score=27, is_active=True
    )
    questions = [
        AssessmentQuestion.objects.create(
            assessment_type=assessment_type, order=i, text=f"Question {i}", options=STANDARD_OPTIONS
        )
        for i in range(1, 10)
    ]
    return assessment_type, questions


class TestAssessmentSubmission:
    def test_submit_requires_all_questions_answered(self, auth_client, phq9):
        assessment_type, questions = phq9
        response = auth_client.post(
            "/api/v1/assessments/submit/",
            {
                "assessment_type": "phq9",
                "answers": [{"question_id": str(questions[0].id), "selected_value": 1}],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_rejects_invalid_option_value(self, auth_client, phq9):
        assessment_type, questions = phq9
        answers = [{"question_id": str(q.id), "selected_value": 0} for q in questions]
        answers[0]["selected_value"] = 99  # not a valid option
        response = auth_client.post(
            "/api/v1/assessments/submit/", {"assessment_type": "phq9", "answers": answers}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_computes_total_score_and_severity(self, auth_client, phq9):
        assessment_type, questions = phq9
        # Item 9 ("thoughts of self-harm") answered 0 — kept separate from
        # this scoring test so it doesn't also trip the crisis risk flag
        # (see test_phq9_item9_nonzero_flags_risk_and_returns_crisis_resources).
        answers = [{"question_id": str(q.id), "selected_value": 0 if q.order == 9 else 1} for q in questions]

        response = auth_client.post(
            "/api/v1/assessments/submit/", {"assessment_type": "phq9", "answers": answers}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["total_score"] == 8
        assert response.data["severity"] == "mild"
        assert response.data["risk_flag"] is False

    def test_phq9_item9_nonzero_flags_risk_and_returns_crisis_resources(self, auth_client, user, phq9):
        from apps.resources.models import EmergencyResource

        EmergencyResource.objects.create(country_code="US", name="988 Lifeline", phone_number="988")

        assessment_type, questions = phq9
        answers = [{"question_id": str(q.id), "selected_value": 0} for q in questions]
        item9 = next(q for q in questions if q.order == 9)
        answers[8]["selected_value"] = 2  # item 9 (index 8) = "more than half the days"
        assert answers[8]["question_id"] == str(item9.id)

        response = auth_client.post(
            "/api/v1/assessments/submit/", {"assessment_type": "phq9", "answers": answers}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["risk_flag"] is True
        assert len(response.data["crisis_resources"]) == 1
        assert RiskAssessment.objects.filter(user=user, detection_source="assessment").exists()

    def test_phq9_item9_zero_does_not_flag_risk(self, auth_client, phq9):
        assessment_type, questions = phq9
        answers = [{"question_id": str(q.id), "selected_value": 0} for q in questions]

        response = auth_client.post(
            "/api/v1/assessments/submit/", {"assessment_type": "phq9", "answers": answers}, format="json"
        )

        assert response.data["risk_flag"] is False
        assert not RiskAssessment.objects.exists()

    def test_results_list_only_shows_own_results(self, auth_client, other_auth_client, phq9):
        assessment_type, questions = phq9
        answers = [{"question_id": str(q.id), "selected_value": 0} for q in questions]
        auth_client.post("/api/v1/assessments/submit/", {"assessment_type": "phq9", "answers": answers}, format="json")

        response = other_auth_client.get("/api/v1/assessments/results/")
        assert response.data["count"] == 0
