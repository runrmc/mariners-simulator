import random
from src.roster import Player, build_roster
from src.at_bat import simulate_at_bat, describe_result


class BasePaths:
    """Tracks runners on base."""
    def __init__(self):
        self.first = False
        self.second = False
        self.third = False

    def advance_all(self, bases: int) -> int:
        """Advance all runners by a number of bases. Returns runs scored."""
        runs = 0
        # Advance in reverse order to avoid overwriting
        if self.third:
            if bases >= 1:
                runs += 1
                self.third = False
        if self.second:
            if bases >= 2:
                runs += 1
                self.second = False
            elif bases == 1:
                self.third = True
                self.second = False
        if self.first:
            if bases >= 3:
                runs += 1
                self.first = False
            elif bases == 2:
                self.second = True
                self.first = False
            elif bases == 1:
                self.third = self.third  # already handled
                self.second = self.second  # already handled
                # runner on first moves to second only if second is open
                if not self.second:
                    self.second = True
                    self.first = False
        return runs

    def place_runner(self, base: int):
        """Place a new runner on a base."""
        if base == 1:
            self.first = True
        elif base == 2:
            self.second = True
        elif base == 3:
            self.third = True

    def __str__(self):
        bases = []
        if self.first: bases.append("1st")
        if self.second: bases.append("2nd")
        if self.third: bases.append("3rd")
        return ", ".join(bases) if bases else "empty"


def simulate_half_inning(roster: list[Player], lineup_pos: int, verbose: bool = True) -> tuple[int, int]:
    """
    Simulate one half-inning.
    Returns (runs scored, new lineup position).
    """
    outs = 0
    runs = 0
    bases = BasePaths()

    if verbose:
        print(f"  Runners: {bases}")

    while outs < 3:
        player = roster[lineup_pos % len(roster)]
        lineup_pos += 1
        result = simulate_at_bat(player)
        description = describe_result(player.name, result)

        if result == "out" or result == "strikeout":
            outs += 1
            if verbose:
                print(f"  {description} (Out {outs}) | Bases: {bases}")

        elif result == "walk":
            # Walk — force runners if bases occupied
            scored = 0
            if bases.first and bases.second and bases.third:
                scored = 1
                bases.third = False
            elif bases.first and bases.second:
                bases.third = True
            elif bases.first:
                bases.second = True
            bases.first = True
            runs += scored
            if verbose:
                print(f"  {description} | Bases: {bases} | Runs: +{scored}")

        elif result == "single":
            scored = bases.advance_all(1)
            bases.place_runner(1)
            runs += scored
            if verbose:
                print(f"  {description} | Bases: {bases} | Runs: +{scored}")

        elif result == "double":
            scored = bases.advance_all(2)
            bases.place_runner(2)
            runs += scored
            if verbose:
                print(f"  {description} | Bases: {bases} | Runs: +{scored}")

        elif result == "triple":
            scored = bases.advance_all(3)
            bases.place_runner(3)
            runs += scored
            if verbose:
                print(f"  {description} | Bases: {bases} | Runs: +{scored}")

        elif result == "home_run":
            # Everyone scores including the batter
            scored = bases.advance_all(4)
            scored += 1  # batter scores
            bases.first = False
            bases.second = False
            bases.third = False
            runs += scored
            if verbose:
                print(f"  {description} | Bases: {bases} | Runs: +{scored}")

    return runs, lineup_pos


def simulate_game(home_roster: list[Player], away_roster: list[Player],
                  home_year: int, away_year: int, verbose: bool = True) -> dict:
    """Simulate a full 9-inning game between two rosters."""
    home_score = 0
    away_score = 0
    home_lineup_pos = 0
    away_lineup_pos = 0

    if verbose:
        print(f"\n{'='*50}")
        print(f"  {away_year} Mariners vs {home_year} Mariners")
        print(f"{'='*50}\n")

    for inning in range(1, 10):
        if verbose:
            print(f"--- Inning {inning} Top ({away_year} Mariners batting) ---")
        runs, away_lineup_pos = simulate_half_inning(away_roster, away_lineup_pos, verbose)
        away_score += runs
        if verbose:
            print(f"  >> {away_year} scores {runs} | Total: {away_score}\n")

        if verbose:
            print(f"--- Inning {inning} Bottom ({home_year} Mariners batting) ---")
        runs, home_lineup_pos = simulate_half_inning(home_roster, home_lineup_pos, verbose)
        home_score += runs
        if verbose:
            print(f"  >> {home_year} scores {runs} | Total: {home_score}\n")

    if verbose:
        print(f"{'='*50}")
        print(f"  FINAL SCORE")
        print(f"  {away_year} Mariners: {away_score}")
        print(f"  {home_year} Mariners: {home_score}")
        winner = away_year if away_score > home_score else home_year if home_score > away_score else "TIE"
        if winner == "TIE":
            print(f"  Result: TIE")
        else:
            print(f"  Winner: {winner} Mariners!")
        print(f"{'='*50}\n")

    return {
        "home_year": home_year,
        "away_year": away_year,
        "home_score": home_score,
        "away_score": away_score,
        "winner": away_year if away_score > home_score else home_year if home_score > away_score else "TIE"
    }


if __name__ == "__main__":
    from src.data_fetcher import fetch_mariners_batting

    # Load two rosters to test
    df_2024 = fetch_mariners_batting(2024)
    df_2001 = fetch_mariners_batting(2001)

    roster_2024 = build_roster(df_2024)
    roster_2001 = build_roster(df_2001)

    simulate_game(roster_2024, roster_2001, home_year=2024, away_year=2001)