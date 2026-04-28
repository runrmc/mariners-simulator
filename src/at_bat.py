import random
from src.roster import Player


# Possible outcomes of a plate appearance
OUTCOMES = ["single", "double", "triple", "home_run", "walk", "strikeout", "out"]


def simulate_at_bat(player: Player) -> str:
    """Simulate a single plate appearance for a player based on their stats."""
    weights = [
        player.prob_single,
        player.prob_double,
        player.prob_triple,
        player.prob_hr,
        player.prob_walk,
        player.prob_strikeout,
        player.prob_out,
    ]

    result = random.choices(OUTCOMES, weights=weights, k=1)[0]
    return result


def describe_result(player_name: str, result: str) -> str:
    """Return a human-readable description of an at-bat result."""
    descriptions = {
        "single":    f"{player_name} singles!",
        "double":    f"{player_name} doubles!",
        "triple":    f"{player_name} triples!",
        "home_run":  f"{player_name} hits a HOME RUN!",
        "walk":      f"{player_name} draws a walk.",
        "strikeout": f"{player_name} strikes out.",
        "out":       f"{player_name} is out.",
    }
    return descriptions[result]


if __name__ == "__main__":
    from src.data_fetcher import fetch_mariners_batting
    from src.roster import build_roster

    df = fetch_mariners_batting(2024)
    roster = build_roster(df)

    # Simulate 10 at-bats for Julio Rodriguez
    julio = next(p for p in roster if "Rodr" in p.name)
    print(f"\nSimulating 10 at-bats for {julio.name}:\n")
    for i in range(10):
        result = simulate_at_bat(julio)
        print(f"  AB {i+1}: {describe_result(julio.name, result)}")

    # Simulate a full lineup cycling through once
    print(f"\nFull lineup - one at-bat each:\n")
    for player in roster[:9]:
        result = simulate_at_bat(player)
        print(f"  {describe_result(player.name, result)}")