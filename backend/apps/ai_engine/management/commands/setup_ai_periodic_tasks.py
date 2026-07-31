from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Registers the daily wellness score / mood prediction sweep (idempotent — safe to re-run)."

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="2", day_of_week="*", day_of_month="*", month_of_year="*"
        )

        task, created = PeriodicTask.objects.update_or_create(
            name="Daily wellness score & mood prediction sweep",
            defaults={
                "crontab": schedule,
                "task": "apps.ai_engine.tasks.daily_wellness_and_prediction_sweep",
                "enabled": True,
            },
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} periodic task: {task.name} (runs daily at 02:00)"))
