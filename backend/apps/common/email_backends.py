import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger("apps")


class ResendBackend(BaseEmailBackend):
    """
    Sends mail via Resend's HTTP API instead of raw SMTP.

    Render's free-tier network has no outbound route to SMTP hosts at all
    (`OSError: [Errno 101] Network is unreachable` connecting to
    smtp.gmail.com:587 — confirmed live, not a guess) while normal HTTPS
    calls work fine, so an HTTP-API email provider is the only delivery
    path that actually works there.
    """

    api_url = "https://api.resend.com/emails"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, "RESEND_API_KEY", "")
        if not api_key:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not set.")
            return 0

        sent = 0
        for message in email_messages:
            payload = {
                "from": message.from_email,
                "to": list(message.to),
                "subject": message.subject,
                "text": message.body,
            }
            if message.cc:
                payload["cc"] = list(message.cc)
            if message.bcc:
                payload["bcc"] = list(message.bcc)

            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )
                response.raise_for_status()
                sent += 1
            except requests.RequestException:
                logger.exception("Resend send failed: subject=%r to=%r", message.subject, message.to)
                if not self.fail_silently:
                    raise

        return sent
