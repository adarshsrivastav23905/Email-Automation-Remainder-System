"""Logging to both the terminal and logs/email_automation.log."""
import logging

from .config import LOGS_DIR


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("email_automation")
    if logger.handlers:  # already configured
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(LOGS_DIR / "email_automation.log", encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger
