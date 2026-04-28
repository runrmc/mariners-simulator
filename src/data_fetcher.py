import pandas as pd
from pybaseball import batting_stats_bref
import os

from pybaseball import cache
cache.enable()

STATS_DIR = "data/stats"


def fetch_mariners_batting(year: int) -> pd.DataFrame:
    """Pull Mariners batting stats for a given year and cache locally."""
    stats_path = f"{STATS_DIR}/mariners_{year}_batting.csv"

    if os.path.exists(stats_path):
        print(f"Loading {year} stats from cache...")
        return pd.read_csv(stats_path)

    print(f"Fetching {year} Mariners batting stats from Baseball Reference...")
    stats = batting_stats_bref(year)
    mariners = stats[stats["Tm"].str.contains("Seattle", na=False)].copy()

    cols = ["Name", "G", "PA", "H", "2B", "3B", "HR", "BB", "SO"]
    mariners = mariners[cols].reset_index(drop=True)

    os.makedirs(STATS_DIR, exist_ok=True)
    mariners.to_csv(stats_path, index=False)
    print(f"Saved {year} stats to {stats_path}")

    return mariners


def load_roster(year: int) -> pd.DataFrame:
    """Load a cached roster, fetching it first if needed."""
    return fetch_mariners_batting(year)


if __name__ == "__main__":
    df = fetch_mariners_batting(2024)
    print(df)