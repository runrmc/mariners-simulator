from dataclasses import dataclass, field


@dataclass
class Pitcher:
    name: str
    games_started: int
    innings_pitched: float
    era: float
    whip: float
    k_per_9: float
    bb_per_9: float
    hr_per_9: float

    # Game tracking stats
    innings_pitched_game: float = field(default=0.0, init=False)
    hits_allowed: int = field(default=0, init=False)
    runs_allowed: int = field(default=0, init=False)
    walks_allowed: int = field(default=0, init=False)
    strikeouts_game: int = field(default=0, init=False)
    hrs_allowed: int = field(default=0, init=False)

    def reset_game_stats(self):
        """Reset per-game tracking stats."""
        self.innings_pitched_game = 0.0
        self.hits_allowed = 0
        self.runs_allowed = 0
        self.walks_allowed = 0
        self.strikeouts_game = 0
        self.hrs_allowed = 0

    def get_modifier(self) -> dict:
        """
        Return probability modifiers based on pitcher quality.
        A league-average ERA is ~4.50. We scale modifiers around that.
        Good pitchers suppress hits, walks, HRs and increase strikeouts.
        """
        era_diff = self.era - 4.50

        hit_mod = era_diff * 0.005
        k_mod = -era_diff * 0.005
        bb_mod = era_diff * 0.003
        hr_mod = era_diff * 0.002

        return {
            "hit_mod": hit_mod,
            "k_mod": k_mod,
            "bb_mod": bb_mod,
            "hr_mod": hr_mod,
        }

    def record_result(self, result: str):
        """Track what happened during a plate appearance."""
        if result in ("single", "double", "triple", "home_run"):
            self.hits_allowed += 1
        if result == "home_run":
            self.hrs_allowed += 1
        if result == "walk":
            self.walks_allowed += 1
        if result == "strikeout":
            self.strikeouts_game += 1

    def __str__(self):
        return (
            f"{self.name} | "
            f"ERA:{self.era:.2f} "
            f"WHIP:{self.whip:.2f} "
            f"K/9:{self.k_per_9:.1f} "
            f"BB/9:{self.bb_per_9:.1f}"
        )