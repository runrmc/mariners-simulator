import csv
import os
from datetime import datetime


EXPORTS_DIR = "data/exports"


def ensure_exports_dir():
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_box_score_csv(result: dict, filename: str = None) -> str:
    """Export a game box score to CSV."""
    ensure_exports_dir()
    if not filename:
        filename = f"boxscore_{result['away_year']}_vs_{result['home_year']}_{timestamp()}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            f"Box Score — {result['away_year']} vs {result['home_year']} Mariners"
        ])
        writer.writerow([
            f"Final: {result['away_year']} {result['away_score']}, "
            f"{result['home_year']} {result['home_score']} "
            f"({result['innings']} innings)"
        ])
        writer.writerow([f"Winner: {result['winner']} Mariners"])
        writer.writerow([])

        # Batting stats for each team
        for year, roster, pitcher in [
            (result['away_year'], result['away_roster'], result.get('away_pitcher')),
            (result['home_year'], result['home_roster'], result.get('home_pitcher')),
        ]:
            writer.writerow([f"{year} Mariners Batting"])
            writer.writerow(["Player", "AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG"])

            for player in roster:
                if player.ab == 0 and player.game_walks == 0:
                    continue
                avg = f"{player.batting_average:.3f}" if player.ab > 0 else ".000"
                writer.writerow([
                    player.name, player.ab, player.hits,
                    player.game_doubles, player.game_triples,
                    player.game_hrs, player.game_rbi,
                    player.game_walks, player.game_ks, avg
                ])

            if pitcher:
                writer.writerow([])
                writer.writerow([f"{year} Starting Pitcher"])
                writer.writerow(["Pitcher", "H", "R", "BB", "K", "HR"])
                writer.writerow([
                    pitcher.name, pitcher.hits_allowed,
                    pitcher.runs_allowed, pitcher.walks_allowed,
                    pitcher.strikeouts_game, pitcher.hrs_allowed
                ])
            writer.writerow([])

    print(f"\n  📄 Box score exported to {filepath}")
    return filepath


def export_series_csv(series_result: dict, year1: int, year2: int, filename: str = None) -> str:
    """Export series results and accumulated stats to CSV."""
    ensure_exports_dir()
    if not filename:
        filename = f"series_{year1}_vs_{year2}_{timestamp()}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Series summary
        writer.writerow([f"Series Results — {year1} vs {year2} Mariners"])
        writer.writerow([f"Winner: {series_result['winner']} Mariners"])
        writer.writerow([f"{year1} Wins: {series_result['wins1']}"])
        writer.writerow([f"{year2} Wins: {series_result['wins2']}"])
        writer.writerow([f"Series MVP: {series_result['mvp']}"])
        writer.writerow([])

        # Accumulated stats
        writer.writerow(["Player Stats"])
        writer.writerow(["Player", "G", "AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG"])

        for name, stats in series_result["accumulated_stats"].items():
            avg = stats['hits'] / stats['ab'] if stats.get('ab', 0) > 0 else 0
            writer.writerow([
                name,
                stats.get('games', 0),
                stats.get('ab', 0),
                stats.get('hits', 0),
                stats.get('doubles', 0),
                stats.get('triples', 0),
                stats.get('home_runs', 0),
                stats.get('rbi', 0),
                stats.get('walks', 0),
                stats.get('strikeouts', 0),
                f"{avg:.3f}"
            ])

    print(f"\n  📄 Series results exported to {filepath}")
    return filepath


def export_quick_sim_csv(sim_result: dict, filename: str = None) -> str:
    """Export quick sim results to CSV."""
    ensure_exports_dir()
    if not filename:
        filename = f"quicksim_{sim_result['year1']}_vs_{sim_result['year2']}_{timestamp()}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([f"Quick Sim — {sim_result['year1']} vs {sim_result['year2']} Mariners"])
        writer.writerow([f"Games Simulated: {sim_result['n_games']}"])
        writer.writerow([])
        writer.writerow(["Team", "Wins", "Win %", "Avg Runs/Game"])
        writer.writerow([
            f"{sim_result['year1']} Mariners",
            sim_result['wins1'],
            f"{sim_result['win_pct1']:.1f}%",
            f"{sim_result['avg_runs1']:.2f}"
        ])
        writer.writerow([
            f"{sim_result['year2']} Mariners",
            sim_result['wins2'],
            f"{sim_result['win_pct2']:.1f}%",
            f"{sim_result['avg_runs2']:.2f}"
        ])
        writer.writerow([])

        # Game by game run log
        writer.writerow(["Game Log"])
        writer.writerow(["Game", f"{sim_result['year1']} Runs", f"{sim_result['year2']} Runs", "Winner"])
        for i, (r1, r2) in enumerate(zip(sim_result['run_history1'], sim_result['run_history2']), 1):
            winner = sim_result['year1'] if r1 > r2 else sim_result['year2']
            writer.writerow([i, r1, r2, f"{winner} Mariners"])

    print(f"\n  📄 Quick sim results exported to {filepath}")
    return filepath


def export_tournament_csv(tournament_result: dict, filename: str = None) -> str:
    """Export tournament results to CSV."""
    ensure_exports_dir()
    if not filename:
        filename = f"tournament_{timestamp()}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["Tournament Results"])
        writer.writerow([f"Champion: {tournament_result['champion']} Mariners"])
        writer.writerow([f"MVP: {tournament_result['mvp']}"])
        writer.writerow([])

        writer.writerow(["Player Stats"])
        writer.writerow(["Player", "G", "AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG"])

        for name, stats in tournament_result["all_stats"].items():
            if stats.get('ab', 0) == 0:
                continue
            avg = stats['hits'] / stats['ab'] if stats.get('ab', 0) > 0 else 0
            writer.writerow([
                name,
                stats.get('games', 0),
                stats.get('ab', 0),
                stats.get('hits', 0),
                stats.get('doubles', 0),
                stats.get('triples', 0),
                stats.get('home_runs', 0),
                stats.get('rbi', 0),
                stats.get('walks', 0),
                stats.get('strikeouts', 0),
                f"{avg:.3f}"
            ])

    print(f"\n  📄 Tournament results exported to {filepath}")
    return filepath