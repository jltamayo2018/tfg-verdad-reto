from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridBackend(BaseEmailBackend):
    """
    Backend de email para Django usando SendGrid Web API (HTTPS).
    Evita SMTP y bloqueos/timeout en plataformas cloud.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, "SENDGRID_API_KEY", None)
        if not api_key:
            raise RuntimeError("SENDGRID_API_KEY no está configurada")

        sg = SendGridAPIClient(api_key)
        sent_count = 0

        for msg in email_messages:
            from_email = msg.from_email or settings.DEFAULT_FROM_EMAIL
            to_emails = msg.to if isinstance(msg.to, (list, tuple)) else [msg.to]
            subject = msg.subject or ""
            body = msg.body or ""

            mail = Mail(
                from_email=from_email,
                to_emails=to_emails,
                subject=subject,
                plain_text_content=body,
            )

            if isinstance(msg, EmailMultiAlternatives):
                for content, mimetype in msg.alternatives:
                    if mimetype == "text/html":
                        mail.html_content = content

            sg.send(mail)
            sent_count += 1

        return sent_count