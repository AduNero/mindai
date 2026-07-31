from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Registers the recurring LibreChat conversation sync task (idempotent — safe to re-run)."

    def handle(self, *args, **options):
        every_5_minutes, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)

        task, created = PeriodicTask.objects.update_or_create(
            name="Sync LibreChat conversations",
            defaults={
                "interval": every_5_minutes,
                "task": "apps.chat.tasks.sync_all_librechat_conversations",
                "enabled": True,
            },
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} periodic task: {task.name} (runs every 5 minutes)"))
