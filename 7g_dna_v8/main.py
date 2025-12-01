# 7g_dna_v8/main.py
import asyncio
from scraper import scrape_flashscore
from datetime import datetime

async def run_7g_playbook():
    print("7G DNA v8 ENGINE STARTED")
    print("="*60)
    print(f"Phase 0 → Pre-match Intelligence | {datetime.now().strftime('%d %b %Y - %H:%M')}")
    print("="*60)

    matches = await scrape_tomorrow_matches()
    
    if matches:
        print(f"\nPre-match scan complete: {len(matches)} fixtures collected")
        print("Next → Phase 1: Subtype Classification (C1–C7 + Hybrids)")
        print("Type '7G' to continue...")
    else:
        print("No matches found. Check connection.")

if __name__ == "__main__":
    asyncio.run(run_7g_playbook())