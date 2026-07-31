from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Registers MindCare AI's recurring Celery Beat tasks (idempotent — safe to re-run)."

    def handle(self, *args, **options):
        hourly, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)

        task, created = PeriodicTask.objects.update_or_create(
            name="Send due reminder notifications",
            defaults={
                "interval": hourly,
                "task": "apps.notifications.tasks.send_due_reminders",
                "enabled": True,
            },
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} periodic task: {task.name}"))
