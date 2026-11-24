"""Create the CSV report (and a failed-only CSV) and print a summary."""
import logging

import pandas as pd

from .config import OUTPUTS_DIR

log = logging.getLogger("email_automation")
COLUMNS = ["timestamp", "reminder_id", "name", "email", "subject", "status", "error"]


def save_report(results: list):
    stamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(results, columns=COLUMNS)
    report_path = OUTPUTS_DIR / f"report_{stamp}.csv"
    df.to_csv(report_path, index=False)

    failed = df[df["status"] == "FAILED"]
    if not failed.empty:
        failed.to_csv(OUTPUTS_DIR / f"failed_{stamp}.csv", index=False)
    return report_path


def print_summary(results: list, still_scheduled: int = 0) -> None:
    df = pd.DataFrame(results, columns=COLUMNS)
    counts = df["status"].value_counts().to_dict()
    log.info("=" * 55)
    log.info("SUMMARY  total=%d | sent=%d | dry_run=%d | failed=%d | still scheduled=%d",
             len(df), counts.get("SENT", 0), counts.get("DRY_RUN", 0),
             counts.get("FAILED", 0), still_scheduled)
    log.info("=" * 55)
