import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def scrape_flashscore():
    fixtures = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("🌍 Loading Flashscore...")
        try:
            await page.goto("https://www.flashscore.com/football/", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_selector("div.event__match", timeout=15000)
        except PlaywrightTimeoutError:
            print("❌ Timeout waiting for match blocks")
            await browser.close()
            return

        # Handle cookie banners
        try:
            cookie_button = await page.query_selector("button#onetrust-accept-btn-handler")
            if cookie_button:
                await cookie_button.click()
                print("✅ Cookie banner dismissed")
                await page.wait_for_timeout(1000)
        except Exception:
            print("⚠️ No cookie banner found")

        match_blocks = await page.query_selector_all("div.event__match")
        print(f"🔍 Found {len(match_blocks)} match blocks")

        for idx, block in enumerate(match_blocks, 1):
            try:
                home_el = await block.query_selector("div.event__homeParticipant")
                away_el = await block.query_selector("div.event__awayParticipant")
                time_el = await block.query_selector("div.event__time")
                match_id = await block.get_attribute("id")

                missing_fields = []
                if not home_el:
                    missing_fields.append("home team")
                if not away_el:
                    missing_fields.append("away team")
                if not time_el:
                    missing_fields.append("kickoff time")
                if not match_id:
                    missing_fields.append("match ID")

                if missing_fields:
                    print(f"⚠️ ({idx}/{len(match_blocks)}) Missing: {', '.join(missing_fields)}")
                    continue

                match_id = match_id.replace("g_1_", "")  # Convert g_1_ABC123 to ABC123
                fixture = {
                    "home": (await home_el.inner_text()).strip(),
                    "away": (await away_el.inner_text()).strip(),
                    "kickoff": (await time_el.inner_text()).strip(),
                    "url": f"https://www.flashscore.com/match/{match_id}/"
                }
                fixtures.append(fixture)
                print(f"✅ ({idx}/{len(match_blocks)}) {fixture['home']} vs {fixture['away']} @ {fixture['kickoff']} | URL: {fixture['url']}")

            except PlaywrightTimeoutError:
                print(f"❌ ({idx}/{len(match_blocks)}) Timeout accessing elements")
                continue
            except Exception as e:
                print(f"❌ ({idx}/{len(match_blocks)}) Error: {e}")
                continue

        await browser.close()

    if fixtures:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flashscore_fixtures_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, indent=2)
        print(f"\n💾 Saved {len(fixtures)} fixtures to {filename}")
    else:
        print("\n⚠️ No fixtures saved. Check selectors or website content.")

# NEW (correct name)
if __name__ == "__main__":
    asyncio.run(scrape_tomorrow_matches())
	
	