def process_fixtures_v48(fixtures):
    results = []
    for fixture in fixtures:
        home = fixture.get("teams", {}).get("home", fixture.get("home", "Unknown"))
        away = fixture.get("teams", {}).get("away", fixture.get("away", "Unknown"))
        title = f"{home} vs {away}"

        btts_conf = fixture.get("btts_confidence", 0.0)
        o25_conf = fixture.get("over25_confidence", 0.0)
        o35_conf = fixture.get("over35_confidence", 0.0)

        key_predictions = {
            "BTTS": "Yes" if btts_conf > 0.5 else "No",
            "Over 2.5": "Yes" if o25_conf > 0.5 else "No",
            "Over 3.5": "Yes" if o35_conf > 0.5 else "No"
        }

        correct_scores = [
            {"score": s, "prob": round(100/len(fixture.get("correct_score_ranked_list", [1])),2)}
            for s in fixture.get("correct_score_ranked_list", [])
        ]

        # 7Goal Trigger
        seven_goal_trigger = (btts_conf > 0.75 and o35_conf > 0.7)

        risk_zone = fixture.get("risk_profile_zone", "Unknown")
        commentary = []
        if fixture.get("momentum_flag"): commentary.append("📈 Home or away team has winning momentum.")
        if fixture.get("volatility_flag"): commentary.append("🌪 Volatile H2H history could spark goals.")
        if seven_goal_trigger: commentary.append("🔥 7Goal Playbook Triggered!")

        logs = [
            f"BTTS Confidence: {btts_conf:.2f} (xG {fixture.get('xg_for_home',0)}+{fixture.get('xg_for_away',0)}, synergy {fixture.get('synergy_index',0)})",
            f"O2.5 Confidence: {o25_conf:.2f} (avg goals {fixture.get('goals_per_match_avg',0)})",
            f"O3.5 Confidence: {o35_conf:.2f}",
            f"Momentum: {fixture.get('momentum_flag')} | Volatility: {fixture.get('volatility_flag')} | PosDiff: {fixture.get('pos_diff')}",
            f"7Goal Trigger: {seven_goal_trigger}"
        ]

        summary = (
            f"🏟 {title} Match Outlook: Likely a cautious game with limited scoring. "
            f"🎯 Betting Signals: BTTS: {key_predictions['BTTS']} | Over 2.5: {key_predictions['Over 2.5']} | "
            f"Top Correct Score: {correct_scores[0]['score'] if correct_scores else 'N/A'} | "
            f"💡 Best Play: BTTS 💡 Engine Insight: BTTS Confidence: {btts_conf:.2f} "
            f"(xG {fixture.get('xg_for_home',0):.2f}+{fixture.get('xg_for_away',0):.2f}, synergy {fixture.get('synergy_index',0):.2f}) | "
            f"7Goal Trigger: {seven_goal_trigger}"
        )

        results.append({
            "fixture": title,
            "summary": summary,
            "key_predictions": key_predictions,
            "correct_scores": correct_scores,
            "risk_zone": risk_zone,
            "tactical_commentary": commentary,
            "engine_logs": logs,
            "confidence_scores": {  # 🔹 For confidence bars
                "BTTS": btts_conf,
                "Over 2.5": o25_conf,
                "Over 3.5": o35_conf
            }
        })

    return results
