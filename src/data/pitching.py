import pandas as pd
import requests
import os
import re
import time
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
    time.sleep(3)

    url = f"https://www.baseball-reference.com/teams/SEA/{year}.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch pitching data for {year}: HTTP {response.status_code}")

    html = response.text

    # Baseball Reference hides some tables in HTML comments — extract them
    commented_tables = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
    extra_html = "\n".join(commented_tables)
    full_html = html + extra_html

    tables = pd.read_html(StringIO(full_html))

    # Find the pitching table by looking for ERA and GS columns
    pitching = None
    for table in tables:
        cols = table.columns.tolist()
        if "ERA" in cols and "GS" in cols and "Player" in cols:
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

    starters = starters[starters["IP"] > 0].copy()
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


from src.models.pitcher import Pitcher


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