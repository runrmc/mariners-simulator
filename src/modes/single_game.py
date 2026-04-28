from src.data.batting import fetch_mariners_batting
from src.data.pitching import fetch_mariners_pitching, build_pitchers
from src.models.roster import build_roster, sort_batting_order
from src.simulation.game import simulate_game
from src.output.box_score import generate_box_score


def select_pitcher(pitchers, year: int) -> object:
    """Let the user select a starting pitcher from the top 5."""
    print(f"\n  {year} Mariners Starting Pitchers:")
    for i, p in enumerate(pitchers, 1):
        print(f"    {i}. {p.name:<25} ERA: {p.era:.2f}  WHIP: {p.whip:.2f}  K/9: {p.k_per_9:.1f}")

    while True:
        try:
            choice = int(input(f"\n  Select pitcher for {year} (1-{len(pitchers)}): "))
            if 1 <= choice <= len(pitchers):
                return pitchers[choice - 1]
            else:
                print(f"  Please enter a number between 1 and {len(pitchers)}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def print_lineup(roster, year: int):
    """Print the optimized batting order."""
    print(f"\n  {year} Mariners Batting Order:")
    for i, player in enumerate(roster[:9], 1):
        obp = (player.prob_single + player.prob_double +
               player.prob_triple + player.prob_hr + player.prob_walk)
        slg = (player.prob_single + 2 * player.prob_double +
               3 * player.prob_triple + 4 * player.prob_hr)
        print(f"    {i}. {player.name:<25} OBP: {obp:.3f}  SLG: {slg:.3f}")


def run_single_game(year1: int, year2: int):
    """Run a single game simulation between two years."""
    print(f"\nLoading rosters and pitching staffs...")

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

    # Show lineups
    print_lineup(roster1, year1)
    print_lineup(roster2, year2)

    # Select pitchers
    pitcher1 = select_pitcher(pitchers1, year1)
    pitcher2 = select_pitcher(pitchers2, year2)

    print(f"\n  Matchup: {pitcher2.name} ({year2}) vs {pitcher1.name} ({year1})")
    input("\n  Press Enter to start the game...")

    # Simulate
    result = simulate_game(
        roster1, roster2,
        home_year=year1, away_year=year2,
        home_pitcher=pitcher1, away_pitcher=pitcher2,
        verbose=True
    )

    # Box score
    print(generate_box_score(result))

    return result