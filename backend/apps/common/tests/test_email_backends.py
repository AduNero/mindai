from unittest.mock import Mock, patch

import pytest
import requests
from django.core.mail import EmailMessage

from apps.common.email_backends import BrevoBackend, ResendBackend, SendGridBackend


def _message():
    return EmailMessage(
        subject="Your code",
        body="Your code is 123456.",
        from_email="MindCare AI <no-reply@mindcare.ai>",
        to=["user@example.com"],
    )


class TestResendBackend:
    def test_send_messages_posts_to_resend_api(self, settings):
        settings.RESEND_API_KEY = "test-key"
        backend = ResendBackend()

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=200, raise_for_status=lambda: None)
            sent = backend.send_messages([_message()])

        assert sent == 1
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.resend.com/emails"
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["json"]["to"] == ["user@example.com"]
        assert kwargs["json"]["subject"] == "Your code"

    def test_missing_api_key_raises_when_not_fail_silently(self, settings):
        settings.RESEND_API_KEY = ""
        backend = ResendBackend(fail_silently=False)

        with pytest.raises(ValueError):
            backend.send_messages([_message()])

    def test_missing_api_key_is_swallowed_when_fail_silently(self, settings):
        settings.RESEND_API_KEY = ""
        backend = ResendBackend(fail_silently=True)

        assert backend.send_messages([_message()]) == 0

    def test_request_failure_raises_when_not_fail_silently(self, settings):
        settings.RESEND_API_KEY = "test-key"
        backend = ResendBackend(fail_silently=False)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            with pytest.raises(requests.RequestException):
                backend.send_messages([_message()])

    def test_request_failure_is_swallowed_when_fail_silently(self, settings):
        settings.RESEND_API_KEY = "test-key"
        backend = ResendBackend(fail_silently=True)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            assert backend.send_messages([_message()]) == 0

    def test_no_messages_is_a_noop(self, settings):
        settings.RESEND_API_KEY = "test-key"
        backend = ResendBackend()
        assert backend.send_messages([]) == 0


class TestSendGridBackend:
    def test_send_messages_posts_to_sendgrid_api(self, settings):
        settings.SENDGRID_API_KEY = "test-key"
        backend = SendGridBackend()

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=202, raise_for_status=lambda: None)
            sent = backend.send_messages([_message()])

        assert sent == 1
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.sendgrid.com/v3/mail/send"
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["json"]["personalizations"][0]["to"] == [{"email": "user@example.com"}]
        assert kwargs["json"]["subject"] == "Your code"

    def test_splits_display_name_from_from_email(self, settings):
        """SendGrid rejects the combined "Name <email>" format Resend accepts as-is."""
        settings.SENDGRID_API_KEY = "test-key"
        backend = SendGridBackend()

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=202, raise_for_status=lambda: None)
            backend.send_messages([_message()])

        sent_from = mock_post.call_args.kwargs["json"]["from"]
        assert sent_from == {"email": "no-reply@mindcare.ai", "name": "MindCare AI"}

    def test_missing_api_key_raises_when_not_fail_silently(self, settings):
        settings.SENDGRID_API_KEY = ""
        backend = SendGridBackend(fail_silently=False)

        with pytest.raises(ValueError):
            backend.send_messages([_message()])

    def test_missing_api_key_is_swallowed_when_fail_silently(self, settings):
        settings.SENDGRID_API_KEY = ""
        backend = SendGridBackend(fail_silently=True)

        assert backend.send_messages([_message()]) == 0

    def test_request_failure_raises_when_not_fail_silently(self, settings):
        settings.SENDGRID_API_KEY = "test-key"
        backend = SendGridBackend(fail_silently=False)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            with pytest.raises(requests.RequestException):
                backend.send_messages([_message()])

    def test_request_failure_is_swallowed_when_fail_silently(self, settings):
        settings.SENDGRID_API_KEY = "test-key"
        backend = SendGridBackend(fail_silently=True)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            assert backend.send_messages([_message()]) == 0

    def test_no_messages_is_a_noop(self, settings):
        settings.SENDGRID_API_KEY = "test-key"
        backend = SendGridBackend()
        assert backend.send_messages([]) == 0


class TestBrevoBackend:
    def test_send_messages_posts_to_brevo_api(self, settings):
        settings.BREVO_API_KEY = "test-key"
        backend = BrevoBackend()

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=201, raise_for_status=lambda: None)
            sent = backend.send_messages([_message()])

        assert sent == 1
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.brevo.com/v3/smtp/email"
        assert kwargs["headers"]["api-key"] == "test-key"
        assert kwargs["json"]["to"] == [{"email": "user@example.com"}]
        assert kwargs["json"]["subject"] == "Your code"

    def test_splits_display_name_from_from_email(self, settings):
        settings.BREVO_API_KEY = "test-key"
        backend = BrevoBackend()

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=201, raise_for_status=lambda: None)
            backend.send_messages([_message()])

        assert mock_post.call_args.kwargs["json"]["sender"] == {
            "email": "no-reply@mindcare.ai",
            "name": "MindCare AI",
        }

    def test_missing_api_key_raises_when_not_fail_silently(self, settings):
        settings.BREVO_API_KEY = ""
        backend = BrevoBackend(fail_silently=False)

        with pytest.raises(ValueError):
            backend.send_messages([_message()])

    def test_missing_api_key_is_swallowed_when_fail_silently(self, settings):
        settings.BREVO_API_KEY = ""
        backend = BrevoBackend(fail_silently=True)

        assert backend.send_messages([_message()]) == 0

    def test_request_failure_raises_when_not_fail_silently(self, settings):
        settings.BREVO_API_KEY = "test-key"
        backend = BrevoBackend(fail_silently=False)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            with pytest.raises(requests.RequestException):
                backend.send_messages([_message()])

    def test_request_failure_is_swallowed_when_fail_silently(self, settings):
        settings.BREVO_API_KEY = "test-key"
        backend = BrevoBackend(fail_silently=True)

        with patch("apps.common.email_backends.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network is unreachable")
            assert backend.send_messages([_message()]) == 0

    def test_no_messages_is_a_noop(self, settings):
        settings.BREVO_API_KEY = "test-key"
        backend = BrevoBackend()
        assert backend.send_messages([]) == 0
