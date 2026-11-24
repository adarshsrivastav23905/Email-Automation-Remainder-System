# Project Guide (Sections 1–6 and 8)

## 1. Project Explanation

**What is it?** An Email Automation & Reminder System is software that sends the right email to the right person at the right time, without a human clicking "send".

**Problem it solves:** Repetitive communication is slow, easy to forget, inconsistent and untraceable.

**Why companies use it**
| Team | Use |
|---|---|
| HR | Interview schedules, onboarding steps, document deadlines |
| Sales | Follow-ups after demos, meeting alerts |
| Trainers | Class and webinar reminders (fewer no-shows) |
| Finance | Payment due and overdue reminders |
| Operations | Task notifications, report deadlines |

**Simple explanation:** It is a digital assistant with a contact list, a message template and a calendar. When a reminder's time arrives, it fills in the person's name and details, sends the email, and writes down whether it worked.

**Technical explanation:** A Python program loads CSV data into Pandas, validates it, renders `{{placeholder}}` templates, uses a scheduler (`schedule` library plus datetime comparison) to find due reminders, builds `EmailMessage` objects and delivers them via `smtplib` (SSL/STARTTLS). Each attempt is logged and written to a CSV report. Dry-run mode swaps the network call for a log line.

**Workflow**
```
contact list → message template → scheduled reminder → email sending → status tracking → report generation
```

## 2. Tech Stack Options

| | Option A (Easy) | Option B (Intermediate) | Option C (Advanced) |
|---|---|---|---|
| Tools | Python, smtplib, csv, datetime, logging | **Pandas, smtplib, email.message, schedule, logging, dotenv, argparse** | FastAPI, SQLAlchemy, APScheduler, Jinja2, aiosmtplib, RRULE, Next.js |
| Difficulty | Beginner | Beginner–Intermediate | Advanced |
| Output | Console log | Logs + CSV report + dry-run + tests (+ optional Streamlit) | REST API, database, dashboard, open/click tracking |

**Best for students: Option B.** It covers the course topics, is fully runnable offline, and is easy to explain in interviews. Option C is a great "version 2" roadmap (see Future Improvements) once B is on GitHub.

## 3. Architecture

```
 INPUT                         PROCESSING                              OUTPUT
┌──────────────┐   ┌──────────────────────────────────────────┐   ┌─────────────────────┐
│contacts.csv  │──▶│ data_loader  (Pandas, validation)        │   │ logs/…log           │
│reminders.csv │──▶│        │                                 │   │ outputs/report_*.csv│
│templates/*.txt│─▶│ scheduler   (is it due? repeat?)         │──▶│ outputs/failed_*.csv│
│.env (secrets)│──▶│        │                                 │   │ console summary     │
└──────────────┘   │ template_engine (personalize)            │   └─────────────────────┘
                   │        │                                 │
                   │ mailer  ── dry-run? ──▶ log only         │
                   │        └─ live ──▶ SMTP server           │
                   │        │                                 │
                   │ reporter (status tracking)               │
                   └──────────────────────────────────────────┘
```
**Data flow:** CSV rows → dicts → for each due reminder, merge contact + reminder fields → render subject/body → send or simulate → result dict (SENT / DRY_RUN / FAILED) → log line + report row.

## 4. Implementation Plan (10 phases)

| Phase | What | Why | Expected output | Beginner mistakes |
|---|---|---|---|---|
| 1 Setup | Install Python 3.10+, VS Code, Git | Reproducible environment | `python --version` works | Forgetting "Add to PATH" on Windows |
| 2 Folders | Create the structure in §5 | Clean, reviewable repo | Folders visible | Putting everything in one file |
| 3 Contact CSV | `contacts.csv` with dummy people | Input data | 6 rows | Real personal data; spaces in headers |
| 4 Template | `.txt` files with `{{name}}` | Reuse and personalization | 5 templates | Typos in placeholders |
| 5 SMTP config | `.env` + `.env.example` | Safe credentials | Settings load | Hard-coding passwords; using the normal Gmail password instead of an App Password |
| 6 Personalization | `render()` merges data | Each email feels individual | Subject/body with real names | Not handling missing values |
| 7 Scheduling | Compare `send_at` to now; repeat logic | Right time delivery | Due vs not-due reminders | Comparing text instead of datetimes; time zone confusion |
| 8 Sending | `EmailSender` with dry-run | The core action | `[DRY-RUN] Would send…` | Testing live too early; no try/except |
| 9 Logging & report | `logging` + CSV | Audit trail and proof | Log file + report CSV | Only `print()`; overwriting reports |
| 10 GitHub | Commit, push, README, screenshots | Proof of work | Public repo | Pushing `.env`; empty README |

## 5. Folder Structure
- `data/` input CSVs (dummy only)
- `templates/` email text templates
- `src/` reusable modules (one responsibility each)
- `outputs/` generated reports
- `logs/` run history
- `images/` screenshots for the README
- `docs/` guides, sample log
- `tests/` pytest tests
- `main.py` entry point, `requirements.txt` dependencies, `.gitignore` files Git must skip, `.env.example` safe config template

## 6. Installation Guide
**Windows**
```bat
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
**Mac/Linux**
```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Libraries: pandas, schedule, python-dotenv, pytest (`smtplib`, `email`, `logging`, `datetime` ship with Python).

## 8. Virtual Simulation (safe testing)

1. **Dummy contacts:** use `example.com` addresses (reserved for testing, they can never reach a real inbox).
2. **Sample reminders:** `data/reminders.csv` includes meetings, task, webinar, payment, follow-up, plus deliberate errors (invalid email `R005`, unknown contact `R007`) and a future reminder (`R008`).
3. **Templates:** see `templates/`.
4. **Dry-run:** `python main.py --all`. It is the default, so you cannot send by accident.
5. **Logs and reports:** `logs/email_automation.log` and `outputs/report_<time>.csv`; failures also go to `outputs/failed_<time>.csv`.
6. **Real-company equivalent:** the CSVs become a CRM/HR database, the script runs on a server (cron, Task Scheduler or a worker container), SMTP becomes a provider like SendGrid or SES, and logs feed a monitoring dashboard.
7. **Optional real test:** put your own two email addresses in `contacts.csv`, fill `.env`, run `python main.py --live --all`.

**Screenshots to capture:** see `docs/HOW_TO_RUN_AND_GITHUB.md` §13.
**Upload to GitHub:** code, dummy CSVs, templates, `outputs/sample_report.csv`, `docs/sample_log.txt`, screenshots.
**Never upload:** `.env`, passwords/App Passwords, real customer emails or phone numbers, logs containing real addresses, API keys.
