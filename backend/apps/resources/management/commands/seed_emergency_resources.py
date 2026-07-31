from django.core.management.base import BaseCommand
from django.db import transaction

from apps.resources.models import EmergencyResource

# A small starter set covering the platform's default/expected countries.
# Admins can add more via the Admin Dashboard's "Manage AI Resources" /
# Emergency Resources tooling — see apps.resources.AdminEmergencyResourceViewSet.
EMERGENCY_RESOURCES = [
    {
        "country_code": "US",
        "name": "988 Suicide & Crisis Lifeline",
        "phone_number": "988",
        "sms_number": "988",
        "website": "https://988lifeline.org",
        "description": "Free, confidential 24/7 crisis support for people in the United States.",
        "is_24_7": True,
    },
    {
        "country_code": "GH",
        "name": "Mental Health Authority Ghana Helpline",
        "phone_number": "0800-111-222",
        "website": "https://mha.gov.gh",
        "description": "National mental health support helpline for Ghana.",
        "is_24_7": True,
    },
    {
        "country_code": "GB",
        "name": "Samaritans",
        "phone_number": "116 123",
        "website": "https://www.samaritans.org",
        "description": "Free, confidential 24/7 emotional support in the UK and Ireland.",
        "is_24_7": True,
    },
    {
        "country_code": "CA",
        "name": "Talk Suicide Canada",
        "phone_number": "1-833-456-4566",
        "website": "https://talksuicide.ca",
        "description": "Bilingual, 24/7 suicide prevention support across Canada.",
        "is_24_7": True,
    },
    {
        "country_code": "AU",
        "name": "Lifeline Australia",
        "phone_number": "13 11 14",
        "website": "https://www.lifeline.org.au",
        "description": "24/7 crisis support and suicide prevention services in Australia.",
        "is_24_7": True,
    },
    {
        "country_code": "NG",
        "name": "Nigeria Suicide Prevention Initiative",
        "phone_number": "0800-800-2000",
        "website": "https://spinng.org",
        "description": "Crisis support helpline for Nigeria.",
        "is_24_7": True,
    },
    {
        "country_code": "IN",
        "name": "Kiran Mental Health Helpline",
        "phone_number": "1800-599-0019",
        "website": "https://www.mohfw.gov.in",
        "description": "Government of India's 24/7 toll-free mental health rehabilitation helpline.",
        "is_24_7": True,
    },
]


class Command(BaseCommand):
    help = "Seeds a starter set of country-level emergency/crisis resources."

    @transaction.atomic
    def handle(self, *args, **options):
        for spec in EMERGENCY_RESOURCES:
            _, created = EmergencyResource.objects.update_or_create(
                country_code=spec["country_code"],
                name=spec["name"],
                defaults=spec,
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} emergency resource: {spec['name']} ({spec['country_code']})"))

        self.stdout.write(self.style.SUCCESS("Emergency resource seed complete."))
