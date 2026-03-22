# Job Application Bot
**Platforms: Naukri · Internshala · Indeed**
Built for: Nawazish Majid Bidiwale

---

## 📁 Project Structure

```
job_bot/
├── main.py                  ← Run this to start all bots
├── config.yaml              ← Keywords, filters, your info
├── .env                     ← Passwords (fill this, never share)
├── requirements.txt
├── stats.py                 ← View stats + export CSV
├── applied_jobs.db          ← Auto-created (tracks all applications)
├── resume/
│   └── Nawazish_Bidiwale_Fullstack.pdf   ← PUT RESUME HERE
├── platforms/
│   ├── naukri.py
│   ├── internshala.py
│   └── indeed.py
└── utils/
    └── logger.py
```

---

## ⚙️ One-Time Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Add your resume
Copy your PDF into the `resume/` folder. Name must match `config.yaml`:
```
resume/Nawazish_Bidiwale_Fullstack.pdf
```

### 3. Fill in your passwords
Open `.env` and add your passwords:
```
NAUKRI_PASSWORD=your_naukri_password
INTERNSHALA_PASSWORD=your_internshala_password
```

---

## ▶️ Running the Bot

### Run all platforms
```bash
python main.py
```

### Run one platform only
```bash
python main.py --platform naukri
python main.py --platform internshala
python main.py --platform indeed
```

A browser window opens for each platform. Don't close it — monitor what's happening.

---

## 📊 Check Your Applications

```bash
python stats.py
```

Prints total applications per platform and exports a dated CSV file.

---

## ⚙️ Customize (config.yaml)

| Setting | What it does |
|---|---|
| `keywords` | Job titles to search for |
| `filters.locations` | Cities to target |
| `limits.max_per_platform` | Max applications per platform per run |
| `limits.delay_between_jobs` | Seconds between each apply (keep ≥ 5) |
| `cover_note` | Your cover letter text |
| `applicant.expected_ctc` | Expected salary in INR |

---

## ⏰ Schedule Daily (Windows)

1. Open **Task Scheduler** → Create Basic Task
2. Trigger: Daily at 9:00 AM
3. Action: Start a Program
   - Program: `python`
   - Arguments: `main.py`
   - Start in: `C:\path\to\job_bot`

---

## ⚠️ Important Notes

- Keep `headless=False` while testing so you can watch and intervene
- **Naukri** — Works best. If CAPTCHA appears, solve manually
- **Internshala** — Most reliable, very bot-friendly
- **Indeed** — Easy Apply only; jobs with external apply links are skipped
- **LinkedIn** — Use **LazyApply** Chrome extension instead of a bot
- **Cutshort / Foundit** — Apply manually; they use skill-match AI so a bot undermines the point
- Don't exceed 30 applications/platform/day to avoid account flags

---

## 🔁 Recommended Daily Workflow

| Time | Action |
|---|---|
| 9:00 AM | `python main.py` — bot runs all 3 platforms |
| 9:30 AM | `python stats.py` — check what was applied |
| Evening | Manually check Cutshort + Foundit (10 min) |
| Evening | LazyApply on LinkedIn (run the extension) |
