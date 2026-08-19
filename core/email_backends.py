import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class ResendBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, "RESEND_API_KEY", None)
        if not api_key:
            if not self.fail_silently:
                raise RuntimeError("RESEND_API_KEY manquant")
            return 0

        sent = 0
        for message in email_messages:
            try:
                payload = {
                    "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.body,
                }
                response = requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=15,
                )
                response.raise_for_status()
                sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
        return sent