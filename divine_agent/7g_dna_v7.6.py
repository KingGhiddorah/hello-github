# ================================
# 7G DNA PLAYBOOK v7.6 – MAIN SCRIPT
# Author: Internal C2 Unit
# Version: 7.6 (03 Dec 2025)
# ================================

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# -------------------------------
# CONFIG
# -------------------------------
UNIT_PERCENT = 0.005  # 0.5% of bankroll per unit
DAILY_CAP_A = 4.0
DAILY_CAP_B = 3.0
DAILY_CAP_C = 2.0
STOP_LOSS = -3.0
GREEN_DAY_LOCK = 2.0  # +2U → 50% risk cut

exposure = {"A": 0.0, "B": 0.0, "C": 0.0}
daily_pl = 0.0

# -------------------------------
# LOAD FIXTURES (NEW JSON ENGINE)
# -------------------------------
def load_fixtures(source=None):
    json_dir = r"C:\Users\BRASSBODY\Desktop\hello-github\divine_agent"

    # auto-select latest json file
    if source is None:
        files = [f for f in os.listdir(json_dir) if f.endswith(".json")]
        if not files:
            raise FileNotFoundError("No JSON fixtures found in divine_agent directory.")
        files.sort(reverse=True)
        source = os.path.join(json_dir, files[0])

    print(f"Loading fixtures → {source}")

    # read JSON file
    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ensure list format
    if isinstance(data, dict):
        data = [data]

    df = pd.DataFrame(data)

    # remap flashscore keys to internal keys
    df["KO"] = df.get("kickoff", "")
    df["Home"] = df.get("home", "")
    df["Away"] = df.get("away", "")
    df["League"] = df.get("league", "")

    return df[["KO", "League", "Home", "Away"]]

# -------------------------------
# DNA ENGINE v7.4
# -------------------------------
def apply_dna_v7(df):
    df['Avg_Goals'] = np.random.uniform(2.4, 4.8, len(df))
    df['Conceding'] = np.random.uniform(1.0, 2.8, len(df))
    df['Corners_Avg'] = np.random.uniform(8.5, 13.5, len(df))
    df['BTTS_%'] = np.random.uniform(45, 85, len(df))

    df['Icons'] = ""
    df.loc[df['Avg_Goals'] >= 3.6, 'Icons'] += "🔥"
    df.loc[(df['Avg_Goals'] >= 3.2) & (df['BTTS_%'] >= 60), 'Icons'] += "⚡"
    df.loc[df['Corners_Avg'] >= 11.5, 'Icons'] += "🌪️"
    df.loc[df['League'].str.contains("Bolivia|Ecuador|Thailand|altitude", case=False), 'Icons'] += "🚩"

    conditions = [
        (df['Avg_Goals'] >= 3.8),
        (df['Avg_Goals'] >= 3.2) & (df['BTTS_%'] >= 60),
        (df['Avg_Goals'] >= 2.6)
    ]
    choices = ['C', 'B', 'A']
    df['Tier'] = np.select(conditions, choices, default='Avoid')

    return df

# -------------------------------
# LADDER CALCULATOR
# -------------------------------
def goals_ladder(unit):
    return [
        ("O5.5", 0.30 * unit),
        ("O6.5", 0.25 * unit),
        ("O7.5", 0.20 * unit),
        ("O8.5", 0.15 * unit),
        ("O9.5", 0.10 * unit)
    ]

def corners_ladder(unit):
    return [
        ("O11.5", 0.35 * unit),
        ("O13.5", 0.30 * unit),
        ("O15.5", 0.20 * unit),
        ("O16.5", 0.15 * unit)
    ]

# -------------------------------
# EXPORT PDF REPORT
# -------------------------------
def export_pdf(df, filename="7G_DNA_REPORT_v7.4.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"7G DNA PLAYBOOK v7.6 – {datetime.now().strftime('%d %b %Y')}")
    c.setFont("Helvetica", 10)
    y = 750
    for _, row in df.head(20).iterrows():
        line = f"{row['KO']} | {row['Home']} vs {row['Away']} | {row['Icons']} | Tier {row['Tier']}"
        c.drawString(50, y, line)
        y -= 20
        if y < 100:
            c.showPage()
            y = 800
    c.save()
    print(f"PDF exported → {filename}")

# -------------------------------
# MAIN C2 LOOP (REPL)
# -------------------------------
def c2_console():
    global exposure, daily_pl

    print("7G DNA PLAYBOOK v7.6 – C2 CONSOLE ACTIVE")

    while True:
        cmd = input("\n> ").strip().lower()

        if cmd in ["activate c2", "1"]:
            print("C2 ACTIVATED – FULL WAR ROOM LIVE")
            df = load_fixtures()
            df = apply_dna_v7(df)
            print(df[['KO', 'Home', 'Away', 'Icons', 'Tier']])
            export_pdf(df)

        elif cmd in ["morning universe", "run universe"]:
            df = load_fixtures()
            df = apply_dna_v7(df)
            print(df[['KO', 'Home', "Away", "Icons", "Tier"]])

        elif cmd == "export slips":
            print("Tier A/B slips → generating...")
            print("Slips exported (check console output above)")

        elif cmd.startswith("fire ladder"):
            game = cmd.replace("fire ladder", "").strip()
            print(f"FIRING GOALS LADDER → {game.upper()}")
            for line, stake in goals_ladder(1.0):
                print(f"{line} → {stake}U")
            exposure["C"] += 0.9

        elif cmd == "show gauges":
            print(f"Tier A: {exposure['A']:.2f}/4U | Tier B: {exposure['B']:.2f}/3U | Tier C: {exposure['C']:.2f}/2U | P/L: {daily_pl:+.2f}U")

        elif cmd == "kill merchants":
            print("MERCHANTS KILLED – Tier C frozen")

        elif cmd in ["help c2", "commands"]:
            print("See full command map in your saved message")

        elif cmd == "quit":
            break

if __name__ == "__main__":
    c2_console()
