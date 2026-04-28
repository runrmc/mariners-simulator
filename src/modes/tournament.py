import math
import random
from src.data.batting import fetch_mariners_batting, get_latest_completed_season
from src.data.pitching import fetch_mariners_pitching, build_pitchers
from src.models.roster import build_roster, sort_batting_order
from src.simulation.game import simulate_game
from src.output.box_score import (
    get_player_game_stats, accumulate_stats, get_series_mvp
)

LATEST_SEASON = get_latest_completed_season()

# Historical Mariners win totals for seeding
WIN_TOTALS = {
    1977: 64, 1978: 56, 1979: 67, 1980: 59, 1981: 44,
    1982: 76, 1983: 60, 1984: 74, 1985: 74, 1986: 67,
    1987: 78, 1988: 68, 1989: 73, 1990: 77, 1991: 83,
    1992: 64, 1993: 82, 1994: 49, 1995: 79, 1996: 85,
    1997: 90, 1998: 76, 1999: 79, 2000: 91, 2001: 116,
    2002: 93, 2003: 93, 2004: 63, 2005: 69, 2006: 78,
    2007: 88, 2008: 61, 2009: 85, 2010: 61, 2011: 67,
    2012: 75, 2013: 71, 2014: 87, 2015: 76, 2016: 86,
    2017: 78, 2018: 89, 2019: 68, 2020: 27, 2021: 90,
    2022: 90, 2023: 88, 2024: 85, 2025: 90,
}


def get_seed_order(years: list[int]) -> list[int]:
    """Seed teams by win total, highest first."""
    return sorted(years, key=lambda y: WIN_TOTALS.get(y, 70), reverse=True)


def load_teams(years: list[int]) -> tuple[dict, dict]:
    """Load only the rosters and pitchers needed for the tournament."""
    rosters = {}
    pitchers = {}
    print(f"\nLoading {len(years)} teams...")
    for year in years:
        try:
            df_b = fetch_mariners_batting(year)
            df_p = fetch_mariners_pitching(year, top_n=3)
            roster = sort_batting_order(build_roster(df_b))
            staff = build_pitchers(df_p)
            if roster and staff:
                rosters[year] = roster
                pitchers[year] = staff
                print(f"  ✓ {year} Mariners loaded ({WIN_TOTALS.get(year, '?')} wins)")
            else:
                print(f"  ✗ {year} skipped (insufficient data)")
        except Exception as e:
            print(f"  ✗ {year} skipped: {e}")
    return rosters, pitchers


def pick_top_n(n: int) -> list[int]:
    """Return top N seasons by win total."""
    all_years = list(range(1977, LATEST_SEASON + 1))
    sorted_years = sorted(all_years, key=lambda y: WIN_TOTALS.get(y, 70), reverse=True)
    return sorted_years[:n]


def pick_random_8() -> list[int]:
    """Return 8 randomly selected seasons."""
    all_years = list(range(1977, LATEST_SEASON + 1))
    return random.sample(all_years, 8)


def pick_custom_8() -> list[int]:
    """Interactively pick 8 years for the tournament."""
    print(f"\n  Custom Tournament Builder")
    print(f"  {'─'*35}")
    print(f"  Pick 8 teams (years between 1977-{LATEST_SEASON})\n")

    selected = []
    while len(selected) < 8:
        remaining = 8 - len(selected)
        try:
            year = int(input(f"  Enter year {len(selected)+1}/8: "))
            if year < 1977 or year > LATEST_SEASON:
                print(f"    Please enter a year between 1977 and {LATEST_SEASON}.")
            elif year in selected:
                print(f"    {year} already selected. Pick a different year.")
            else:
                wins = WIN_TOTALS.get(year, "?")
                selected.append(year)
                print(f"    ✓ {year} Mariners added ({wins} wins) — {remaining-1} remaining\n")
        except ValueError:
            print("    Invalid input. Please enter a year.")

    seeded = get_seed_order(selected)
    print(f"\n  Your Tournament:")
    print(f"  {'─'*35}")
    for i, year in enumerate(seeded, 1):
        print(f"  Seed {i}: {year} Mariners ({WIN_TOTALS.get(year, '?')} wins)")

    input("\n  Press Enter to start the tournament...")
    return seeded


def print_bracket(years: list[int], title: str):
    """Print the tournament bracket."""
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"  {len(years)} teams seeded by wins")
    print(f"{'='*55}")
    for i, year in enumerate(years, 1):
        wins = WIN_TOTALS.get(year, "?")
        print(f"  Seed {i:>2}: {year} Mariners ({wins} wins)")
    print(f"{'='*55}\n")


def simulate_series(
    year1: int, year2: int,
    roster1, roster2,
    pitchers1, pitchers2,
) -> tuple[int, dict]:
    """Simulate a best-of-7 series. Returns (winner_year, accumulated_stats)."""
    wins1 = 0
    wins2 = 0
    game_num = 1
    accumulated_stats = {}

    while wins1 < 4 and wins2 < 4:
        pitcher1 = pitchers1[(game_num - 1) % len(pitchers1)]
        pitcher2 = pitchers2[(game_num - 1) % len(pitchers2)]

        result = simulate_game(
            roster1, roster2,
            home_year=year1, away_year=year2,
            home_pitcher=pitcher1, away_pitcher=pitcher2,
            verbose=False
        )

        home_stats = get_player_game_stats(result["home_roster"])
        away_stats = get_player_game_stats(result["away_roster"])
        accumulated_stats = accumulate_stats(accumulated_stats, home_stats)
        accumulated_stats = accumulate_stats(accumulated_stats, away_stats)

        if result["winner"] == year1:
            wins1 += 1
        else:
            wins2 += 1

        game_num += 1

    winner = year1 if wins1 > wins2 else year2
    return winner, accumulated_stats


def run_tournament(years: list[int], title: str = "MARINERS ALL-TIME TOURNAMENT"):
    """Run a full single-elimination tournament."""
    seeded = get_seed_order(years)
    print_bracket(seeded, title)

    rosters, pitchers = load_teams(seeded)

    available = [y for y in seeded if y in rosters]
    if len(available) < 2:
        print("Not enough teams loaded to run tournament.")
        return

    remaining = available.copy()
    all_accumulated_stats = {}
    round_num = 1
    round_names = {1: "QUARTERFINALS", 2: "SEMIFINALS", 3: "CHAMPIONSHIP"}

    while len(remaining) > 1:
        round_label = round_names.get(round_num, f"ROUND {round_num}")
        print(f"\n{'='*55}")
        print(f"  {round_label}")
        print(f"{'='*55}")

        next_round = []

        # Handle bye if odd number
        if len(remaining) % 2 != 0:
            bye_team = remaining[0]
            remaining = remaining[1:]
            next_round.append(bye_team)
            print(f"\n  {bye_team} Mariners receive a bye!")

        for i in range(0, len(remaining), 2):
            year1 = remaining[i]
            year2 = remaining[i + 1]

            print(f"\n  #{i+1} {year1} Mariners vs #{i+2} {year2} Mariners")
            print(f"  ({WIN_TOTALS.get(year1,'?')} wins vs {WIN_TOTALS.get(year2,'?')} wins)")

            winner, stats = simulate_series(
                year1, year2,
                rosters[year1], rosters[year2],
                pitchers[year1], pitchers[year2]
            )

            for name, s in stats.items():
                if name not in all_accumulated_stats:
                    all_accumulated_stats[name] = s.copy()
                else:
                    for k, v in s.items():
                        if isinstance(v, (int, float)):
                            all_accumulated_stats[name][k] = (
                                all_accumulated_stats[name].get(k, 0) + v
                            )

            loser = year2 if winner == year1 else year1
            print(f"  ✓ {winner} Mariners advance | {loser} Mariners eliminated")
            next_round.append(winner)

        remaining = next_round
        round_num += 1

    champion = remaining[0]
    print(f"\n{'='*55}")
    print(f"  🏆 TOURNAMENT CHAMPION: {champion} MARINERS!")
    print(f"  ({WIN_TOTALS.get(champion, '?')} regular season wins)")
    print(f"{'='*55}")

    mvp_name, mvp_stats = get_series_mvp(all_accumulated_stats)
    if mvp_name and mvp_stats:
        avg = mvp_stats['hits'] / mvp_stats['ab'] if mvp_stats.get('ab', 0) > 0 else 0
        print(f"\n  🌟 TOURNAMENT MVP: {mvp_name}")
        print(f"  AVG: {avg:.3f}  HR: {mvp_stats.get('home_runs',0)}  RBI: {mvp_stats.get('rbi',0)}")
        print(f"{'='*55}\n")

    return {
        "champion": champion,
        "mvp": mvp_name,
        "mvp_stats": mvp_stats,
        "all_stats": all_accumulated_stats
    }