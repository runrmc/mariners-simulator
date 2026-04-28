import pandas as pd
import requests
import os
from io import StringIO
from pybaseball import cache
from datetime import date
import time
cache.enable()

STATS_DIR = "data/stats"


def fix_name(name: str) -> str:
    """Fix encoding issues and clean suffixes from player names."""
    name = str(name)
    name = name.replace("*", "").replace("#", "").strip()
    if "\\" in name:
        try:
            name = bytes(name, "utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")
        except Exception:
            pass
    try:
        name = name.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return name


def fetch_mariners_batting(year: int) -> pd.DataFrame:
    """Pull Mariners batting stats for a given year and cache locally."""
    stats_path = f"{STATS_DIR}/mariners_{year}_batting.csv"

    if os.path.exists(stats_path):
        print(f"Loading {year} batting stats from cache...")
        return pd.read_csv(stats_path)

    print(f"Fetching {year} Mariners batting stats from Baseball Reference...")

    url = f"https://www.baseball-reference.com/teams/SEA/{year}.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    time.sleep(1) # Be polite to Baseball Reference
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {year}: HTTP {response.status_code}")

    html = response.text
    tables = pd.read_html(StringIO(html))

    batting = tables[0].copy()

    batting = batting[batting["Player"].notna()]
    batting = batting[batting["Player"] != "Player"]
    batting = batting[~batting["Player"].str.contains("Team|Total|Totals", na=False)]
    batting = batting.rename(columns={"Player": "Name"})
    batting["Name"] = batting["Name"].apply(fix_name)

    for col in ["G", "PA", "H", "2B", "3B", "HR", "BB", "SO"]:
        batting[col] = pd.to_numeric(batting[col], errors="coerce").fillna(0).astype(int)

    cols = ["Name", "G", "PA", "H", "2B", "3B", "HR", "BB", "SO"]
    batting = batting[cols].reset_index(drop=True)

    os.makedirs(STATS_DIR, exist_ok=True)
    batting.to_csv(stats_path, index=False)
    print(f"Saved {year} batting stats to {stats_path}")

    return batting


def get_latest_completed_season() -> int:
    """
    Returns the most recent completed MLB season.
    If we're before October 1, the previous year is the last complete season.
    """
    today = date.today()
    if today.month >= 10:
        return today.year
    else:
        return today.year - 1