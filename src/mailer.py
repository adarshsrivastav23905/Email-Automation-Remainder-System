"""Build and send emails. Supports a safe DRY-RUN mode (no network, nothing sent)."""
import logging
import re
import smtplib
import time
from email.message import EmailMessage
from email.utils import formataddr

log = logging.getLogger("email_automation")
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def is_valid_email(address: str) -> bool:
    return bool(EMAIL_RE.match(address or ""))


def build_message(sender_name, sender_email, to_email, subject, body) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


class EmailSender:
    def __init__(self, settings: dict, dry_run: bool = True, retries: int = 2):
        self.settings = settings
        self.dry_run = dry_run
        self.retries = retries
        if not dry_run and not (settings["user"] and settings["password"]):
            raise RuntimeError("Live mode needs SMTP_USER and SMTP_PASS in your .env file.")

    def send(self, to_email: str, subject: str, body: str) -> str:
        """Returns 'DRY_RUN' or 'SENT'. Raises an exception if sending fails."""
        sender_email = self.settings["user"] or "demo@example.com"
        msg = build_message(self.settings["sender_name"], sender_email, to_email, subject, body)

        if self.dry_run:
            log.info("[DRY-RUN] Would send to %s | Subject: %s", to_email, subject)
            return "DRY_RUN"

        last_error = None
        for attempt in range(1, self.retries + 2):
            try:
                self._deliver(msg)
                log.info("[SENT] %s | Subject: %s", to_email, subject)
                return "SENT"
            except smtplib.SMTPAuthenticationError:
                raise  # wrong password - retrying will not help
            except (smtplib.SMTPException, OSError) as exc:
                last_error = exc
                log.warning("Attempt %d failed for %s: %s", attempt, to_email, exc)
                time.sleep(2 * attempt)
        raise last_error

    def _deliver(self, msg: EmailMessage) -> None:
        s = self.settings
        if s["port"] == 465:
            with smtplib.SMTP_SSL(s["host"], s["port"], timeout=30) as server:
                server.login(s["user"], s["password"])
                server.send_message(msg)
        else:  # e.g. port 587
            with smtplib.SMTP(s["host"], s["port"], timeout=30) as server:
                server.starttls()
                server.login(s["user"], s["password"])
                server.send_message(msg)
