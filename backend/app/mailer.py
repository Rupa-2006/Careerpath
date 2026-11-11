"""
Sends account emails (password reset codes, forgotten usernames).

Laptop mode: with no SMTP settings, nothing is sent. The email is printed in the server window instead,
so everything can be tested before the site is online. Real sending needs SMTP_HOST and friends in .env,
for example a free Brevo account or a Gmail app password. Keys stay in .env only.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import BACKEND_DIR, get_settings

log = logging.getLogger("careerpath.mail")
LAPTOP_LOG = BACKEND_DIR / "laptop-emails.log"


def send_email(to: str, subject: str, body: str) -> bool:
    """Returns True if the email was handed over (or printed in laptop mode). Never raises."""
    settings = get_settings()
    if not settings.email_on:
        if settings.is_production:
            log.error("Email not sent: SMTP is not set up. Subject: %s", subject)
            return False
        text = (f"\n===== PathMithra email (laptop mode, not really sent) =====\nTo: {to}\nSubject: {subject}\n\n{body}\n"
                "============================================================\n")
        print(text, flush=True)
        try:   # also kept in a file next to the server; *.log files are never uploaded to GitHub
            with LAPTOP_LOG.open("a", encoding="utf-8") as file:
                file.write(text)
        except OSError:
            pass
        return True

    message = EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        return True
    except (OSError, smtplib.SMTPException) as problem:
        log.error("Email not sent: %s", problem)
        return False
