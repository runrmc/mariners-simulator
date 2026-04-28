import pandas as pd
import requests
import os
from io import StringIO
from src.data.batting import fix_name

STATS_DIR = "data/stats"


def fetch_mariners_pitching(year: int, top_n: int = 5) -> pd.DataFrame:
    """Pull Mariners starting pitcher stats for a given year and cache locally."""
    stats_path = f"{STATS_DIR}/mariners_{year}_pitching.csv"

    if os.path.exists(stats_path):
        print(f"Loading {year} pitching stats from cache...")
        return pd.read_csv(stats_path)

    print(f"Fetching {year} Mariners pitching stats from Baseball Reference...")

    url = f"https://www.baseball-reference.com/teams/SEA/{year}.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch pitching data for {year}: HTTP {response.status_code}")

    html = response.text
    tables = pd.read_html(StringIO(html))

    # Find the pitching table by looking for ERA and GS columns
    pitching = None
    for table in tables:
        if "ERA" in table.columns and "GS" in table.columns and "Player" in table.columns:
            pitching = table.copy()
            break

    if pitching is None:
        raise Exception(f"Could not find pitching table for {year}")

    pitching = pitching[pitching["Player"].notna()]
    pitching = pitching[pitching["Player"] != "Player"]
    pitching = pitching[~pitching["Player"].str.contains("Team|Total|Totals", na=False)]
    pitching = pitching.rename(columns={"Player": "Name"})
    pitching["Name"] = pitching["Name"].apply(fix_name)

    for col in ["GS", "ERA", "WHIP", "SO", "BB", "IP", "HR"]:
        pitching[col] = pd.to_numeric(pitching[col], errors="coerce").fillna(0)

    starters = pitching[pitching["GS"] >= 1].copy()

    starters["K9"] = (starters["SO"] / starters["IP"] * 9).round(2)
    starters["BB9"] = (starters["BB"] / starters["IP"] * 9).round(2)
    starters["HR9"] = (starters["HR"] / starters["IP"] * 9).round(2)

    starters = starters.sort_values("GS", ascending=False).head(top_n)

    cols = ["Name", "GS", "IP", "ERA", "WHIP", "K9", "BB9", "HR9"]
    starters = starters[cols].reset_index(drop=True)

    os.makedirs(STATS_DIR, exist_ok=True)
    starters.to_csv(stats_path, index=False)
    print(f"Saved {year} pitching stats to {stats_path}")

    return starters
