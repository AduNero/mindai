from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


class GoogleTokenError(Exception):
    """The credential wasn't a valid, current Google ID token for this app's client ID."""


# Reused across requests — verify_oauth2_token caches Google's public keys
# internally on this, so only the first call per process actually fetches
# them over the network.
_google_request = google_requests.Request()


def verify_google_id_token(credential):
    """
    Verifies a Google Identity Services ID token: checks the cryptographic
    signature against Google's public keys, that it hasn't expired, and
    that it was issued for *this* app (`aud` must match GOOGLE_CLIENT_ID) —
    without that last check, a token meant for a totally different Google
    app would also pass verification. Raises GoogleTokenError on any
    failure; on success returns the token's claims (email, given_name,
    family_name, email_verified, sub, ...).
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleTokenError("Google Sign-In is not configured.")

    try:
        return id_token.verify_oauth2_token(credential, _google_request, settings.GOOGLE_CLIENT_ID)
    except ValueError as exc:
        raise GoogleTokenError(str(exc)) from exc
