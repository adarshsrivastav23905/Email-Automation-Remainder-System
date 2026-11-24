# How to Run, GitHub Upload, Proof Plan, Screenshots (Sections 9, 10, 12, 13)

## 9. How to Run
```bash
python main.py --all          # dry-run, everything
python main.py                # dry-run, only due reminders
python main.py --schedule --interval 10   # scheduler loop
python main.py --live --all   # actual email mode (after .env is set)
```
**Expected terminal output (dry-run):** see README "Sample Output". Generated: `logs/email_automation.log`, `outputs/report_YYYYMMDD_HHMMSS.csv`, and `outputs/failed_*.csv` when something failed.

**Actual email mode checklist:** 1) `.env` filled with a Gmail App Password; 2) contacts changed to addresses you own; 3) run `--live --all`; 4) check inbox and the `SENT` rows. Authentication errors mean wrong App Password.

## 10. GitHub Upload Steps
1. Create a new repo on github.com → name: **`Email-Automation-Reminder-System`**, public, no README (we have one).
2. In the project folder:
```bash
git init
git add .
git status          # CHECK: .env must NOT appear
git commit -m "Initial commit: project structure and dummy data"
git branch -M main
git remote add origin https://github.com/<your-username>/Email-Automation-Reminder-System.git
git push -u origin main
```
3. Later: add screenshots to `images/`, then `git add . && git commit -m "..." && git push`.

**Description:** *Python email automation and reminder system with CSV contacts, templates, SMTP, scheduling, dry-run mode, logging and CSV reports.*
**Topics/tags:** `python` `automation` `email-automation` `smtp` `pandas` `scheduler` `reminder-system` `logging` `csv` `student-project`

**Safety:** never upload passwords; commit `.env.example`, not `.env`; `.gitignore` already excludes `.env`, `venv/`, logs and runtime reports. If you ever commit a secret by mistake, **revoke the App Password immediately**; deleting the file later does not remove it from history.

## 12. Day-wise Proof Plan
| Day | Work | Commit message | Screenshot |
|---|---|---|---|
| 1 | Setup, folders, venv, requirements, .gitignore | `chore: project structure and dependencies` | Project folder tree |
| 2 | contacts.csv, reminders.csv, templates | `feat: add sample contacts, reminders and templates` | CSV in editor, template |
| 3 | data_loader, template_engine | `feat: CSV loading and email personalization` | Rendered email preview |
| 4 | mailer (dry-run + SMTP), scheduler | `feat: SMTP sender, dry-run mode and scheduler` | Dry-run terminal |
| 5 | logging, reporter, tests | `feat: logging, CSV reports and unit tests` | Log file, report CSV, pytest passing |
| 6 | README, docs, screenshots, sample outputs | `docs: README, guides and screenshots` | GitHub repo preview |

## 13. Screenshots / Outputs to Capture (save in `images/`)
1. `project_folder.png`: VS Code explorer showing the structure
2. `contacts_csv.png`: `data/contacts.csv`
3. `email_template.png`: one file from `templates/`
4. `dry_run_terminal.png`: output of `python main.py --all`
5. `reminder_schedule.png`: output of `python main.py --schedule --interval 10`
6. `log_file.png`: `logs/email_automation.log` with SENT/DRY_RUN and FAILED lines
7. `report_csv.png`: report opened in Excel/VS Code
8. `pytest.png`: `python -m pytest` passing
9. `github_repo.png`: the repo home page with README preview

Hide any real email addresses or usernames before taking screenshots.
