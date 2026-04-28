"""
Run this once to pre-fetch and cache all Mariners season data.
After this runs successfully, the simulator will load everything from cache.
"""
import sys
import time
sys.path.append(".")

from src.data.batting import fetch_mariners_batting
from src.data.pitching import fetch_mariners_pitching

PRIORITY_YEARS = [
    2001, 2002, 2003, 2000, 1997, 2021, 2022, 2025,  # top 8
    2018, 2007, 2023, 2014, 2016, 1996, 2009, 2024,  # top 16
]

ALL_YEARS = list(range(1977, 2026))

def prefetch(years: list[int], delay: float = 4.0):
    total = len(years)
    success = 0
    failed = []

    for i, year in enumerate(years, 1):
        print(f"\n[{i}/{total}] Fetching {year}...")
        try:
            fetch_mariners_batting(year)
            time.sleep(delay)
            fetch_mariners_pitching(year, top_n=5)
            time.sleep(delay)
            success += 1
            print(f"  ✓ {year} complete")
        except Exception as e:
            print(f"  ✗ {year} failed: {e}")
            failed.append(year)
            time.sleep(delay * 2)  # Extra wait after a failure

    print(f"\n{'='*40}")
    print(f"  Done! {success}/{total} seasons cached.")
    if failed:
        print(f"  Failed: {failed}")
        print(f"  Re-run the script to retry failed seasons.")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    mode = input("Fetch [1] Top 16 priority years or [2] All years (1977-2025)? ").strip()
    if mode == "1":
        prefetch(PRIORITY_YEARS)
    else:
        prefetch(ALL_YEARS)