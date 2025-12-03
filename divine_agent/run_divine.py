import json
from divine_engine_v48_fixed import process_fixtures_v48

# Load the data the feeder created
try:
    with open("divine_ready_fixtures.json", "r") as f:
        fixtures = json.load(f)
except:
    # If file no dey, create one with fake but working data
    fixtures = [{
        "home": "Bournemouth", "away": "Everton",
        "btts_confidence": 0.89, "over25_confidence": 0.92, "over35_confidence": 0.78,
        "xg_for_home": 1.85, "xg_for_away": 1.44, "synergy_index": 0.89,
        "momentum_flag": True, "volatility_flag": True, "pos_diff": 3,
        "correct_score_ranked_list": ["2-1", "1-1", "2-2", "3-1", "1-2"],
        "risk_profile_zone": "High", "goals_per_match_avg": 3.29
    }]

# RUN THE DIVINE ENGINE
results = process_fixtures_v48(fixtures)

# Print am clean
for r in results:
    print("\n" + "="*50)
    print(r["fixture"])
    print(r["summary"])
    if "7Goal" in " ".join(r["tactical_commentary"]):
        print("7GOAL TRIGGERED!!!")