from django.core.management.base import BaseCommand
from django.db import transaction

from apps.recommendations.models import RecommendationCategory, RecommendationTemplate

TEMPLATES = [
    {
        "category": RecommendationCategory.PHYSICAL_ACTIVITY,
        "title": "Take a short walk",
        "description": "A 10-15 minute walk outside can lift your mood and clear your head.",
        "trigger_conditions": {"mood_in": ["sad", "anxious", "tired", "angry"]},
    },
    {
        "category": RecommendationCategory.PHYSICAL_ACTIVITY,
        "title": "Get moving with light exercise",
        "description": "Even 10 minutes of stretching or light exercise can help regulate stress hormones.",
        "trigger_conditions": {"mood_in": ["angry", "anxious"], "min_intensity": 6},
    },
    {
        "category": RecommendationCategory.BREATHING,
        "title": "Try a breathing exercise",
        "description": "Box breathing (4 seconds in, 4 hold, 4 out, 4 hold) can calm your nervous system in minutes.",
        "trigger_conditions": {"mood_in": ["anxious", "angry"]},
    },
    {
        "category": RecommendationCategory.MINDFULNESS,
        "title": "Listen to relaxing music",
        "description": "Calming music can lower cortisol levels and ease a racing mind.",
        "trigger_conditions": {"mood_in": ["anxious", "sad", "tired"]},
    },
    {
        "category": RecommendationCategory.NUTRITION,
        "title": "Drink some water",
        "description": "Even mild dehydration can worsen mood and concentration — grab a glass of water.",
        "trigger_conditions": {},
    },
    {
        "category": RecommendationCategory.SLEEP,
        "title": "Consider sleeping earlier tonight",
        "description": "Poor sleep and low mood often reinforce each other. An earlier bedtime tonight may help.",
        "trigger_conditions": {"mood_in": ["tired", "depressed"]},
    },
    {
        "category": RecommendationCategory.PROFESSIONAL_HELP,
        "title": "Consider talking to a counselor",
        "description": "You don't have to navigate this alone — booking a session with a counselor is a strong, proactive step.",
        "trigger_conditions": {"mood_in": ["depressed"], "min_intensity": 7},
    },
    {
        "category": RecommendationCategory.MINDFULNESS,
        "title": "Try a short guided meditation",
        "description": "A 5-10 minute guided meditation can help settle a busy or anxious mind.",
        "trigger_conditions": {"mood_in": ["anxious", "sad", "depressed"]},
    },
    {
        "category": RecommendationCategory.PHYSICAL_ACTIVITY,
        "title": "Channel your energy into exercise",
        "description": "Physical activity is one of the most effective ways to process anger and restlessness.",
        "trigger_conditions": {"mood_in": ["angry", "excited"]},
    },
    {
        "category": RecommendationCategory.ENTERTAINMENT,
        "title": "Watch something motivational",
        "description": "A short motivational video or talk can help reframe a difficult day.",
        "trigger_conditions": {"mood_in": ["sad", "depressed"]},
    },
    {
        "category": RecommendationCategory.EDUCATION,
        "title": "Read a wellness article",
        "description": "Browse the Resource Center for articles on coping strategies relevant to how you're feeling.",
        "trigger_conditions": {},
    },
    {
        "category": RecommendationCategory.SOCIAL,
        "title": "Reach out to someone you trust",
        "description": "A short conversation with a friend or family member can help you feel less alone.",
        "trigger_conditions": {"mood_in": ["sad", "depressed", "anxious"]},
    },
    # --- AI-informed tier (Phase 5): driven by journal sentiment analysis
    # and assessment severity rather than mood alone. ---
    {
        "category": RecommendationCategory.SELF_CARE,
        "title": "Your recent journal entries suggest high stress",
        "description": "Try a short break — a walk, water, or a few minutes away from screens can help reset your stress response.",
        "trigger_conditions": {"min_stress_score": 0.5},
    },
    {
        "category": RecommendationCategory.BREATHING,
        "title": "Your writing suggests you're feeling anxious",
        "description": "A grounding exercise (5 things you can see, 4 you can hear, 3 you can touch) can help in the moment.",
        "trigger_conditions": {"min_anxiety_score": 0.4},
    },
    {
        "category": RecommendationCategory.PROFESSIONAL_HELP,
        "title": "Your latest assessment suggests it's a good time to talk to someone",
        "description": "Based on your most recent assessment, connecting with a counselor could be genuinely helpful right now.",
        "trigger_conditions": {"severity_in": ["moderate", "moderately_severe", "severe"]},
    },
]


class Command(BaseCommand):
    help = "Seeds the starter RecommendationTemplate catalogue."

    @transaction.atomic
    def handle(self, *args, **options):
        for spec in TEMPLATES:
            _, created = RecommendationTemplate.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "category": spec["category"],
                    "description": spec["description"],
                    "trigger_conditions": spec["trigger_conditions"],
                    "is_active": True,
                },
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} template: {spec['title']}"))

        self.stdout.write(self.style.SUCCESS("Recommendation template seed complete."))
