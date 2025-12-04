def load_fixtures():
    search_locations = [
        Path.cwd(),
        Path(os.path.expanduser("~/Desktop")),
        Path(os.path.expanduser("~/Downloads")),
        Path(os.path.expanduser("~"))
    ]

    json_files = []
    for loc in search_locations:
        json_files.extend(list(loc.glob("flashscore_fixtures_*.json")))

    if not json_files:
        print("❌ No Flashscore JSON found → manual paste mode")
        return manual_paste()

    latest_file = max(json_files, key=os.path.getmtime)
    print(f"✅ AUTO-LOADED → {latest_file.name}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # FIXED: Handle list or dict at top-level
    if isinstance(raw, list):
        events = raw  # Direct list of events
    else:
        # Dict case: try common keys
        events = raw.get("data", raw.get("events", raw.get("EVENTS", [])))
        if isinstance(events, dict):
            events = list(events.values())  # Flatten if nested dict

    matches = []
    for event in events:
        if isinstance(event, dict):
            try:
                ts = event.get("startTimestamp", event.get("time", 0))
                ko = datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "N/A"
                league = event.get("tournament", {}).get("name", event.get("league", "Unknown"))
                home = event.get("homeTeam", {}).get("name", event.get("home", "Home"))
                away = event.get("awayTeam", {}).get("name", event.get("away", "Away"))
                matches.append({"KO": ko, "League": league, "Home": home, "Away": away})
            except Exception as e:
                print(f"Parse skip: {e}")
                continue

    df = pd.DataFrame(matches)
    if df.empty:
        print("⚠️ JSON parsed but no matches → manual mode")
        return manual_paste()
    
    df = df[["KO", "League", "Home", "Away"]].drop_duplicates().reset_index(drop=True)
    print(f"Loaded {len(df)} fixtures successfully!")
    return df