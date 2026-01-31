import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)


def send_email(subject: str, to: str, body: str) -> None:
    """Send a simple plain-text email using SMTP.
    This helper is minimal; in production use a proper mail delivery service.
    """
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        # If mail isn't configured, raise so caller can handle gracefully
        raise RuntimeError('SMTP not configured (SMTP_HOST/SMTP_USER/SMTP_PASS)')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)
