from src.data.batting import fetch_mariners_batting
from src.data.pitching import fetch_mariners_pitching, build_pitchers
from src.models.roster import build_roster, sort_batting_order
from src.simulation.game import simulate_game
import random


def run_quick_sim(year1: int, year2: int, n_games: int):
    """Run up to 1000 simulations between two years, return summary results."""
    print(f"\nLoading rosters...")

    df_b1 = fetch_mariners_batting(year1)
    df_p1 = fetch_mariners_pitching(year1)
    roster1 = sort_batting_order(build_roster(df_b1))
    pitchers1 = build_pitchers(df_p1)

    df_b2 = fetch_mariners_batting(year2)
    df_p2 = fetch_mariners_pitching(year2)
    roster2 = sort_batting_order(build_roster(df_b2))
    pitchers2 = build_pitchers(df_p2)

    if not roster1 or not roster2:
        print("  Could not build rosters. Try different years.")
        return

    print(f"\nSimulating {n_games} game(s) between {year1} and {year2} Mariners...\n")

    wins1 = 0
    wins2 = 0
    total_runs1 = 0
    total_runs2 = 0
    run_history1 = []
    run_history2 = []

    for i in range(n_games):
        if n_games > 1 and (i + 1) % 50 == 0:
            print(f"  Simulating game {i + 1}/{n_games}...")

        # Randomly select pitchers each game
        pitcher1 = random.choice(pitchers1)
        pitcher2 = random.choice(pitchers2)

        result = simulate_game(
            roster1, roster2,
            home_year=year1, away_year=year2,
            home_pitcher=pitcher1, away_pitcher=pitcher2,
            verbose=False
        )

        total_runs1 += result["home_score"]
        total_runs2 += result["away_score"]
        run_history1.append(result["home_score"])
        run_history2.append(result["away_score"])

        if result["winner"] == year1:
            wins1 += 1
        else:
            wins2 += 1

    win_pct1 = wins1 / n_games * 100
    win_pct2 = wins2 / n_games * 100
    avg_runs1 = total_runs1 / n_games
    avg_runs2 = total_runs2 / n_games

    print(f"\n{'='*55}")
    print(f"  QUICK SIM RESULTS — {n_games} games")
    print(f"{'='*55}")
    print(f"  {year1} Mariners: {wins1} wins ({win_pct1:.1f}%)  avg {avg_runs1:.1f} runs/game")
    print(f"  {year2} Mariners: {wins2} wins ({win_pct2:.1f}%)  avg {avg_runs2:.1f} runs/game")
    print(f"{'='*55}")

    champion = year1 if wins1 > wins2 else year2
    print(f"  🏆 {champion} Mariners win the simulation series!")
    print(f"{'='*55}\n")

    return {
        "year1": year1,
        "year2": year2,
        "wins1": wins1,
        "wins2": wins2,
        "win_pct1": win_pct1,
        "win_pct2": win_pct2,
        "avg_runs1": avg_runs1,
        "avg_runs2": avg_runs2,
        "run_history1": run_history1,
        "run_history2": run_history2,
        "n_games": n_games,
    }