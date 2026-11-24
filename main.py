"""Email Automation & Reminder System - command line entry point.

Examples
--------
python main.py --all                 # dry-run, process EVERY reminder (safe demo)
python main.py                       # dry-run, only reminders that are due now
python main.py --schedule            # dry-run, keep checking every 30 seconds
python main.py --live --all          # REAL emails (needs .env credentials)
"""
import argparse
import sys

import pandas as pd

from src.config import DATA_DIR, get_smtp_settings
from src.data_loader import load_contacts, load_reminders
from src.logger_setup import setup_logging
from src.mailer import EmailSender
from src.reporter import print_summary, save_report
from src.scheduler import process_due_reminders, run_scheduler


def parse_args():
    p = argparse.ArgumentParser(description="Email Automation & Reminder System")
    p.add_argument("--live", action="store_true", help="Send REAL emails (default is dry-run)")
    p.add_argument("--all", action="store_true", help="Ignore send_at and process every reminder now")
    p.add_argument("--schedule", action="store_true", help="Keep running and check periodically")
    p.add_argument("--interval", type=int, default=30, help="Seconds between checks in --schedule mode")
    p.add_argument("--contacts", default=str(DATA_DIR / "contacts.csv"))
    p.add_argument("--reminders", default=str(DATA_DIR / "reminders.csv"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    log = setup_logging()
    dry_run = not args.live
    log.info("Starting in %s mode", "DRY-RUN (no emails will be sent)" if dry_run else "LIVE")

    try:
        contacts = load_contacts(args.contacts)
        reminders = load_reminders(args.reminders)
        sender = EmailSender(get_smtp_settings(), dry_run=dry_run)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        log.error("Setup problem: %s", exc)
        return 1
    log.info("Loaded %d contacts and %d reminders", len(contacts), len(reminders))

    if args.schedule:
        results = run_scheduler(reminders, contacts, sender, args.interval)
    else:
        results = process_due_reminders(reminders, contacts, sender, pd.Timestamp.now(), args.all)

    not_due = sum(1 for r in reminders if not r["done"])
    if results:
        report = save_report(results)
        print_summary(results, not_due)
        log.info("Report saved: %s", report)
    else:
        log.info("Nothing was due. Try --all to process every reminder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
