from src.models.player import Player
from src.models.pitcher import Pitcher


def generate_box_score(result: dict) -> str:
    """Generate a text box score from a game result dictionary."""
    home_year = result["home_year"]
    away_year = result["away_year"]
    home_score = result["home_score"]
    away_score = result["away_score"]
    winner = result["winner"]
    innings = result["innings"]
    home_roster = result["home_roster"]
    away_roster = result["away_roster"]
    home_pitcher = result.get("home_pitcher")
    away_pitcher = result.get("away_pitcher")

    lines = []
    lines.append(f"\n{'='*65}")
    lines.append(f"  BOX SCORE — {away_year} Mariners vs {home_year} Mariners")
    lines.append(f"  Final: {away_year} {away_score}, {home_year} {home_score} ({innings} innings)")
    lines.append(f"  Winner: {winner} Mariners")
    lines.append(f"{'='*65}")

    for year, roster, pitcher in [
        (away_year, away_roster, away_pitcher),
        (home_year, home_roster, home_pitcher)
    ]:
        lines.append(f"\n  {year} Mariners Batting")
        lines.append(f"  {'Player':<25} {'AB':>4} {'H':>4} {'2B':>4} {'3B':>4} {'HR':>4} {'RBI':>4} {'BB':>4} {'K':>4} {'AVG':>6}")
        lines.append(f"  {'-'*63}")

        for player in roster:
            if player.ab == 0 and player.game_walks == 0:
                continue
            avg = f"{player.batting_average:.3f}" if player.ab > 0 else ".000"
            lines.append(
                f"  {player.name:<25} "
                f"{player.ab:>4} "
                f"{player.hits:>4} "
                f"{player.game_doubles:>4} "
                f"{player.game_triples:>4} "
                f"{player.game_hrs:>4} "
                f"{player.game_rbi:>4} "
                f"{player.game_walks:>4} "
                f"{player.game_ks:>4} "
                f"{avg:>6}"
            )

        if pitcher:
            lines.append(f"\n  {year} Starting Pitcher")
            lines.append(f"  {'Pitcher':<25} {'H':>4} {'R':>4} {'BB':>4} {'K':>4} {'HR':>4}")
            lines.append(f"  {'-'*45}")
            lines.append(
                f"  {pitcher.name:<25} "
                f"{pitcher.hits_allowed:>4} "
                f"{pitcher.runs_allowed:>4} "
                f"{pitcher.walks_allowed:>4} "
                f"{pitcher.strikeouts_game:>4} "
                f"{pitcher.hrs_allowed:>4}"
            )

    lines.append(f"\n{'='*65}\n")
    return "\n".join(lines)


def get_player_game_stats(roster: list[Player]) -> list[dict]:
    """Return a list of player stat dicts for a game."""
    stats = []
    for player in roster:
        if player.ab == 0 and player.game_walks == 0:
            continue
        stats.append({
            "name": player.name,
            "ab": player.ab,
            "hits": player.hits,
            "doubles": player.game_doubles,
            "triples": player.game_triples,
            "home_runs": player.game_hrs,
            "rbi": player.game_rbi,
            "walks": player.game_walks,
            "strikeouts": player.game_ks,
            "runs": player.game_runs,
            "avg": player.batting_average,
        })
    return stats


def get_series_mvp(accumulated_stats: dict) -> tuple[str, dict]:
    """
    Determine series MVP based on accumulated stats.
    Scoring: H + 2*HR + RBI + BB - K
    """
    best_player = None
    best_score = -999

    for name, stats in accumulated_stats.items():
        score = (
            stats.get("hits", 0) +
            2 * stats.get("home_runs", 0) +
            stats.get("rbi", 0) +
            stats.get("walks", 0) -
            0.5 * stats.get("strikeouts", 0)
        )
        if score > best_score:
            best_score = score
            best_player = name

    return best_player, accumulated_stats.get(best_player, {})


def accumulate_stats(accumulated: dict, game_stats: list[dict]) -> dict:
    """Add game stats to accumulated series/tournament stats."""
    for stat in game_stats:
        name = stat["name"]
        if name not in accumulated:
            accumulated[name] = {
                "ab": 0, "hits": 0, "doubles": 0, "triples": 0,
                "home_runs": 0, "rbi": 0, "walks": 0, "strikeouts": 0,
                "runs": 0, "games": 0
            }
        accumulated[name]["ab"] += stat["ab"]
        accumulated[name]["hits"] += stat["hits"]
        accumulated[name]["doubles"] += stat["doubles"]
        accumulated[name]["triples"] += stat["triples"]
        accumulated[name]["home_runs"] += stat["home_runs"]
        accumulated[name]["rbi"] += stat["rbi"]
        accumulated[name]["walks"] += stat["walks"]
        accumulated[name]["strikeouts"] += stat["strikeouts"]
        accumulated[name]["runs"] += stat["runs"]
        accumulated[name]["games"] += 1

    return accumulated