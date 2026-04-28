import sys
from src.data_fetcher import fetch_mariners_batting
from src.roster import build_roster
from src.game import simulate_game


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║       SEATTLE MARINERS TEAM SIMULATOR        ║
║         Who is the greatest M's team?        ║
╚══════════════════════════════════════════════╝
""")


def pick_year(prompt: str) -> int:
    """Prompt the user to enter a valid Mariners year."""
    while True:
        try:
            year = int(input(prompt))
            if 1977 <= year <= 2024:
                return year
            else:
                print("  Please enter a year between 1977 and 2024.")
        except ValueError:
            print("  Invalid input. Please enter a year like 2001.")


def pick_simulations() -> int:
    """Prompt the user to enter number of simulations to run."""
    while True:
        try:
            n = int(input("How many games to simulate? (1-1000): "))
            if 1 <= n <= 1000:
                return n
            else:
                print("  Please enter a number between 1 and 1000.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def run_series(year1: int, year2: int, n_games: int):
    """Run a series of simulated games between two years' rosters."""
    print(f"\nLoading rosters...")
    df1 = fetch_mariners_batting(year1)
    df2 = fetch_mariners_batting(year2)
    roster1 = build_roster(df1)
    roster2 = build_roster(df2)

    if not roster1:
        print(f"  Could not build roster for {year1}. Try a different year.")
        return
    if not roster2:
        print(f"  Could not build roster for {year2}. Try a different year.")
        return

    print(f"\nSimulating {n_games} game(s) between {year1} and {year2} Mariners...\n")

    wins1 = 0
    wins2 = 0
    ties = 0
    total_runs1 = 0
    total_runs2 = 0

    # Show verbose output only for single game
    verbose = n_games == 1

    for i in range(n_games):
        if n_games > 1 and (i + 1) % 10 == 0:
            print(f"  Simulating game {i + 1}/{n_games}...")

        result = simulate_game(roster1, roster2, home_year=year1,
                               away_year=year2, verbose=verbose)

        total_runs1 += result["home_score"]
        total_runs2 += result["away_score"]

        if result["winner"] == year1:
            wins1 += 1
        elif result["winner"] == year2:
            wins2 += 1
        else:
            ties += 1

    # Print series summary
    print(f"""
{'='*50}
  SERIES RESULTS: {n_games} game(s)
{'='*50}
  {year1} Mariners: {wins1} wins  (avg {total_runs1/n_games:.1f} runs/game)
  {year2} Mariners: {wins2} wins  (avg {total_runs2/n_games:.1f} runs/game)
  Ties: {ties}
{'='*50}""")

    if wins1 > wins2:
        print(f"  🏆 {year1} Mariners win the series!")
    elif wins2 > wins1:
        print(f"  🏆 {year2} Mariners win the series!")
    else:
        print(f"  🤝 Series is tied!")
    print(f"{'='*50}\n")


def main():
    print_banner()

    while True:
        print("Options:")
        print("  [1] Simulate a game between two years")
        print("  [2] Quit")
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            year1 = pick_year("Enter first year (e.g. 2001): ")
            year2 = pick_year("Enter second year (e.g. 2024): ")
            n_games = pick_simulations()
            run_series(year1, year2, n_games)

        elif choice == "2":
            print("See you at the ballpark!")
            sys.exit(0)

        else:
            print("  Invalid choice. Please enter 1 or 2.\n")


if __name__ == "__main__":
    main()