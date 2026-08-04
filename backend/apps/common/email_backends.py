import logging
from email.utils import parseaddr

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


class SendGridBackend(BaseEmailBackend):
    """
    Sends mail via SendGrid's HTTP API — the alternative to ResendBackend
    for when there's no domain to verify. Resend's sandbox mode (no
    verified domain) only delivers to the email address on the Resend
    account itself, rejecting sends to anyone else outright; SendGrid's
    "Single Sender Verification" verifies one plain email address (a
    Gmail address works fine, just click the link SendGrid emails you)
    with no DNS/domain ownership required, and lets that address send to
    any recipient.
    """

    api_url = "https://api.sendgrid.com/v3/mail/send"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, "SENDGRID_API_KEY", "")
        if not api_key:
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY is not set.")
            return 0

        sent = 0
        for message in email_messages:
            # SendGrid wants {"email": ..., "name": ...} — not the combined
            # "Name <email>" string Django's DEFAULT_FROM_EMAIL uses (which
            # Resend accepts as-is, SendGrid doesn't).
            from_name, from_email = parseaddr(message.from_email)
            from_field = {"email": from_email}
            if from_name:
                from_field["name"] = from_name

            payload = {
                "personalizations": [
                    {"to": [{"email": recipient} for recipient in message.to]}
                ],
                "from": from_field,
                "subject": message.subject,
                "content": [{"type": "text/plain", "value": message.body}],
            }
            if message.cc:
                payload["personalizations"][0]["cc"] = [{"email": r} for r in message.cc]
            if message.bcc:
                payload["personalizations"][0]["bcc"] = [{"email": r} for r in message.bcc]

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
                logger.exception("SendGrid send failed: subject=%r to=%r", message.subject, message.to)
                if not self.fail_silently:
                    raise

        return sent
