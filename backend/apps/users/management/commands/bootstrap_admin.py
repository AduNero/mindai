import os

from django.core.management.base import BaseCommand

from apps.users.models import Role, User


class Command(BaseCommand):
    """
    Idempotent superuser creation, driven entirely by env vars — safe to
    run on every deploy (e.g. chained into a platform's start command)
    rather than needing one-off shell access, which isn't available on
    some free-tier hosting plans. No-ops quietly if DJANGO_SUPERUSER_EMAIL/
    DJANGO_SUPERUSER_PASSWORD aren't set, so it's harmless to leave in the
    default start command everywhere else too.
    """

    help = "Creates (or promotes) a superuser from DJANGO_SUPERUSER_* env vars. Safe to re-run."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not email or not password:
            self.stdout.write("DJANGO_SUPERUSER_EMAIL/PASSWORD not set — skipping.")
            return

        first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
        last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "User")

        user = User.objects.filter(email__iexact=email).first()
        if user:
            user.set_password(password)
            user.role = Role.ADMIN
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.is_email_verified = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated existing superuser: {email}"))
        else:
            User.objects.create_superuser(
                email=email, password=password, first_name=first_name, last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {email}"))
