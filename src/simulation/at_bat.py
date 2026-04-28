import random
from src.models.player import Player
from src.models.pitcher import Pitcher

OUTCOMES = ["single", "double", "triple", "home_run", "walk", "strikeout", "out"]


def simulate_at_bat(player: Player, pitcher: Pitcher = None) -> str:
    """
    Simulate a single plate appearance.
    If a pitcher is provided, their stats modify the batter's probabilities.
    """
    p_single = player.prob_single
    p_double = player.prob_double
    p_triple = player.prob_triple
    p_hr = player.prob_hr
    p_walk = player.prob_walk
    p_strikeout = player.prob_strikeout
    p_out = player.prob_out

    if pitcher is not None:
        mod = pitcher.get_modifier()

        hit_mod = mod["hit_mod"]
        k_mod = mod["k_mod"]
        bb_mod = mod["bb_mod"]
        hr_mod = mod["hr_mod"]

        total_hit_prob = p_single + p_double + p_triple + p_hr
        if total_hit_prob > 0:
            p_single = max(0.0, p_single + hit_mod * (p_single / total_hit_prob))
            p_double = max(0.0, p_double + hit_mod * (p_double / total_hit_prob))
            p_triple = max(0.0, p_triple + hit_mod * (p_triple / total_hit_prob))
            p_hr = max(0.0, p_hr + hr_mod)

        p_walk = max(0.0, p_walk + bb_mod)
        p_strikeout = max(0.0, p_strikeout + k_mod)

        p_out = max(0.0, 1.0 - (
            p_single + p_double + p_triple +
            p_hr + p_walk + p_strikeout
        ))

    weights = [p_single, p_double, p_triple, p_hr, p_walk, p_strikeout, p_out]

    total = sum(weights)
    if total <= 0:
        weights = [player.prob_single, player.prob_double, player.prob_triple,
                   player.prob_hr, player.prob_walk, player.prob_strikeout, player.prob_out]

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