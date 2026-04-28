from src.models.player import Player
from src.models.pitcher import Pitcher
from src.simulation.at_bat import simulate_at_bat, describe_result
from src.simulation.base_running import BasePaths


def simulate_half_inning(
    roster: list[Player],
    lineup_pos: int,
    pitcher: Pitcher = None,
    verbose: bool = True,
    inning: int = 0,
    is_top: bool = True
) -> tuple[int, int, list[dict]]:
    """
    Simulate one half-inning.
    Returns (runs scored, new lineup position, play-by-play log).
    """
    outs = 0
    runs = 0
    bases = BasePaths()
    plays = []

    while outs < 3:
        player = roster[lineup_pos % len(roster)]
        lineup_pos += 1
        result = simulate_at_bat(player, pitcher)
        rbi = 0

        if result in ("out", "strikeout"):
            outs += 1
            player.record_result(result)

        elif result == "walk":
            scored = bases.advance_walk()
            runs += scored
            rbi = scored
            player.record_result(result, rbi)

        elif result == "single":
            scored = bases.advance_all(1)
            bases.place_runner(1)
            runs += scored
            rbi = scored
            player.record_result(result, rbi)

        elif result == "double":
            scored = bases.advance_all(2)
            bases.place_runner(2)
            runs += scored
            rbi = scored
            player.record_result(result, rbi)

        elif result == "triple":
            scored = bases.advance_all(3)
            bases.place_runner(3)
            runs += scored
            rbi = scored
            player.record_result(result, rbi)

        elif result == "home_run":
            scored = bases.advance_all(4)
            scored += 1
            bases.clear()
            runs += scored
            rbi = scored
            player.record_result(result, rbi)
            player.game_runs += 1

        if pitcher:
            pitcher.record_result(result)

        description = describe_result(player.name, result)
        play = {
            "player": player.name,
            "result": result,
            "description": description,
            "outs": outs,
            "runs": rbi,
            "bases": str(bases),
        }
        plays.append(play)

        if verbose:
            if result in ("out", "strikeout"):
                print(f"  {description} (Out {outs}) | Bases: {bases}")
            else:
                print(f"  {description} | Bases: {bases} | Runs: +{rbi}")

    return runs, lineup_pos, plays


def simulate_game(
    home_roster: list[Player],
    away_roster: list[Player],
    home_year: int,
    away_year: int,
    home_pitcher: Pitcher = None,
    away_pitcher: Pitcher = None,
    verbose: bool = True,
    inning_by_inning: bool = False,
) -> dict:
    """Simulate a full game between two rosters."""

    # Reset all player game stats
    for p in home_roster:
        p.reset_game_stats()
    for p in away_roster:
        p.reset_game_stats()
    if home_pitcher:
        home_pitcher.reset_game_stats()
    if away_pitcher:
        away_pitcher.reset_game_stats()

    home_score = 0
    away_score = 0
    home_lineup_pos = 0
    away_lineup_pos = 0
    inning_scores = []
    all_plays = []

    if verbose:
        print(f"\n{'='*55}")
        print(f"  {away_year} Mariners vs {home_year} Mariners")
        if away_pitcher:
            print(f"  {away_year} SP: {away_pitcher.name} (ERA: {away_pitcher.era})")
        if home_pitcher:
            print(f"  {home_year} SP: {home_pitcher.name} (ERA: {home_pitcher.era})")
        print(f"{'='*55}\n")

    inning = 1
    while True:
        # Top of inning
        if verbose and not inning_by_inning:
            print(f"--- Inning {inning} Top ({away_year} Mariners batting) ---")
        elif inning_by_inning:
            print(f"--- Inning {inning} ---")

        runs, away_lineup_pos, plays = simulate_half_inning(
            away_roster, away_lineup_pos, away_pitcher,
            verbose=verbose and not inning_by_inning,
            inning=inning, is_top=True
        )
        away_score += runs
        all_plays.extend(plays)

        if verbose and not inning_by_inning:
            print(f"  >> {away_year} scores {runs} | Total: {away_score}\n")
        elif inning_by_inning:
            print(f"  {away_year}: {runs} run(s) | Score: {away_score}-{home_score}")

        # Bottom of inning
        if verbose and not inning_by_inning:
            print(f"--- Inning {inning} Bottom ({home_year} Mariners batting) ---")

        runs, home_lineup_pos, plays = simulate_half_inning(
            home_roster, home_lineup_pos, home_pitcher,
            verbose=verbose and not inning_by_inning,
            inning=inning, is_top=False
        )
        home_score += runs
        all_plays.extend(plays)

        if verbose and not inning_by_inning:
            print(f"  >> {home_year} scores {runs} | Total: {home_score}\n")
        elif inning_by_inning:
            print(f"  {home_year}: {runs} run(s) | Score: {home_score}-{away_score}\n")

        inning_scores.append({
            "inning": inning,
            "away": away_score,
            "home": home_score
        })

        # Check for extra innings
        if inning >= 9 and home_score != away_score:
            break
        elif inning >= 9 and home_score == away_score:
            if verbose or inning_by_inning:
                print(f"  ** Tied at {home_score} after {inning} innings — extras! **\n")
        elif inning < 9:
            pass

        if inning >= 18:
            # Hard cap at 18 innings
            break

        inning += 1

    winner = away_year if away_score > home_score else home_year
    if verbose or inning_by_inning:
        print(f"{'='*55}")
        print(f"  FINAL SCORE ({inning} innings)")
        print(f"  {away_year} Mariners: {away_score}")
        print(f"  {home_year} Mariners: {home_score}")
        print(f"  Winner: {winner} Mariners!")
        print(f"{'='*55}\n")

    return {
        "home_year": home_year,
        "away_year": away_year,
        "home_score": home_score,
        "away_score": away_score,
        "winner": winner,
        "innings": inning,
        "inning_scores": inning_scores,
        "home_roster": home_roster,
        "away_roster": away_roster,
        "home_pitcher": home_pitcher,
        "away_pitcher": away_pitcher,
        "plays": all_plays,
    }