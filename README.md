# 🤖 Job Application Bot

An automated job application bot that applies to jobs on **Naukri**, **Internshala**, and **Indeed** — runs 3x daily on GitHub Actions (no laptop needed).

Built with Python, Playwright, and GitHub Actions.

---

## Who is this for?
- Freshers and final year students applying for first job in India
- Anyone tired of manually applying on Naukri, Internshala, Indeed
- Developers who want to learn Playwright + GitHub Actions automation

## ✨ Features

- 🔍 Searches multiple job keywords across multiple locations
- ✅ Auto-applies via Easy Apply / Quick Apply on each platform
- 🚫 Tracks applied jobs in SQLite — never applies to the same job twice
- ☁️ Runs on GitHub Actions — works even when your laptop is off
- 🔐 Credentials stored as GitHub Secrets — never hardcoded
- 📊 Exports application history to CSV after every run
- ⚙️ Fully configurable via `config.yaml` — no code changes needed
# 🤖 Job Application Bot

An automated job application bot that applies to jobs on **Naukri**, **Internshala**, and **Indeed** — runs 3x daily on GitHub Actions (no laptop needed).

Built with Python, Playwright, and GitHub Actions.

---

## ✨ Features

- 🔍 Searches multiple job keywords across multiple locations
- ✅ Auto-applies via Easy Apply / Quick Apply on each platform
- 🚫 Tracks applied jobs in SQLite — never applies to the same job twice
- ☁️ Runs on GitHub Actions — works even when your laptop is off
- 🔐 Credentials stored as GitHub Secrets — never hardcoded
- 📊 Exports application history to CSV after every run
- ⚙️ Fully configurable via `config.yaml` — no code changes needed

---

## 🏗️ Project Structure
## 🏗️ Project Structure

```
job-bot/
├── main.py                  # Orchestrator — runs all platform bots
├── config.yaml              # Keywords, filters, applicant info
├── .env.example             # Credentials template (copy to .env locally)
job-bot/
├── main.py                  # Orchestrator — runs all platform bots
├── config.yaml              # Keywords, filters, applicant info
├── .env.example             # Credentials template (copy to .env locally)
├── requirements.txt
├── platforms/
│   ├── naukri.py            # Naukri bot
│   ├── internshala.py       # Internshala bot
│   └── indeed.py            # Indeed bot
├── utils/
│   ├── logger.py            # SQLite tracking + CSV export
│   └── browser.py           # Headless/headed mode switcher
└── .github/
    └── workflows/
        └── job_bot.yml      # GitHub Actions schedule (3x daily)
│   ├── naukri.py            # Naukri bot
│   ├── internshala.py       # Internshala bot
│   └── indeed.py            # Indeed bot
├── utils/
│   ├── logger.py            # SQLite tracking + CSV export
│   └── browser.py           # Headless/headed mode switcher
└── .github/
    └── workflows/
        └── job_bot.yml      # GitHub Actions schedule (3x daily)
```

---

## ⚙️ Local Setup
## ⚙️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/Nawaz-B-04/job-bot.git
cd job-bot
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
### 1. Clone the repo
```bash
git clone https://github.com/Nawaz-B-04/job-bot.git
cd job-bot
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set up credentials
```bash
cp .env.example .env
```
Open `.env` and fill in your credentials:
```
NAUKRI_EMAIL=your@email.com
NAUKRI_PASSWORD=yourpassword
INTERNSHALA_EMAIL=your@email.com
INTERNSHALA_PASSWORD=yourpassword
INDEED_EMAIL=your@email.com
```

### 5. Add your resume
Drop your resume PDF in the `resume/` folder and update the path in `config.yaml`:
```yaml
resume_path: "./resume/your_resume.pdf"
```

### 6. Configure your job preferences
Edit `config.yaml`:

### 7. Run
```bash
# Run all platforms
# Run all platforms
python main.py

# Run one platform only
# Run one platform only
python main.py --platform naukri
python main.py --platform internshala
python main.py --platform indeed
```

---

## ☁️ GitHub Actions Setup (Run in Cloud)

This bot runs automatically 3x/day on GitHub's servers — no laptop needed.

### 1. Fork this repo

### 2. Add your credentials as GitHub Secrets
Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value |
|---|---|
| `NAUKRI_EMAIL` | your naukri email |
| `NAUKRI_PASSWORD` | your naukri password |
| `INTERNSHALA_EMAIL` | your internshala email |
| `INTERNSHALA_PASSWORD` | your internshala password |
| `INDEED_EMAIL` | your indeed email |

### 3. Enable Actions
Go to the **Actions** tab in your repo → enable workflows if prompted.

### 4. Test manually
Actions tab → **Job Application Bot** → **Run workflow**

The bot now runs automatically at:
- 🕘 9:00 AM IST
- 🕐 1:00 PM IST
- 🕖 7:00 PM IST

---

## 📊 Viewing Results

After each run, go to:

**Actions tab → latest run → scroll to bottom → download `applied-jobs-db` artifact**

It contains:
- `applied_jobs.db` — open with [DB Browser for SQLite](https://sqlitebrowser.org)
- `applied_YYYYMMDD.csv` — open in Excel

---

## 🔒 Security

- Credentials are stored in **GitHub Secrets** (encrypted, never visible in logs or code)
- `.env` is in `.gitignore` — never committed
- Secrets are injected as environment variables at runtime only

---

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| **Python** | Core language |
| **Playwright** | Browser automation |
| **asyncio** | Async/concurrent execution |
| **PyYAML** | Config file parsing |
| **python-dotenv** | Local credential loading |
| **SQLite** | Deduplication tracking |
| **GitHub Actions** | Cloud scheduling (CI/CD) |

---

## ⚠️ Disclaimer

This tool is for personal use to automate your own job applications. Use responsibly and respect each platform's terms of service. Keep daily application limits reasonable (≤ 30/platform) to avoid account flags.

---

## 🤝 Contributing

PRs welcome! Some ideas:
- Add more platforms (Wellfound, Unstop)
- Add Telegram/email notification on successful apply
- Build a dashboard UI for viewing applications

---
