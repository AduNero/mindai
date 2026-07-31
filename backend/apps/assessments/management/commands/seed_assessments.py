from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AssessmentCode, AssessmentQuestion, AssessmentType

STANDARD_0_3 = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]

FREQUENCY_0_4 = [
    {"value": 0, "label": "Never"},
    {"value": 1, "label": "Almost never"},
    {"value": 2, "label": "Sometimes"},
    {"value": 3, "label": "Fairly often"},
    {"value": 4, "label": "Very often"},
]

def _reversed_scale(scale):
    """Copies + reverses a scale's labels so a raw answer already reflects
    the intended direction for reverse-worded items (e.g. "I feel confident"
    scored so that agreeing counts as *lower* stress, not higher)."""
    reversed_labels = [opt["label"] for opt in reversed(scale)]
    return [{"value": i, "label": label} for i, label in enumerate(reversed_labels)]


FREQUENCY_0_4_REVERSED = _reversed_scale(FREQUENCY_0_4)

AGREEMENT_0_3 = [
    {"value": 0, "label": "Strongly disagree"},
    {"value": 1, "label": "Disagree"},
    {"value": 2, "label": "Agree"},
    {"value": 3, "label": "Strongly agree"},
]

AGREEMENT_0_3_REVERSED = _reversed_scale(AGREEMENT_0_3)


ASSESSMENTS = {
    AssessmentCode.PHQ9: {
        "name": "PHQ-9 (Patient Health Questionnaire)",
        "description": "A 9-item screening tool for the presence and severity of depression symptoms.",
        "instructions": "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
        "max_score": 27,
        "questions": [
            ("Little interest or pleasure in doing things", STANDARD_0_3),
            ("Feeling down, depressed, or hopeless", STANDARD_0_3),
            ("Trouble falling or staying asleep, or sleeping too much", STANDARD_0_3),
            ("Feeling tired or having little energy", STANDARD_0_3),
            ("Poor appetite or overeating", STANDARD_0_3),
            ("Feeling bad about yourself, or that you are a failure, or have let yourself or your family down", STANDARD_0_3),
            ("Trouble concentrating on things, such as reading or watching television", STANDARD_0_3),
            ("Moving or speaking so slowly that other people could have noticed, or being so fidgety/restless that you have been moving a lot more than usual", STANDARD_0_3),
            ("Thoughts that you would be better off dead, or of hurting yourself in some way", STANDARD_0_3),
        ],
    },
    AssessmentCode.GAD7: {
        "name": "GAD-7 (Generalized Anxiety Disorder Scale)",
        "description": "A 7-item screening tool for the presence and severity of anxiety symptoms.",
        "instructions": "Over the last 2 weeks, how often have you been bothered by the following problems?",
        "max_score": 21,
        "questions": [
            ("Feeling nervous, anxious, or on edge", STANDARD_0_3),
            ("Not being able to stop or control worrying", STANDARD_0_3),
            ("Worrying too much about different things", STANDARD_0_3),
            ("Trouble relaxing", STANDARD_0_3),
            ("Being so restless that it is hard to sit still", STANDARD_0_3),
            ("Becoming easily annoyed or irritable", STANDARD_0_3),
            ("Feeling afraid, as if something awful might happen", STANDARD_0_3),
        ],
    },
    AssessmentCode.STRESS: {
        "name": "Perceived Stress Scale",
        "description": "A 10-item measure of the degree to which situations in your life are perceived as stressful.",
        "instructions": "In the last month, how often have you felt or thought the following?",
        "max_score": 40,
        "questions": [
            ("Been upset because of something that happened unexpectedly", FREQUENCY_0_4),
            ("Felt that you were unable to control the important things in your life", FREQUENCY_0_4),
            ("Felt nervous and stressed", FREQUENCY_0_4),
            ("Felt confident about your ability to handle your personal problems", FREQUENCY_0_4_REVERSED),
            ("Felt that things were going your way", FREQUENCY_0_4_REVERSED),
            ("Found that you could not cope with all the things that you had to do", FREQUENCY_0_4),
            ("Been able to control irritations in your life", FREQUENCY_0_4_REVERSED),
            ("Felt that you were on top of things", FREQUENCY_0_4_REVERSED),
            ("Been angered because of things that were outside of your control", FREQUENCY_0_4),
            ("Felt difficulties were piling up so high that you could not overcome them", FREQUENCY_0_4),
        ],
    },
    AssessmentCode.BURNOUT: {
        "name": "Burnout Assessment",
        "description": "A 10-item self-report measure of exhaustion, cynicism, and reduced sense of accomplishment.",
        "instructions": "In the last month, how often have you felt the following about your work or daily responsibilities?",
        "max_score": 40,
        "questions": [
            ("I feel emotionally drained by my responsibilities", FREQUENCY_0_4),
            ("I feel used up at the end of the day", FREQUENCY_0_4),
            ("I feel tired when I get up and have to face another day", FREQUENCY_0_4),
            ("I feel burned out from my responsibilities", FREQUENCY_0_4),
            ("I feel frustrated by my daily tasks", FREQUENCY_0_4),
            ("I feel I'm working too hard", FREQUENCY_0_4),
            ("I don't really care what happens to some of the things I'm responsible for", FREQUENCY_0_4),
            ("I've become more callous toward people since taking on my current responsibilities", FREQUENCY_0_4),
            ("I feel I'm positively influencing other people's lives through what I do", FREQUENCY_0_4_REVERSED),
            ("I feel exhilarated after accomplishing my tasks", FREQUENCY_0_4_REVERSED),
        ],
    },
    AssessmentCode.SELF_ESTEEM: {
        "name": "Self-Esteem Scale",
        "description": "A 10-item measure of global self-worth, based on the Rosenberg Self-Esteem Scale.",
        "instructions": "How much do you agree or disagree with each statement below?",
        "max_score": 30,
        "questions": [
            ("On the whole, I am satisfied with myself", AGREEMENT_0_3),
            ("At times, I think I am no good at all", AGREEMENT_0_3_REVERSED),
            ("I feel that I have a number of good qualities", AGREEMENT_0_3),
            ("I am able to do things as well as most other people", AGREEMENT_0_3),
            ("I feel I do not have much to be proud of", AGREEMENT_0_3_REVERSED),
            ("I certainly feel useless at times", AGREEMENT_0_3_REVERSED),
            ("I feel that I'm a person of worth, at least on an equal plane with others", AGREEMENT_0_3),
            ("I wish I could have more respect for myself", AGREEMENT_0_3_REVERSED),
            ("All in all, I am inclined to feel that I am a failure", AGREEMENT_0_3_REVERSED),
            ("I take a positive attitude toward myself", AGREEMENT_0_3),
        ],
    },
}


class Command(BaseCommand):
    help = "Seeds/updates the standardized assessment instruments (PHQ-9, GAD-7, Stress, Burnout, Self-esteem)."

    @transaction.atomic
    def handle(self, *args, **options):
        for code, spec in ASSESSMENTS.items():
            assessment_type, created = AssessmentType.objects.update_or_create(
                code=code,
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "instructions": spec["instructions"],
                    "max_score": spec["max_score"],
                    "is_active": True,
                },
            )
            for order, (text, options) in enumerate(spec["questions"], start=1):
                AssessmentQuestion.objects.update_or_create(
                    assessment_type=assessment_type,
                    order=order,
                    defaults={"text": text, "options": options},
                )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} {assessment_type.name} ({len(spec['questions'])} questions)"))

        self.stdout.write(self.style.SUCCESS("Assessment seed complete."))
