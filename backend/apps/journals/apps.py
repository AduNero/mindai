from django.apps import AppConfig


class JournalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.journals"
    verbose_name = "Journal Module"

    def ready(self):
        # Signal handlers (e.g. triggering AI sentiment/risk analysis on
        # save) are wired up in Phase 3/5 once the AI engine is available.
        pass
