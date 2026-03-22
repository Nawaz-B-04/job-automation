import asyncio
import random
import os
import yaml
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from utils.logger import already_applied, log_applied
from utils.browser import get_browser_options

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

PLATFORM = "Internshala"
APPLICANT = cfg["applicant"]
COVER = cfg["cover_note"].strip()
LIMITS = cfg["limits"]
RESUME = os.path.abspath(cfg["resume_path"])


async def delay(base=None):
    base = base or LIMITS["delay_between_jobs"]
    await asyncio.sleep(random.uniform(base * 0.8, base * 1.5))


async def login(page, email, password):
    print("🔐 Logging into Internshala...")
    await page.goto("https://internshala.com/login/user", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)

    await page.fill("#email", email)
    await page.fill("#password", password)
    await page.click("#login_submit")
    await page.wait_for_timeout(3000)
    print("✅ Internshala logged in")


async def fill_application_form(page):
    """Handle Internshala's cover letter / application form"""
    try:
        # Cover letter textarea
        cover_textarea = await page.query_selector("textarea#cover_letter_text, textarea[name='cover_letter']")
        if cover_textarea:
            val = await cover_textarea.input_value()
            if not val:
                await cover_textarea.fill(COVER)

        # Availability question (when can you start)
        avail = await page.query_selector("input#availability, select#availability")
        if avail:
            tag = await avail.evaluate("el => el.tagName")
            if tag == "SELECT":
                await avail.select_option(index=1)
            else:
                await avail.fill("Immediately")

        # Any other text inputs
        inputs = await page.query_selector_all("input[type='text']:not([readonly])")
        for inp in inputs:
            try:
                name = (await inp.get_attribute("name") or "").lower()
                placeholder = (await inp.get_attribute("placeholder") or "").lower()
                val = await inp.input_value()
                if val:
                    continue
                if "phone" in name or "phone" in placeholder:
                    await inp.fill(APPLICANT["phone"])
                elif "city" in name or "location" in placeholder:
                    await inp.fill("Pune")
            except:
                pass
    except Exception as e:
        print(f"  ⚠️ Form fill error: {e}")


async def apply_to_job(page, url, title, company, location):
    if already_applied(url):
        print(f"  ⏭️  Skip: {title}")
        return False

    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Find Apply Now button
        apply_btn = (
            await page.query_selector("a#apply_now_button") or
            await page.query_selector("button:has-text('Apply now')") or
            await page.query_selector("a:has-text('Apply now')")
        )
        if not apply_btn:
            print(f"  ❌ No apply button: {title}")
            return False

        await apply_btn.click()
        await page.wait_for_timeout(2500)

        # Fill the form
        await fill_application_form(page)

        # Submit
        submit = (
            await page.query_selector("input#submit, button#submit") or
            await page.query_selector("button:has-text('Submit application')") or
            await page.query_selector("button:has-text('Submit')")
        )
        if submit:
            await submit.click()
            await page.wait_for_timeout(2000)
            log_applied(url, title, company, location, PLATFORM)
            print(f"  ✅ Applied: {title} @ {company}")
            await delay()
            return True

        return False

    except PWTimeout:
        print(f"  ⏱️ Timeout: {title}")
        return False
    except Exception as e:
        print(f"  ⚠️ Error: {title} — {e}")
        return False


async def run(email, password):
    count = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(**get_browser_options())
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        await login(page, email, password)

        for keyword in cfg["keywords"]:
            if count >= LIMITS["max_per_platform"]:
                break

            kw = keyword.replace(" ", "%20")

            # Internshala has /jobs and /internships — hit both
            for section in ["jobs", "internships"]:
                if count >= LIMITS["max_per_platform"]:
                    break

                search_url = f"https://internshala.com/{section}/{keyword.lower().replace(' ', '-')}-{section}"
                print(f"\n🔍 Internshala ({section}): '{keyword}'")

                try:
                    await page.goto(search_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    # Scroll to load all cards
                    for _ in range(3):
                        await page.keyboard.press("End")
                        await page.wait_for_timeout(800)

                    job_cards = await page.query_selector_all(".individual_internship, .job-internship-card")
                    print(f"   Found {len(job_cards)} listings")

                    for card in job_cards:
                        if count >= LIMITS["max_per_platform"]:
                            break
                        try:
                            # Get the detail page link
                            link_el = await card.query_selector("a.job-title-href, a.view_detail_button, h3 a")
                            if not link_el:
                                continue

                            href = await link_el.get_attribute("href")
                            if not href:
                                continue
                            job_url = f"https://internshala.com{href}" if href.startswith("/") else href

                            title_el = await card.query_selector("h3, .job-title, .profile")
                            job_title = (await title_el.inner_text()).strip() if title_el else keyword

                            company_el = await card.query_selector(".company_name, .company-name")
                            company = (await company_el.inner_text()).strip() if company_el else ""

                            location_el = await card.query_selector(".location_link, .location")
                            location = (await location_el.inner_text()).strip() if location_el else "India"

                            result = await apply_to_job(page, job_url, job_title, company, location)
                            if result:
                                count += 1

                        except Exception:
                            continue

                    await asyncio.sleep(LIMITS["delay_between_searches"])

                except Exception as e:
                    print(f"  ⚠️ Search error: {e}")
                    continue

        await browser.close()
    print(f"\n✅ Internshala done — {count} applications")
    return count
