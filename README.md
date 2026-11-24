# 📧 Email Automation & Reminder System

A beginner-friendly, industry-style **Python** project that reads contacts and reminders from CSV files, personalizes email templates, schedules reminders, sends emails over **SMTP** (or simulates them in a safe **dry-run mode**), and produces logs plus a CSV report of sent and failed emails.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Pandas](https://img.shields.io/badge/Pandas-CSV-green) ![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)

## Problem Statement
Teams waste hours manually sending repetitive messages: meeting alerts, invoice reminders, webinar invites, follow-ups. Manual sending causes missed deadlines, inconsistent wording and no audit trail. This project automates that workflow.

## Industry Relevance
| Team | Example use |
|---|---|
| HR | Interview schedules, onboarding nudges, policy follow-ups |
| Sales | Follow-ups, meeting reminders |
| Operations / Admin | Task deadlines, report submission alerts |
| Finance | Payment due reminders |
| Trainers / Educators | Class and webinar reminders |

## Features
- Reads **contacts.csv** and **reminders.csv** with Pandas
- `{{placeholder}}` templates (5 included), with a clear error on missing values
- **Dry-run by default**: nothing is sent unless you pass `--live`
- Real SMTP sending (Gmail App Password supported), with retries
- Email validation and per-reminder error handling (one failure never stops the batch)
- Recurring reminders (`daily` / `weekly`) and a periodic scheduler (`--schedule`)
- Console + file logging, a timestamped **CSV report**, and a separate **failed-emails CSV**
- Credentials via **environment variables** only (`.env` is git-ignored)
- Unit tests with pytest

## Tech Stack
Python 3.10+, Pandas, `smtplib`, `email.message`, `schedule`, `logging`, `argparse`, `python-dotenv`, `pytest`

## Folder Structure
```
Email-Automation-Reminder-System/
├── data/        contacts.csv, reminders.csv
├── templates/   email templates (.txt)
├── src/         config, data_loader, template_engine, mailer, scheduler, reporter, logger_setup
├── outputs/     generated CSV reports (sample_report.csv committed)
├── logs/        email_automation.log
├── images/      screenshots for this README
├── docs/        full guide, GitHub steps, interview prep, sample log
├── tests/       pytest unit tests
├── main.py      entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup
```bash
# 1. Clone
git clone https://github.com/<your-username>/Email-Automation-Reminder-System.git
cd Email-Automation-Reminder-System

# 2. Virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# 3. Install
pip install -r requirements.txt
```

## Environment Variables (only needed for live mode)
```bash
cp .env.example .env      # Windows: copy .env.example .env
```
Edit `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_16_char_app_password
SENDER_NAME=Automation Bot
```
Never commit `.env`. For Gmail, enable 2-Step Verification and create an **App Password**.

## How to Run
```bash
python main.py --all            # safe dry-run of every reminder (recommended first run)
python main.py                  # dry-run, only reminders whose send_at has passed
python main.py --schedule       # keep checking every 30s (Ctrl+C to stop)
python main.py --live --all     # REAL emails (use your own test addresses!)
python -m pytest                # run tests
```

## Sample Output
```
INFO    | Starting in DRY-RUN (no emails will be sent) mode
INFO    | Loaded 6 contacts and 8 reminders
INFO    | [DRY-RUN] Would send to aarav.sharma@example.com | Subject: Meeting Reminder: Weekly Sales Review
INFO    | [DRY-RUN] Would send to priya.nair@example.com | Subject: Meeting Reminder: Interview Panel Briefing
ERROR   | [FAILED] R005 -> Invalid email address 'ravi.kumar-example.com'
ERROR   | [FAILED] R007 -> Unknown contact_id 'C999'
INFO    | SUMMARY  total=8 | sent=0 | dry_run=6 | failed=2 | still scheduled=1
```
See [`outputs/sample_report.csv`](outputs/sample_report.csv) and [`docs/sample_log.txt`](docs/sample_log.txt).

## Screenshots
| | |
|---|---|
| Dry-run terminal | ![dry run](images/dry_run_terminal.png) |
| Report CSV | ![report](images/report_csv.png) |
| Log file | ![log](images/log_file.png) |

## Learning Outcomes
- File handling and data processing with Pandas
- Working with SMTP and the `email` package
- Template-based personalization
- Scheduling and recurring jobs
- Error handling, logging and reporting
- Secure secret management and GitHub best practices
- Writing unit tests

## Future Improvements
SQLite/Postgres storage, FastAPI + dashboard (Next.js or Streamlit), RRULE recurrence, open/click tracking, unsubscribe handling, rate limiting, SMS/WhatsApp, Google Calendar invites, cloud deployment.

## Disclaimer
Educational project. Use dummy data or your own consent-based test addresses only.
