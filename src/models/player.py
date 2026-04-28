from dataclasses import dataclass, field


@dataclass
class Player:
    name: str
    games: int
    pa: int
    singles: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    strikeouts: int

    # Calculated probabilities
    prob_single: float = field(default=0.0, init=False)
    prob_double: float = field(default=0.0, init=False)
    prob_triple: float = field(default=0.0, init=False)
    prob_hr: float = field(default=0.0, init=False)
    prob_walk: float = field(default=0.0, init=False)
    prob_strikeout: float = field(default=0.0, init=False)
    prob_out: float = field(default=0.0, init=False)

    # Game tracking stats
    ab: int = field(default=0, init=False)
    hits: int = field(default=0, init=False)
    game_singles: int = field(default=0, init=False)
    game_doubles: int = field(default=0, init=False)
    game_triples: int = field(default=0, init=False)
    game_hrs: int = field(default=0, init=False)
    game_walks: int = field(default=0, init=False)
    game_ks: int = field(default=0, init=False)
    game_rbi: int = field(default=0, init=False)
    game_runs: int = field(default=0, init=False)

    def __post_init__(self):
        if self.pa == 0:
            return
        self.prob_single = self.singles / self.pa
        self.prob_double = self.doubles / self.pa
        self.prob_triple = self.triples / self.pa
        self.prob_hr = self.home_runs / self.pa
        self.prob_walk = self.walks / self.pa
        self.prob_strikeout = self.strikeouts / self.pa
        self.prob_out = max(0.0, 1.0 - (
            self.prob_single + self.prob_double + self.prob_triple +
            self.prob_hr + self.prob_walk + self.prob_strikeout
        ))

    def reset_game_stats(self):
        """Reset per-game tracking stats."""
        self.ab = 0
        self.hits = 0
        self.game_singles = 0
        self.game_doubles = 0
        self.game_triples = 0
        self.game_hrs = 0
        self.game_walks = 0
        self.game_ks = 0
        self.game_rbi = 0
        self.game_runs = 0

    def record_result(self, result: str, rbi: int = 0):
        """Record the result of a plate appearance."""
        if result != "walk":
            self.ab += 1
        if result == "single":
            self.hits += 1
            self.game_singles += 1
        elif result == "double":
            self.hits += 1
            self.game_doubles += 1
        elif result == "triple":
            self.hits += 1
            self.game_triples += 1
        elif result == "home_run":
            self.hits += 1
            self.game_hrs += 1
        elif result == "walk":
            self.game_walks += 1
        elif result == "strikeout":
            self.game_ks += 1
        self.game_rbi += rbi

    @property
    def batting_average(self) -> float:
        return self.hits / self.ab if self.ab > 0 else 0.0

    def __str__(self):
        return (
            f"{self.name} | "
            f"1B:{self.prob_single:.3f} "
            f"2B:{self.prob_double:.3f} "
            f"3B:{self.prob_triple:.3f} "
            f"HR:{self.prob_hr:.3f} "
            f"BB:{self.prob_walk:.3f} "
            f"K:{self.prob_strikeout:.3f} "
            f"Out:{self.prob_out:.3f}"
        )