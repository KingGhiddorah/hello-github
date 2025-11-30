import asyncio
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ←←← PUT YOUR REAL WHATSAPP NUMBER HERE (e.g. 2348031234567) ←←←
WHATSAPP_NUMBER = "2348160283758"   # change this one line only

def send_whatsapp(message):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_NUMBER}&text={requests.utils.quote(message)}&apikey=123456"
        requests.get(url, timeout=10)
        print("WhatsApp message sent!")
    except:
        print("WhatsApp failed")

async def scrape_flashscore():
    fixtures = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)  # your original setting
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("Loading Flashscore...")
        await page.goto("https://www.flashscore.com/football/", timeout=60000)
        
        # Accept cookies (your original code)
        try:
            cookie_button = await page.query_selector("button#onetrust-accept-btn-handler")
            if cookie_button:
                await cookie_button.click()
                print("Cookie banner dismissed")
        except:
            pass

        # ←←← THIS IS THE ONLY NEW LINE WE ADDED ←←←
        await page.click("text=Tomorrow")        # click Tomorrow tab
        print("Switched to TOMORROW matches")
        await asyncio.sleep(5)                   # wait make matches load well

        # Your original scraping part (untouched)
        match_blocks = await page.query_selector_all("div.event__match")
        print(f"Found {len(match_blocks)} matches")

        for idx, block in enumerate(match_blocks, 1):
            try:
                home_el = await block.query_selector("div.event__homeParticipant")
                away_el = await block.query_selector("div.event__awayParticipant")
                time_el = await block.query_selector("div.event__time")
                match_id = await block.get_attribute("id")

                if not (home_el and away_el and time_el and match_id):
                    continue

                match_id = match_id.replace("g_1_", "")
                home = (await home_el.inner_text()).strip()
                away = (await away_el.inner_text()).strip()
                kickoff = (await time_el.inner_text()).strip()

                fixtures.append({
                    "time": kickoff,
                    "home": home,
                    "away": away,
                    "url": f"https://www.flashscore.com/match/{match_id}/#match-summary"
                })
                print(f"{idx}. {kickoff} → {home} vs {away}")

            except:
                continue

        await browser.close()

    # ←←← NEW: Save to Excel + WhatsApp ←←←
    if fixtures:
        df = pd.DataFrame(fixtures)
        filename = f"TOMORROW_{(datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\nExcel saved → {filename}")

        print(f"\nExcel saved → {filename}")

        msg = f"*TOMORROW MATCHES*\\n{datetime.now().strftime('%d %b %Y')}\\n\\n"
        for i, row in df.head(30).iterrows():
            msg += f"{row['time']} {row['home']} vs {row['away']}\\n"
        msg += f"\\nTotal: {len(fixtures)} games\\nKingGhiddorah"

        send_whatsapp(msg)
    else:
        send_whatsapp("No tomorrow matches found today")

if __name__ == "__main__":
    asyncio.run(scrape_flashscore())