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
        era_diff = self.era - 4.50  # positive = worse