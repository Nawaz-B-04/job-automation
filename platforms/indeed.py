import asyncio
import random
import os
import yaml
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from utils.logger import already_applied, log_applied

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

PLATFORM = "Indeed"
APPLICANT = cfg["applicant"]
COVER = cfg["cover_note"].strip()
LIMITS = cfg["limits"]
RESUME = os.path.abspath(cfg["resume_path"])


async def delay(base=None):
    base = base or LIMITS["delay_between_jobs"]
    await asyncio.sleep(random.uniform(base * 0.8, base * 1.5))


async def handle_indeed_form(page):
    """Fill Indeed's Easy Apply multi-step form"""
    try:
        # Resume upload
        file_input = await page.query_selector("input[type='file']")
        if file_input:
            await file_input.set_input_files(RESUME)
            await page.wait_for_timeout(1500)

        # Text fields
        inputs = await page.query_selector_all("input[type='text'], input[type='number'], input[type='tel']")
        for inp in inputs:
            try:
                label_text = ""
                label_id = await inp.get_attribute("id")
                if label_id:
                    label_el = await page.query_selector(f"label[for='{label_id}']")
                    if label_el:
                        label_text = (await label_el.inner_text()).lower()

                val = await inp.input_value()
                if val:
                    continue

                if "phone" in label_text or "mobile" in label_text:
                    await inp.fill(APPLICANT["phone"])
                elif "city" in label_text or "location" in label_text:
                    await inp.fill("Pune, Maharashtra")
                elif "salary" in label_text or "ctc" in label_text:
                    await inp.fill("500000")
                elif "experience" in label_text or "year" in label_text:
                    await inp.fill("0")
                elif "name" in label_text:
                    await inp.fill(APPLICANT["name"])
            except:
                pass

        # Textareas (cover letter)
        textareas = await page.query_selector_all("textarea")
        for ta in textareas:
            val = await ta.input_value()
            if not val:
                await ta.fill(COVER)
                break

        # Dropdowns — pick first non-empty or "Yes" option
        selects = await page.query_selector_all("select")
        for sel in selects:
            try:
                options = await sel.query_selector_all("option")
                texts = [await o.inner_text() for o in options]
                for opt in texts:
                    if opt.strip().lower() in ["yes", "immediately", "0", "india", "bachelor"]:
                        await sel.select_option(label=opt.strip())
                        break
            except:
                pass

    except Exception as e:
        print(f"  ⚠️ Form error: {e}")


async def apply_to_job(page, job_id, title, company, location):
    job_url = f"https://in.indeed.com/viewjob?jk={job_id}"

    if already_applied(job_url):
        print(f"  ⏭️  Skip: {title}")
        return False

    try:
        await page.goto(job_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # Find Indeed Easy Apply button
        apply_btn = (
            await page.query_selector("button.indeedApplyButton") or
            await page.query_selector("button[id*='indeedApplyButton']") or
            await page.query_selector("span.indeed-apply-button-label")
        )
        if not apply_btn:
            print(f"  ❌ No Easy Apply: {title}")
            return False

        await apply_btn.click()
        await page.wait_for_timeout(3000)

        # Indeed opens apply in a new tab or modal — handle both
        # Try to find the apply iframe
        frame = None
        for f in page.frames:
            if "indeed" in f.url and "apply" in f.url:
                frame = f
                break

        target = frame or page

        # Walk through multi-step form
        max_steps = 6
        for step in range(max_steps):
            await handle_indeed_form(target)

            # Check for final submit
            submit = await target.query_selector("button[type='submit']:has-text('Submit')")
            if submit:
                await submit.click()
                await page.wait_for_timeout(2000)
                log_applied(job_url, title, company, location, PLATFORM)
                print(f"  ✅ Applied: {title} @ {company}")
                await delay()
                return True

            # Next step
            next_btn = (
                await target.query_selector("button:has-text('Continue')") or
                await target.query_selector("button:has-text('Next')") or
                await target.query_selector("button[type='submit']")
            )
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(2000)
            else:
                break

        return False

    except PWTimeout:
        print(f"  ⏱️ Timeout: {title}")
        return False
    except Exception as e:
        print(f"  ⚠️ Error: {title} — {e}")
        return False


async def run(email=None):
    count = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Indeed India — no login required for Easy Apply on many jobs
        # But pre-fill email if available
        await page.goto("https://in.indeed.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        for keyword in cfg["keywords"]:
            if count >= LIMITS["max_per_platform"]:
                break

            for location in cfg["filters"]["locations"]:
                if count >= LIMITS["max_per_platform"]:
                    break

                loc_param = "remote" if location.lower() == "remote" else location
                kw_encoded = keyword.replace(" ", "+")

                # Indeed India URL with Easy Apply filter (&iafilter=1) and date posted last 7 days (&fromage=7)
                search_url = (
                    f"https://in.indeed.com/jobs?q={kw_encoded}&l={loc_param}"
                    f"&iafilter=1&fromage=7&explvl=entry_level"
                )

                print(f"\n🔍 Indeed: '{keyword}' in {location}")

                try:
                    await page.goto(search_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    # Extract job IDs from the page
                    job_cards = await page.query_selector_all("div.job_seen_beacon, div.resultContent")
                    print(f"   Found {len(job_cards)} listings")

                    for card in job_cards:
                        if count >= LIMITS["max_per_platform"]:
                            break
                        try:
                            # Get job ID from data attribute
                            job_id = await card.get_attribute("data-jk")
                            if not job_id:
                                link_el = await card.query_selector("a[data-jk]")
                                if link_el:
                                    job_id = await link_el.get_attribute("data-jk")

                            if not job_id:
                                continue

                            title_el = await card.query_selector("h2.jobTitle span, span[title]")
                            job_title = (await title_el.inner_text()).strip() if title_el else keyword

                            company_el = await card.query_selector("span.companyName, [data-testid='company-name']")
                            company = (await company_el.inner_text()).strip() if company_el else ""

                            loc_el = await card.query_selector("div.companyLocation, [data-testid='text-location']")
                            job_loc = (await loc_el.inner_text()).strip() if loc_el else location

                            result = await apply_to_job(page, job_id, job_title, company, job_loc)
                            if result:
                                count += 1

                        except Exception:
                            continue

                    await asyncio.sleep(LIMITS["delay_between_searches"])

                except Exception as e:
                    print(f"  ⚠️ Search error: {e}")
                    continue

        await browser.close()
    print(f"\n✅ Indeed done — {count} applications")
    return count
