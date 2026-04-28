from dataclasses import dataclass
import pandas as pd


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

    # Calculated probabilities (set after init)
    prob_single: float = 0.0
    prob_double: float = 0.0
    prob_triple: float = 0.0
    prob_hr: float = 0.0
    prob_walk: float = 0.0
    prob_strikeout: float = 0.0
    prob_out: float = 0.0

    def __post_init__(self):
        """Calculate at-bat probabilities from raw stats."""
        if self.pa == 0:
            return

        self.prob_single = self.singles / self.pa
        self.prob_double = self.doubles / self.pa
        self.prob_triple = self.triples / self.pa
        self.prob_hr = self.home_runs / self.pa
        self.prob_walk = self.walks / self.pa
        self.prob_strikeout = self.strikeouts / self.pa

        # Everything else is an out
        self.prob_out = max(0.0, 1.0 - (
            self.prob_single +
            self.prob_double +
            self.prob_triple +
            self.prob_hr +
            self.prob_walk +
            self.prob_strikeout
        ))

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


def build_roster(df: pd.DataFrame, min_pa: int = 50) -> list[Player]:
    """Convert a stats dataframe into a list of Player objects."""
    players = []

    for _, row in df.iterrows():
        if row["PA"] < min_pa:
            continue  # Skip players with too few plate appearances

        player = Player(
            name=row["Name"],
            games=int(row["G"]),
            pa=int(row["PA"]),
            singles=int(row["H"] - row["2B"] - row["3B"] - row["HR"]),
            doubles=int(row["2B"]),
            triples=int(row["3B"]),
            home_runs=int(row["HR"]),
            walks=int(row["BB"]),
            strikeouts=int(row["SO"])
        )
        players.append(player)

    return players


if __name__ == "__main__":
    from src.data_fetcher import fetch_mariners_batting

    df = fetch_mariners_batting(2024)
    roster = build_roster(df)

    print(f"\n2024 Mariners Roster ({len(roster)} players)\n")
    for player in roster:
        print(player)