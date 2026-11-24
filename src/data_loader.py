"""Read contacts and reminders from CSV files using Pandas."""
import pandas as pd

CONTACT_COLUMNS = {"contact_id", "name", "email", "department"}
REMINDER_COLUMNS = {"reminder_id", "contact_id", "title", "template", "send_at", "details", "repeat"}


def _read_csv(path, required_columns: set) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
    return df.apply(lambda col: col.str.strip())


def load_contacts(path) -> dict:
    """Return {contact_id: {name, email, department, ...}}."""
    df = _read_csv(path, CONTACT_COLUMNS)
    return {row["contact_id"]: row.to_dict() for _, row in df.iterrows()}


def load_reminders(path) -> list:
    """Return a list of reminder dicts. 'send_at' becomes a Timestamp (NaT if invalid)."""
    df = _read_csv(path, REMINDER_COLUMNS)
    reminders = []
    for _, row in df.iterrows():
        r = row.to_dict()
        r["send_at"] = pd.to_datetime(r["send_at"], errors="coerce")
        r["repeat"] = r["repeat"].lower() or "none"
        r["done"] = False  # runtime state
        reminders.append(r)
    return reminders
