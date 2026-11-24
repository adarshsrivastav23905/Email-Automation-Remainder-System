"""Decide which reminders are due, send them, and keep track of results."""
import logging
import time
from datetime import timedelta

import pandas as pd
import schedule

from .mailer import is_valid_email
from .template_engine import load_template, render

log = logging.getLogger("email_automation")
REPEAT_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _result(r, contact, subject, status, error=""):
    return {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_id": r["reminder_id"],
        "name": contact.get("name", ""),
        "email": contact.get("email", ""),
        "subject": subject,
        "status": status,
        "error": error,
    }


def _advance(r, now):
    """After sending: one-off reminders are finished, repeating ones move to their next date."""
    delta = REPEAT_DELTAS.get(r["repeat"])
    if delta is None:
        r["done"] = True
        return
    r["send_at"] = r["send_at"] + delta
    while r["send_at"] <= now:
        r["send_at"] += delta


def process_due_reminders(reminders, contacts, sender, now, send_all=False) -> list:
    """Send every reminder that is due (or ALL of them if send_all=True, handy for demos)."""
    results = []
    for r in reminders:
        if r["done"]:
            continue
        contact = contacts.get(r["contact_id"], {})

        if pd.isna(r["send_at"]):
            r["done"] = True
            log.error("[FAILED] %s - invalid send_at date", r["reminder_id"])
            results.append(_result(r, contact, "", "FAILED", "invalid send_at date"))
            continue
        if not send_all and r["send_at"] > now:
            continue  # not due yet

        subject = ""
        try:
            if not contact:
                raise ValueError(f"Unknown contact_id '{r['contact_id']}'")
            if not is_valid_email(contact["email"]):
                raise ValueError(f"Invalid email address '{contact['email']}'")

            subject_tmpl, body_tmpl = load_template(r["template"])
            context = {
                **contact,
                "title": r["title"],
                "details": r["details"],
                "send_at": r["send_at"].strftime("%d %b %Y, %I:%M %p"),
            }
            subject = render(subject_tmpl, context)
            body = render(body_tmpl, context)
            status = sender.send(contact["email"], subject, body)
            results.append(_result(r, contact, subject, status))
        except Exception as exc:  # one bad reminder must never stop the others
            log.error("[FAILED] %s -> %s", r["reminder_id"], exc)
            results.append(_result(r, contact, subject, "FAILED", str(exc)))

        _advance(r, now)
    return results


def run_scheduler(reminders, contacts, sender, interval_seconds=30) -> list:
    """Check for due reminders every N seconds. Press Ctrl+C to stop (needed for repeating ones)."""
    all_results = []

    def tick():
        all_results.extend(process_due_reminders(reminders, contacts, sender, pd.Timestamp.now()))
        waiting = [r for r in reminders if not r["done"]]
        log.info("Scheduler tick complete. %d reminder(s) still waiting.", len(waiting))

    tick()
    schedule.every(interval_seconds).seconds.do(tick)
    try:
        while any(not r["done"] for r in reminders):
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Scheduler stopped by user.")
    schedule.clear()
    return all_results
