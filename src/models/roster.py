import pandas as pd
from src.models.player import Player


def build_roster(df: pd.DataFrame, min_pa: int = 50) -> list[Player]:
    """Convert a stats dataframe into a list of Player objects."""
    players = []

    for _, row in df.iterrows():
        if row["PA"] < min_pa:
            continue

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


def sort_batting_order(players: list[Player]) -> list[Player]:
    """
    Sort players into a realistic batting order.
    Slots 1-2: High OBP (contact, speed)
    Slots 3-4: Best hitters (high SLG, high AVG)
    Slot 5:    Power bat
    Slots 6-9: Remaining players by OBP
    """
    if not players:
        return players

    def obp_estimate(p: Player) -> float:
        return p.prob_single + p.prob_double + p.prob_triple + p.prob_hr + p.prob_walk

    def slg_estimate(p: Player) -> float:
        return (p.prob_single + 2 * p.prob_double +
                3 * p.prob_triple + 4 * p.prob_hr)

    sorted_by_obp = sorted(players, key=obp_estimate, reverse=True)
    sorted_by_slg = sorted(players, key=slg_estimate, reverse=True)

    used = set()
    order = []

    def pick(pool: list[Player]) -> Player:
        for p in pool:
            if p.name not in used:
                used.add(p.name)
                return p

    # Slots 1-2: high OBP
    order.append(pick(sorted_by_obp))
    order.append(pick(sorted_by_obp))
    # Slots 3-4: best overall (SLG)
    order.append(pick(sorted_by_slg))
    order.append(pick(sorted_by_slg))
    # Slot 5: next best power
    order.append(pick(sorted_by_slg))
    # Slots 6-9: remaining by OBP
    while len(order) < min(9, len(players)):
        order.append(pick(sorted_by_obp))

    return order