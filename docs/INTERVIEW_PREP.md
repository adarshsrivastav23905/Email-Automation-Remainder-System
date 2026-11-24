# Interview Preparation (Section 14)

### 1. Explain your project.
**Answer:** "I built an Email Automation & Reminder System in Python. It reads contacts and reminders from CSV files using Pandas, personalizes email templates with each person's details, checks which reminders are due using a scheduler, and sends emails through SMTP. Every attempt is logged, and the system generates a CSV report with sent and failed emails. It has a dry-run mode so it can be tested safely, keeps credentials in environment variables, and has unit tests. It reduces manual follow-up work for HR, sales, trainers and operations teams."

**HR / non-technical version:** "I created a system that automatically sends reminder emails at the right time, so teams don't have to remember and write every follow-up by hand. It also keeps a record of what was sent and what failed."

**Technical version:** "Modular pipeline: `data_loader` → `scheduler` → `template_engine` → `mailer` → `reporter`. SMTP over SSL/STARTTLS with retries, per-record exception isolation, recurring reminders, argparse CLI, logging to console and file."

### 2. What problem does it solve?
Manual, repetitive, error-prone communication: missed deadlines, inconsistent messages, no audit trail. Automation makes it reliable, consistent and traceable.

### 3. Which technologies did you use and why?
Pandas for CSV reading/cleaning/reporting, `smtplib` + `email.message` for building and sending mail, `schedule` + `datetime` for timing, `logging` for observability, `python-dotenv` for secrets, `argparse` for modes, `pytest` for tests.

### 4. How does personalization work?
Templates contain `{{name}}`-style placeholders. For each reminder I merge the contact row and reminder row into one dictionary and replace placeholders with a regex. A missing value raises an error that is logged as FAILED instead of sending a broken email.

### 5. What is SMTP?
Simple Mail Transfer Protocol, the standard for sending email to a mail server. I use SMTP_SSL on port 465 (or STARTTLS on 587) with an App Password.

### 6. How do you handle errors?
Each reminder is processed inside its own try/except, so an invalid email, unknown contact, missing template or missing placeholder is logged and recorded as FAILED while the rest continue. Network errors are retried with a delay; authentication errors are not retried. Failures go to a separate `failed_*.csv`.

### 7. How did you keep it safe for GitHub?
No secrets in code; credentials come from environment variables; `.env` is in `.gitignore`; `.env.example` documents the setup; data is dummy `example.com`.

### 8. What is dry-run mode and why did you add it?
It runs the whole pipeline but replaces the actual send with a log line. It's the default, so nobody can accidentally email real people while testing. Real companies use the same idea for staging environments.

### 9. How does scheduling and recurrence work?
Each reminder has `send_at` and `repeat` (none/daily/weekly). A reminder is due when `send_at <= now`. After sending, one-off reminders are marked done; repeating ones move to their next date. `--schedule` mode runs this check every N seconds with the `schedule` library.

### 10. How would you improve it?
Store data in a database (SQLite/Postgres), persist sent-state to guarantee no duplicates after restarts (idempotency), expose a FastAPI service with a dashboard, add RRULE recurrence, time-zone aware sends, unsubscribe handling and rate limiting, open/click tracking, HTML emails, calendar invites, SMS/WhatsApp, and cloud deployment.

### Bonus questions
- **Time zones?** Currently local time; production would store UTC and convert per contact.
- **What if the script crashes mid-run?** Currently the state is in memory, so a restart could resend; persisting status in a DB fixes this.
- **How would you send 10,000 emails?** Use a provider API, batching, rate limits and a queue/worker.
