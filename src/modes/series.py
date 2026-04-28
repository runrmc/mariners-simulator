from src.data.batting import fetch_mariners_batting
from src.data.pitching import fetch_mariners_pitching, build_pitchers
from src.models.roster import build_roster, sort_batting_order
from src.simulation.game import simulate_game
from src.output.box_score import (
    generate_box_score, get_player_game_stats,
    accumulate_stats, get_series_mvp
)


def print_series_status(year1: int, year2: int, wins1: int, wins2: int, game_num: int):
    """Print the current series status."""
    print(f"\n  {'='*45}")
    print(f"  Series Status — Game {game_num}")
    print(f"  {year1} Mariners: {wins1} win(s)")
    print(f"  {year2} Mariners: {wins2} win(s)")
    print(f"  {'='*45}\n")


def print_mvp(mvp_name: str, mvp_stats: dict, year: int):
    """Print the series MVP."""
    avg = mvp_stats['hits'] / mvp_stats['ab'] if mvp_stats['ab'] > 0 else 0
    print(f"\n  🏆 SERIES MVP: {mvp_name} ({year} Mariners)")
    print(f"  {'='*45}")
    print(f"  Games:    {mvp_stats['games']}")
    print(f"  AVG:      {avg:.3f}")
    print(f"  Hits:     {mvp_stats['hits']}")
    print(f"  HR:       {mvp_stats['home_runs']}")
    print(f"  RBI:      {mvp_stats['rbi']}")
    print(f"  BB:       {mvp_stats['walks']}")
    print(f"  K:        {mvp_stats['strikeouts']}")
    print(f"  {'='*45}\n")


def run_series(year1: int, year2: int):
    """Run a best-of-7 series between two years."""
    print(f"\nLoading rosters...")

    df_b1 = fetch_mariners_batting(year1)
    df_p1 = fetch_mariners_pitching(year1, top_n=3)
    roster1 = sort_batting_order(build_roster(df_b1))
    pitchers1 = build_pitchers(df_p1)

    df_b2 = fetch_mariners_batting(year2)
    df_p2 = fetch_mariners_pitching(year2, top_n=3)
    roster2 = sort_batting_order(build_roster(df_b2))
    pitchers2 = build_pitchers(df_p2)

    if not roster1 or not roster2:
        print("  Could not build rosters. Try different years.")
        return

    print(f"\n  {year1} Rotation: {', '.join(p.name for p in pitchers1)}")
    print(f"  {year2} Rotation: {', '.join(p.name for p in pitchers2)}")

    wins1 = 0
    wins2 = 0
    game_num = 1
    accumulated_stats = {}

    while wins1 < 4 and wins2 < 4:
        # Rotate pitchers: game 1->0, game 2->1, game 3->2, game 4->0...
        pitcher1 = pitchers1[(game_num - 1) % len(pitchers1)]
        pitcher2 = pitchers2[(game_num - 1) % len(pitchers2)]

        print(f"\n{'='*55}")
        print(f"  GAME {game_num} — {year2} Mariners vs {year1} Mariners")
        print(f"  {year2} SP: {pitcher2.name}  |  {year1} SP: {pitcher1.name}")
        print(f"{'='*55}")

        result = simulate_game(
            roster1, roster2,
            home_year=year1, away_year=year2,
            home_pitcher=pitcher1, away_pitcher=pitcher2,
            verbose=False, inning_by_inning=True
        )

        # Print box score
        print(generate_box_score(result))

        # Accumulate stats
        home_stats = get_player_game_stats(result["home_roster"])
        away_stats = get_player_game_stats(result["away_roster"])
        accumulated_stats = accumulate_stats(accumulated_stats, home_stats)
        accumulated_stats = accumulate_stats(accumulated_stats, away_stats)

        if result["winner"] == year1:
            wins1 += 1
        else:
            wins2 += 1

        print_series_status(year1, year2, wins1, wins2, game_num)
        game_num += 1

    # Series winner
    series_winner = year1 if wins1 > wins2 else year2
    print(f"\n{'='*55}")
    print(f"  🏆 {series_winner} MARINERS WIN THE SERIES!")
    print(f"  {year1}: {wins1} wins  |  {year2}: {wins2} wins")
    print(f"{'='*55}")

    # MVP
    mvp_name, mvp_stats = get_series_mvp(accumulated_stats)
    mvp_year = year1 if any(
        p.name == mvp_name for p in roster1
    ) else year2
    print_mvp(mvp_name, mvp_stats, mvp_year)

    # Export option
    choice = input("  Export series results to CSV? (y/n): ").strip().lower()
    if choice == "y":
        from src.output.exporter import export_series_csv
        export_series_csv(result, year1, year2)

    return {
        "winner": series_winner,
        "wins1": wins1,
        "wins2": wins2,
        "mvp": mvp_name,
        "mvp_stats": mvp_stats,
        "accumulated_stats": accumulated_stats
    }