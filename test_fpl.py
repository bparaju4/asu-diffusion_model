"""Tests for the Fantasy Premier League (fpl) module."""

import pytest
from fpl import (
    get_top_players_by_points,
    calculate_team_value,
    get_players_by_position,
    get_best_value_players,
    recommend_transfers,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_players():
    """A small list of mock FPL player dicts."""
    return [
        {"id": 1, "web_name": "Salah",    "element_type": 3, "total_points": 200, "now_cost": 130},
        {"id": 2, "web_name": "Haaland",  "element_type": 4, "total_points": 190, "now_cost": 140},
        {"id": 3, "web_name": "Alexander-Arnold", "element_type": 2, "total_points": 150, "now_cost": 85},
        {"id": 4, "web_name": "Raya",     "element_type": 1, "total_points": 120, "now_cost": 50},
        {"id": 5, "web_name": "Saka",     "element_type": 3, "total_points": 170, "now_cost": 100},
        {"id": 6, "web_name": "Watkins",  "element_type": 4, "total_points":  80, "now_cost":  85},
    ]


# ---------------------------------------------------------------------------
# get_top_players_by_points
# ---------------------------------------------------------------------------

def test_top_players_returns_correct_count(sample_players):
    result = get_top_players_by_points(sample_players, n=3)
    assert len(result) == 3


def test_top_players_are_sorted_descending(sample_players):
    result = get_top_players_by_points(sample_players, n=3)
    points = [p["total_points"] for p in result]
    assert points == sorted(points, reverse=True)


def test_top_players_first_is_highest(sample_players):
    result = get_top_players_by_points(sample_players, n=1)
    assert result[0]["web_name"] == "Salah"


def test_top_players_n_larger_than_list(sample_players):
    result = get_top_players_by_points(sample_players, n=100)
    assert len(result) == len(sample_players)


def test_top_players_n_zero_returns_empty(sample_players):
    result = get_top_players_by_points(sample_players, n=0)
    assert result == []


def test_top_players_negative_n_raises(sample_players):
    with pytest.raises(ValueError):
        get_top_players_by_points(sample_players, n=-1)


# ---------------------------------------------------------------------------
# calculate_team_value
# ---------------------------------------------------------------------------

def test_team_value_is_float(sample_players):
    value = calculate_team_value(sample_players)
    assert isinstance(value, float)


def test_team_value_correct(sample_players):
    # Sum of now_cost: 130+140+85+50+100+85 = 590  -> £59.0M
    assert calculate_team_value(sample_players) == pytest.approx(59.0)


def test_team_value_empty_list():
    assert calculate_team_value([]) == pytest.approx(0.0)


def test_team_value_single_player():
    players = [{"now_cost": 65}]
    assert calculate_team_value(players) == pytest.approx(6.5)


# ---------------------------------------------------------------------------
# get_players_by_position
# ---------------------------------------------------------------------------

def test_players_by_position_midfielders(sample_players):
    mids = get_players_by_position(sample_players, position_id=3)
    assert len(mids) == 2
    names = {p["web_name"] for p in mids}
    assert names == {"Salah", "Saka"}


def test_players_by_position_goalkeeper(sample_players):
    gks = get_players_by_position(sample_players, position_id=1)
    assert len(gks) == 1
    assert gks[0]["web_name"] == "Raya"


def test_players_by_position_no_match(sample_players):
    result = get_players_by_position(sample_players, position_id=99)
    assert result == []


# ---------------------------------------------------------------------------
# get_best_value_players
# ---------------------------------------------------------------------------

def test_best_value_players_count(sample_players):
    result = get_best_value_players(sample_players, n=3)
    assert len(result) == 3
    # Verify the first entry has the highest points-per-million in the sample.
    # Raya: 120 / 5.0 = 24.0 ppm is the highest.
    assert result[0]["web_name"] == "Raya"


def test_best_value_players_have_ppm_key(sample_players):
    result = get_best_value_players(sample_players, n=2)
    for p in result:
        assert "points_per_million" in p


def test_best_value_players_sorted_descending(sample_players):
    result = get_best_value_players(sample_players, n=len(sample_players))
    ppms = [p["points_per_million"] for p in result]
    assert ppms == sorted(ppms, reverse=True)


def test_best_value_players_excludes_zero_cost():
    players = [
        {"id": 1, "web_name": "Ghost", "element_type": 3, "total_points": 100, "now_cost": 0},
        {"id": 2, "web_name": "Salah", "element_type": 3, "total_points": 200, "now_cost": 130},
    ]
    result = get_best_value_players(players, n=5)
    names = [p["web_name"] for p in result]
    assert "Ghost" not in names


def test_best_value_negative_n_raises(sample_players):
    with pytest.raises(ValueError):
        get_best_value_players(sample_players, n=-1)


# ---------------------------------------------------------------------------
# recommend_transfers
# ---------------------------------------------------------------------------

@pytest.fixture
def squad_and_pool():
    """Minimal squad and player pool for transfer recommendation tests."""
    squad = [
        {"id": 1, "web_name": "Watkins",  "element_type": 4, "total_points":  80, "now_cost": 85},
        {"id": 2, "web_name": "Raya",     "element_type": 1, "total_points": 120, "now_cost": 50},
    ]
    pool = [
        {"id": 1, "web_name": "Watkins",  "element_type": 4, "total_points":  80, "now_cost": 85},
        {"id": 2, "web_name": "Raya",     "element_type": 1, "total_points": 120, "now_cost": 50},
        {"id": 3, "web_name": "Haaland",  "element_type": 4, "total_points": 190, "now_cost": 140},
        {"id": 4, "web_name": "Firmino",  "element_type": 4, "total_points":  85, "now_cost":  85},
        {"id": 5, "web_name": "Flekken",  "element_type": 1, "total_points":  90, "now_cost":  45},
    ]
    return squad, pool


def test_recommend_transfers_returns_list(squad_and_pool):
    squad, pool = squad_and_pool
    result = recommend_transfers(squad, pool, budget=10.0)
    assert isinstance(result, list)


def test_recommend_transfers_respects_n(squad_and_pool):
    squad, pool = squad_and_pool
    result = recommend_transfers(squad, pool, budget=10.0, n=1)
    assert len(result) <= 1


def test_recommend_transfers_no_negative_points_gain(squad_and_pool):
    squad, pool = squad_and_pool
    result = recommend_transfers(squad, pool, budget=100.0)
    for rec in result:
        assert rec["points_gain"] > 0


def test_recommend_transfers_budget_respected(squad_and_pool):
    squad, pool = squad_and_pool
    # Budget of 0 means only free/cheaper transfers allowed
    result = recommend_transfers(squad, pool, budget=0.0)
    for rec in result:
        assert rec["cost_diff"] <= 0.0


def test_recommend_transfers_negative_n_raises(squad_and_pool):
    squad, pool = squad_and_pool
    with pytest.raises(ValueError):
        recommend_transfers(squad, pool, budget=10.0, n=-1)


def test_recommend_transfers_sorted_by_points_gain(squad_and_pool):
    squad, pool = squad_and_pool
    result = recommend_transfers(squad, pool, budget=100.0, n=10)
    gains = [r["points_gain"] for r in result]
    assert gains == sorted(gains, reverse=True)
