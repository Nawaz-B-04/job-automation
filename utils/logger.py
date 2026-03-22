import sqlite3
import csv
from datetime import datetime

DB_PATH = "applied_jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applied (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            company TEXT,
            location TEXT,
            platform TEXT,
            status TEXT DEFAULT 'Applied',
            applied_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database ready\n")

def already_applied(url: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM applied WHERE url=?", (url,))
        result = cur.fetchone()
        conn.close()
        return result is not None
    except:
        return False

def log_applied(url: str, title: str, company: str = "", location: str = "", platform: str = ""):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO applied (url, title, company, location, platform, applied_at) VALUES (?,?,?,?,?,?)",
            (url, title, company, location, platform, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  ⚠️ Log error: {e}")

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT platform, COUNT(*) FROM applied GROUP BY platform")
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM applied WHERE date(applied_at) = date('now')")
    today = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM applied")
    total = cur.fetchone()[0]
    conn.close()
    print("\n📊 Application Stats")
    print(f"   Total: {total} | Today: {today}")
    for platform, count in rows:
        print(f"   {platform}: {count}")

def export_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title, company, location, platform, status, applied_at, url FROM applied ORDER BY applied_at DESC")
    rows = cur.fetchall()
    conn.close()
    filename = f"applied_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Company", "Location", "Platform", "Status", "Applied At", "URL"])
        writer.writerows(rows)
    print(f"📁 Exported to {filename}")
