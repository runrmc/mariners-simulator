import sys
from src.data.batting import get_latest_completed_season


LATEST_SEASON = get_latest_completed_season()
FIRST_SEASON = 1977


def print_banner():
    print(f"""
╔══════════════════════════════════════════════════╗
║       SEATTLE MARINERS TEAM SIMULATOR            ║
║       Who is the greatest M's team ever?         ║
║       Seasons available: {FIRST_SEASON} — {LATEST_SEASON}             ║
╚══════════════════════════════════════════════════╝
""")


def pick_year(prompt: str) -> int:
    """Prompt the user to enter a valid Mariners year."""
    while True:
        try:
            year = int(input(prompt))
            if FIRST_SEASON <= year <= LATEST_SEASON:
                return year
            else:
                print(f"  Please enter a year between {FIRST_SEASON} and {LATEST_SEASON}.")
        except ValueError:
            print("  Invalid input. Please enter a year like 2001.")


def pick_simulations() -> int:
    """Prompt the user to enter number of simulations."""
    while True:
        try:
            n = int(input("  How many games to simulate? (1-1000): "))
            if 1 <= n <= 1000:
                return n
            else:
                print("  Please enter a number between 1 and 1000.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def run_single_game_mode():
    from src.modes.single_game import run_single_game
    print("\n  --- SINGLE GAME MODE ---")
    year1 = pick_year(f"  Enter home team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    year2 = pick_year(f"  Enter away team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    run_single_game(year1, year2)


def run_series_mode():
    from src.modes.series import run_series
    print("\n  --- SERIES MODE (Best of 7) ---")
    year1 = pick_year(f"  Enter first team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    year2 = pick_year(f"  Enter second team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    run_series(year1, year2)


def run_tournament_mode():
    from src.modes.tournament import (
        run_tournament, pick_top_n, pick_random_8, pick_custom_8, get_seed_order
    )
    print("\n  --- TOURNAMENT MODE ---")
    print("  Options:")
    print("    [1] Top 8 seasons by wins")
    print("    [2] Top 16 seasons by wins")
    print("    [3] Custom — pick your own 8 years")
    print("    [4] Random 8 seasons")

    choice = input("\n  Enter choice: ").strip()

    if choice == "1":
        years = pick_top_n(8)
        run_tournament(years, title="TOP 8 MARINERS TOURNAMENT")
    elif choice == "2":
        years = pick_top_n(16)
        run_tournament(years, title="TOP 16 MARINERS TOURNAMENT")
    elif choice == "3":
        years = pick_custom_8()
        run_tournament(years, title="CUSTOM 8-TEAM TOURNAMENT")
    elif choice == "4":
        years = pick_random_8()
        print(f"\n  Randomly selected: {sorted(years)}")
        run_tournament(years, title="RANDOM 8-TEAM TOURNAMENT")
    else:
        print("  Invalid choice.")


def run_quick_sim_mode():
    from src.modes.quick_sim import run_quick_sim
    print("\n  --- QUICK SIM MODE ---")
    year1 = pick_year(f"  Enter first team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    year2 = pick_year(f"  Enter second team year ({FIRST_SEASON}-{LATEST_SEASON}): ")
    n_games = pick_simulations()
    run_quick_sim(year1, year2, n_games)


def main():
    print_banner()

    while True:
        print("  Select a mode:")
        print("    [1] Single Game  — play-by-play, select pitchers")
        print("    [2] Series       — best of 7, pitcher rotation, MVP")
        print("    [3] Tournament   — all Mariners seasons, bracket style")
        print("    [4] Quick Sim    — simulate up to 1000 games, get results")
        print("    [5] Quit")

        choice = input("\n  Enter choice: ").strip()

        if choice == "1":
            run_single_game_mode()
        elif choice == "2":
            run_series_mode()
        elif choice == "3":
            run_tournament_mode()
        elif choice == "4":
            run_quick_sim_mode()
        elif choice == "5":
            print("\n  See you at the ballpark! ⚾\n")
            sys.exit(0)
        else:
            print("  Invalid choice. Please enter 1-5.\n")


if __name__ == "__main__":
    main()