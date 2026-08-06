import pytest

from apps.users.google_oauth import GoogleTokenError, verify_google_id_token


class TestVerifyGoogleIdToken:
    def test_rejects_malformed_token(self, settings):
        settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        with pytest.raises(GoogleTokenError):
            verify_google_id_token("not-a-real-jwt")

    def test_raises_when_not_configured(self, settings):
        settings.GOOGLE_CLIENT_ID = ""
        with pytest.raises(GoogleTokenError):
            verify_google_id_token("anything")
