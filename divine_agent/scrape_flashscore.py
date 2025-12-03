import asyncio
import json
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def scrape_flashscore():
    fixtures = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        print("Loading Flashscore...")
        try:
            await page.goto("https://www.flashscore.com/football/", timeout=60000)
            await page.wait_for_selector("div.event__match", timeout=20000)
        except PlaywrightTimeoutError:
            print("Timeout – no matches found or page too slow")
            await browser.close()
            return

        # Accept cookies
        try:
            await page.click("button#onetrust-accept-btn-handler", timeout=5000)
            print("Cookie banner dismissed")
        except:
            print("No cookie banner")

        match_blocks = await page.query_selector_all("div.event__match")
        print(f"Found {len(match_blocks)} matches")

        for idx, block in enumerate(match_blocks, 1):
            try:
                home_el = await block.query_selector("div.event__homeParticipant")
                away_el = await block.query_selector("div.event__awayParticipant")
                time_el = await block.query_selector("div.event__time")
                match_id = await block.get_attribute("id")

                if not all([home_el, away_el, time_el, match_id]):
                    continue

                home = (await home_el.inner_text()).strip()
                away = (await away_el.inner_text()).strip()
                kickoff = (await time_el.inner_text()).strip().replace("\n", " ")
                match_id = match_id.replace("g_1_", "")

                fixture = {
                    "home": home,
                    "away": away,
                    "kickoff": kickoff,
                    "url": f"https://www.flashscore.com/match/{match_id}/"
                }
                fixtures.append(fixture)
                print(f"{idx:3d}. {home} vs {away} @ {kickoff}")

            except Exception as e:
                continue

        await browser.close()

    # Save JSON
    if fixtures:
        filename = f"flashscore_fixtures_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(fixtures)} fixtures → {filename}")

        # Auto GitHub push
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Daily fixtures {timestamp}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Pushed to GitHub successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Git failed: {e}")
        except FileNotFoundError:
            print("Git not found in PATH – install Git or remove push block")
    else:
        print("No fixtures scraped today.")


# RUN IT
if __name__ == "__main__":
    asyncio.run(scrape_flashscore())