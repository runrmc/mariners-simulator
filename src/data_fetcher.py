import pandas as pd
import requests
import os
from io import StringIO
from pybaseball import cache
cache.enable()

STATS_DIR = "data/stats"

def fix_name(name: str) -> str:
    """Fix encoding issues in player names."""
    name = str(name)
    # Remove suffixes like *, #
    name = name.replace("*", "").replace("#", "").strip()
    # Fix \x escape sequences (2024-style)
    if "\\" in name:
        try:
            name = bytes(name, "utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")
        except Exception:
            pass
    # Fix garbled latin encoding (2001-style)
    try:
        name = name.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return name


def fetch_mariners_batting(year: int) -> pd.DataFrame:
    """Pull Mariners batting stats for a given year and cache locally."""
    stats_path = f"{STATS_DIR}/mariners_{year}_batting.csv"

    if os.path.exists(stats_path):
        print(f"Loading {year} stats from cache...")
        return pd.read_csv(stats_path)

    print(f"Fetching {year} Mariners batting stats from Baseball Reference...")

    url = f"https://www.baseball-reference.com/teams/SEA/{year}.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {year}: HTTP {response.status_code}")

    html = response.text
    tables = pd.read_html(StringIO(html))

    # Table 0 is the full season batting table
    batting = tables[0].copy()

    # Clean up — remove summary rows
    batting = batting[batting["Player"].notna()]
    batting = batting[batting["Player"] != "Player"]
    batting = batting[~batting["Player"].str.contains("Team|Total|Totals", na=False)]

    # Rename Player to Name for consistency
    batting = batting.rename(columns={"Player": "Name"})
    batting["Name"] = batting["Name"].apply(fix_name)

    # Convert numeric columns
    for col in ["G", "PA", "H", "2B", "3B", "HR", "BB", "SO"]:
        batting[col] = pd.to_numeric(batting[col], errors="coerce").fillna(0).astype(int)

    cols = ["Name", "G", "PA", "H", "2B", "3B", "HR", "BB", "SO"]
    batting = batting[cols].reset_index(drop=True)

    os.makedirs(STATS_DIR, exist_ok=True)
    batting.to_csv(stats_path, index=False)
    print(f"Saved {year} stats to {stats_path}")

    return batting


def load_roster(year: int) -> pd.DataFrame:
    """Load a cached roster, fetching it first if needed."""
    return fetch_mariners_batting(year)