"""Fantasy Premier League (FPL) utilities module.

Provides functions for analyzing FPL player data, calculating team value,
and generating transfer recommendations.
"""

import urllib.request
import json


FPL_BASE_URL = "https://fantasy.premierleague.com/api"


def fetch_bootstrap_data():
    """Fetch the FPL bootstrap-static data (players, teams, events).

    Returns:
        dict: Parsed JSON data from the FPL bootstrap-static endpoint.

    Raises:
        RuntimeError: If the data cannot be fetched.
    """
    url = f"{FPL_BASE_URL}/bootstrap-static/"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch FPL data: {exc}") from exc


def get_top_players_by_points(players, n=10):
    """Return the top N players sorted by total FPL points.

    Args:
        players (list[dict]): List of player dicts as returned by the FPL API.
            Each dict must contain at least ``"web_name"`` and
            ``"total_points"`` keys.
        n (int): Number of top players to return. Defaults to 10.

    Returns:
        list[dict]: Players sorted descending by ``total_points``, at most
            ``n`` entries.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    sorted_players = sorted(players, key=lambda p: p.get("total_points", 0), reverse=True)
    return sorted_players[:n]


def calculate_team_value(players):
    """Calculate the total value (in £M) of a list of players.

    The FPL API stores player values as integers in tenths of a million
    (e.g., 65 means £6.5M).  This function converts and sums them.

    Args:
        players (list[dict]): List of player dicts.  Each dict must contain a
            ``"now_cost"`` key with the integer cost value.

    Returns:
        float: Total team value in millions of pounds.
    """
    return sum(p.get("now_cost", 0) for p in players) / 10.0


def get_players_by_position(players, position_id):
    """Filter players by their element type (position).

    FPL position IDs: 1=GKP, 2=DEF, 3=MID, 4=FWD.

    Args:
        players (list[dict]): List of player dicts.
        position_id (int): The ``element_type`` value to filter on.

    Returns:
        list[dict]: Players with the matching ``element_type``.
    """
    return [p for p in players if p.get("element_type") == position_id]


def get_best_value_players(players, n=5):
    """Return the top N players by points-per-million value.

    Players with a ``now_cost`` of 0 are excluded to avoid division by zero.

    Args:
        players (list[dict]): List of player dicts containing ``"total_points"``
            and ``"now_cost"`` keys.
        n (int): Number of players to return. Defaults to 5.

    Returns:
        list[dict]: Players sorted descending by points-per-million, at most
            ``n`` entries.  Each dict is augmented with a
            ``"points_per_million"`` key.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    valued = []
    for p in players:
        cost = p.get("now_cost", 0)
        if cost > 0:
            entry = dict(p)
            entry["points_per_million"] = p.get("total_points", 0) / (cost / 10.0)
            valued.append(entry)
    return sorted(valued, key=lambda p: p["points_per_million"], reverse=True)[:n]


def recommend_transfers(current_squad, all_players, budget, n=3):
    """Suggest transfer targets that improve points-per-million within budget.

    For each player in ``current_squad`` the function finds a replacement
    from ``all_players`` (same position, higher points, affordable within the
    remaining budget) sorted by points gain.

    Args:
        current_squad (list[dict]): Current 15-player squad.  Each dict must
            contain ``"id"``, ``"element_type"``, ``"total_points"``, and
            ``"now_cost"``.
        all_players (list[dict]): Full pool of available players.
        budget (float): Available transfer budget in £M.
        n (int): Maximum number of recommendations to return. Defaults to 3.

    Returns:
        list[dict]: Up to ``n`` recommendation dicts, each containing:
            ``"sell"`` (player to sell), ``"buy"`` (player to buy),
            ``"points_gain"``, and ``"cost_diff"`` keys.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    squad_ids = {p["id"] for p in current_squad}
    recommendations = []

    for player in current_squad:
        sell_cost = player.get("now_cost", 0) / 10.0
        position = player.get("element_type")
        current_pts = player.get("total_points", 0)

        for candidate in all_players:
            if candidate["id"] in squad_ids:
                continue
            if candidate.get("element_type") != position:
                continue
            buy_cost = candidate.get("now_cost", 0) / 10.0
            cost_diff = buy_cost - sell_cost
            if cost_diff > budget:
                continue
            pts_gain = candidate.get("total_points", 0) - current_pts
            if pts_gain > 0:
                recommendations.append({
                    "sell": player,
                    "buy": candidate,
                    "points_gain": pts_gain,
                    "cost_diff": cost_diff,
                })

    recommendations.sort(key=lambda r: r["points_gain"], reverse=True)
    return recommendations[:n]
