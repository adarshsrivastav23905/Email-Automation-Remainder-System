"""Central configuration: folder paths + SMTP settings read from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # does nothing if .env does not exist (fine for dry-run)

DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

for _folder in (OUTPUTS_DIR, LOGS_DIR):
    _folder.mkdir(exist_ok=True)


def get_smtp_settings() -> dict:
    """Read credentials from environment variables - never hard-code passwords."""
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASS", ""),
        "sender_name": os.getenv("SENDER_NAME", "Automation Bot"),
    }
