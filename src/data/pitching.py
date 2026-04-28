import pandas as pd
import requests
import os
from io import StringIO
from src.data.batting import fix_name
from src.models.pitcher import Pitcher
import time

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
    time.sleep(1) # Be polite to Baseball Reference
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch pitching data for {year}: HTTP {response.status_code}")

    html = response.text
    tables = pd.read_html(StringIO(html))

    # Table 2 is the pitching table
    pitching = tables[2].copy()

    # Clean up
    pitching = pitching[pitching["Player"].notna()]
    pitching = pitching[pitching["Player"] != "Player"]
    pitching = pitching[~pitching["Player"].str.contains("Team|Total|Totals", na=False)]
    pitching = pitching.rename(columns={"Player": "Name"})
    pitching["Name"] = pitching["Name"].apply(fix_name)

    # Convert numeric columns
    for col in ["GS", "ERA", "WHIP", "SO", "BB", "IP", "HR"]:
        pitching[col] = pd.to_numeric(pitching[col], errors="coerce").fillna(0)

    # Filter to starters only (at least 1 game started)
    starters = pitching[pitching["GS"] >= 1].copy()

    # Calculate K/9 and BB/9
    starters["K9"] = (starters["SO"] / starters["IP"] * 9).round(2)
    starters["BB9"] = (starters["BB"] / starters["IP"] * 9).round(2)
    starters["HR9"] = (starters["HR"] / starters["IP"] * 9).round(2)

    # Sort by games started, take top N
    starters = starters.sort_values("GS", ascending=False).head(top_n)

    cols = ["Name", "GS", "IP", "ERA", "WHIP", "K9", "BB9", "HR9"]
    starters = starters[cols].reset_index(drop=True)

    os.makedirs(STATS_DIR, exist_ok=True)
    starters.to_csv(stats_path, index=False)
    print(f"Saved {year} pitching stats to {stats_path}")

    return starters

def build_pitchers(df: pd.DataFrame) -> list[Pitcher]:
    """Convert a pitching dataframe into a list of Pitcher objects."""
    pitchers = []

    for _, row in df.iterrows():
        pitcher = Pitcher(
            name=row["Name"],
            games_started=int(row["GS"]),
            innings_pitched=float(row["IP"]),
            era=float(row["ERA"]),
            whip=float(row["WHIP"]),
            k_per_9=float(row["K9"]),
            bb_per_9=float(row["BB9"]),
            hr_per_9=float(row["HR9"]),
        )
        pitchers.append(pitcher)

    return pitchers

if __name__ == "__main__":
    # Quick test
    df = fetch_mariners_pitching(2001)
    print(f"\n2001 Mariners Top Starters:\n")
    print(df)

    df2 = fetch_mariners_pitching(2024)
    print(f"\n2024 Mariners Top Starters:\n")
    print(df2)