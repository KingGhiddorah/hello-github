import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import subprocess   # ← new
import os           # ← new

async def scrape_flashscore():
    fixtures = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("Loading Flashscore...")
        try:
            await page.goto("https://www.flashscore.com/football/", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_selector("div.event__match", timeout=15000)
        except PlaywrightTimeoutError:
            print("Timeout waiting for match blocks")
            await browser.close()
            return

        # Handle cookie banners
        try:
            cookie_button = await page.query_selector("button#onetrust-accept-btn-handler")
            if cookie_button:
                await cookie_button.click()
                print("Cookie banner dismissed")
                await page.wait_for_timeout(1000)
        except Exception:
            print("No cookie banner found")

        match_blocks = await page.query_selector_all("div.event__match")
        print(f"Found {len(match_blocks)} match blocks")

        for idx, block in enumerate(match_blocks, 1):
            try:
                home_el = await block.query_selector("div.event__homeParticipant")
                away_el = await block.query_selector("div.event__awayParticipant")
                time_el = await block.query_selector("div.event__time")
                match_id = await block.get_attribute("id")

                missing_fields = []
                if not home_el: missing_fields.append("home team")
                if not away_el: missing_fields.append("away team")
                if not time_el: missing_fields.append("kickoff time")
                if not match_id: missing_fields.append("match ID")

                if missing_fields:
                    print(f"Warning ({idx}/{len(match_blocks)}) Missing: {', '.join(missing_fields)}")
                    continue

                match_id = match_id.replace("g_1_", "")
                fixture = {
                    "home": (await home_el.inner_text()).strip(),
                    "away": (await away_el.inner_text()).strip(),
                    "kickoff": (await time_el.inner_text()).strip(),
                    "url": f"https://www.flashscore.com/match/{match_id}/"
                }
                fixtures.append(fixture)
                print(f"Success ({idx}/{len(match_blocks)}) {fixture['home']} vs {fixture['away']} @ {fixture['kickoff']}")

            except Exception as e:
                print(f"Error ({idx}/{len(match_blocks)}): {e}")
                continue

        await browser.close()

    if fixtures:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flashscore_fixtures_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, indent=2)
        print(f"\nSaved {len(fixtures)} fixtures to {filename}")

        # ←←← ONLY THIS PART IS NEW (5 lines) ←←←
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Update fixtures {timestamp}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Pushed to GitHub successfully!")
        except:
            print("Git push failed – run 'git config --global credential.helper store' first time only")
    else:
        print("\nNo fixtures saved.")

if __name__ == "__main__":
    asyncio.run(scrape_flashscore())