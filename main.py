"""
Job Application Bot — Main Orchestrator
Runs Naukri, Internshala, and Indeed bots sequentially.

Usage:
  python main.py                    # Run all platforms
  python main.py --platform naukri  # Run specific platform
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asyncio
import argparse
import os
from dotenv import load_dotenv
from utils.logger import init_db, get_stats, export_csv

load_dotenv()

# Credentials
NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD")
INTERNSHALA_EMAIL = os.getenv("INTERNSHALA_EMAIL")
INTERNSHALA_PASSWORD = os.getenv("INTERNSHALA_PASSWORD")
INDEED_EMAIL = os.getenv("INDEED_EMAIL")


async def run_all():
    from platforms.naukri import run as naukri_run
    from platforms.internshala import run as internshala_run
    from platforms.indeed import run as indeed_run

    total = 0

    print("=" * 50)
    print("🤖 JOB BOT STARTING")
    print("=" * 50)

    # --- Naukri ---
    print("\n🟠 PLATFORM: NAUKRI")
    print("-" * 30)
    try:
        n = await naukri_run(NAUKRI_EMAIL, NAUKRI_PASSWORD)
        total += n
    except Exception as e:
        print(f"❌ Naukri bot crashed: {e}")

    # --- Internshala ---
    print("\n🔵 PLATFORM: INTERNSHALA")
    print("-" * 30)
    try:
        i = await internshala_run(INTERNSHALA_EMAIL, INTERNSHALA_PASSWORD)
        total += i
    except Exception as e:
        print(f"❌ Internshala bot crashed: {e}")

    # --- Indeed ---
    print("\n🔴 PLATFORM: INDEED")
    print("-" * 30)
    try:
        d = await indeed_run(INDEED_EMAIL)
        total += d
    except Exception as e:
        print(f"❌ Indeed bot crashed: {e}")

    print("\n" + "=" * 50)
    print(f"🎯 TOTAL APPLICATIONS THIS RUN: {total}")
    print("=" * 50)
    get_stats()
    export_csv()


async def run_single(platform):
    if platform == "naukri":
        from platforms.naukri import run
        await run(NAUKRI_EMAIL, NAUKRI_PASSWORD)
    elif platform == "internshala":
        from platforms.internshala import run
        await run(INTERNSHALA_EMAIL, INTERNSHALA_PASSWORD)
    elif platform == "indeed":
        from platforms.indeed import run
        await run(INDEED_EMAIL)
    else:
        print(f"❌ Unknown platform: {platform}")
        print("Available: naukri, internshala, indeed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Application Bot")
    parser.add_argument("--platform", type=str, help="Run a specific platform only")
    args = parser.parse_args()

    init_db()

    if args.platform:
        asyncio.run(run_single(args.platform.lower()))
    else:
        asyncio.run(run_all())
