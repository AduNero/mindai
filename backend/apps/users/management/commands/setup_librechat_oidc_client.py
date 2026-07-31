from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = (
        "Registers (or updates) LibreChat as an OAuth2/OIDC client application, "
        "using LIBRECHAT_OIDC_CLIENT_ID/SECRET and LIBRECHAT_OIDC_REDIRECT_URI from "
        "settings. Idempotent — safe to re-run after changing the redirect URI."
    )

    def handle(self, *args, **options):
        if not settings.LIBRECHAT_OIDC_CLIENT_SECRET:
            raise CommandError(
                "LIBRECHAT_OIDC_CLIENT_SECRET is not set — generate one and add it to "
                ".env (used as both this app's client secret and LibreChat's OPENID_CLIENT_SECRET)."
            )

        application, created = Application.objects.update_or_create(
            client_id=settings.LIBRECHAT_OIDC_CLIENT_ID,
            defaults={
                "name": "LibreChat",
                "client_secret": settings.LIBRECHAT_OIDC_CLIENT_SECRET,
                "client_type": Application.CLIENT_CONFIDENTIAL,
                "authorization_grant_type": Application.GRANT_AUTHORIZATION_CODE,
                "redirect_uris": settings.LIBRECHAT_OIDC_REDIRECT_URI,
                "algorithm": Application.RS256_ALGORITHM,
                # Skip django-oauth-toolkit's "Authorize this application?" consent
                # screen — the user already trusts MindCare, and LibreChat is a
                # first-party integration, not a third-party app requesting access.
                "skip_authorization": True,
            },
        )

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} OIDC client application: {application.name}"))
        self.stdout.write(f"  client_id: {application.client_id}")
        self.stdout.write(f"  redirect_uris: {application.redirect_uris}")
        self.stdout.write(
            self.style.WARNING(
                "Set the same client_id/secret as OPENID_CLIENT_ID/OPENID_CLIENT_SECRET "
                "in LibreChat's own environment — see librechat/config/librechat.env.example."
            )
        )
