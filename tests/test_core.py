import pandas as pd
import pytest

from src.mailer import EmailSender, is_valid_email
from src.scheduler import process_due_reminders
from src.template_engine import render

SETTINGS = {"host": "x", "port": 465, "user": "", "password": "", "sender_name": "Bot"}


def test_render_replaces_placeholders():
    assert render("Hi {{name}}", {"name": "Asha"}) == "Hi Asha"


def test_render_missing_key_raises():
    with pytest.raises(KeyError):
        render("Hi {{nme}}", {"name": "Asha"})


def test_email_validation():
    assert is_valid_email("a.b@example.com")
    assert not is_valid_email("bad-email.com")


def _reminder(contact_id="C1", send_at="2020-01-01 09:00", repeat="none"):
    return {"reminder_id": "R1", "contact_id": contact_id, "title": "T", "template": "follow_up.txt",
            "send_at": pd.Timestamp(send_at), "details": "d", "repeat": repeat, "done": False}


CONTACTS = {"C1": {"contact_id": "C1", "name": "Asha", "email": "asha@example.com", "department": "HR"}}


def test_dry_run_marks_dry_run():
    res = process_due_reminders([_reminder()], CONTACTS, EmailSender(SETTINGS), pd.Timestamp.now())
    assert res[0]["status"] == "DRY_RUN"


def test_unknown_contact_fails_without_crashing():
    res = process_due_reminders([_reminder("C9")], CONTACTS, EmailSender(SETTINGS), pd.Timestamp.now())
    assert res[0]["status"] == "FAILED"


def test_future_reminder_is_skipped():
    res = process_due_reminders([_reminder(send_at="2999-01-01 09:00")], CONTACTS,
                                EmailSender(SETTINGS), pd.Timestamp.now())
    assert res == []


def test_weekly_reminder_moves_forward():
    r = _reminder(repeat="weekly")
    now = pd.Timestamp.now()
    process_due_reminders([r], CONTACTS, EmailSender(SETTINGS), now)
    assert not r["done"] and r["send_at"] > now
