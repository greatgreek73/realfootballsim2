import os
import random

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realfootballsim.settings")
django.setup()

from matches.match_simulation import (
    ZONE_GRID,
    clamp,
    clamp_int,
    forward_dribble_zone,
    make_zone,
    mirror_side,
    mirrored_zone,
    next_zone,
    random_adjacent_zone,
    zone_conditions,
    zone_prefix,
    zone_side,
)


@pytest.mark.parametrize(
    "value,min_val,max_val,expected",
    [
        (-1.0, 0.0, 1.0, 0.0),
        (0.5, 0.0, 1.0, 0.5),
        (1.5, 0.0, 1.0, 1.0),
        (10.0, -5.0, 5.0, 5.0),
        (-10.0, -5.0, 5.0, -5.0),
    ],
)
def test_clamp(value, min_val, max_val, expected):
    assert clamp(value, min_val, max_val) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value,min_val,max_val,expected",
    [
        (-150, -100, 100, -100),
        (0, -100, 100, 0),
        (75, -50, 50, 50),
        (25, 0, 20, 20),
        (-5, 0, 20, 0),
    ],
)
def test_clamp_int(value, min_val, max_val, expected):
    assert clamp_int(value, min_val, max_val) == expected


@pytest.mark.parametrize(
    "zone,prefix,side",
    [
        ("GK", "GK", "C"),
        ("DEF-L", "DEF", "L"),
        ("DM-C", "DM", "C"),
        ("AM-R", "AM", "R"),
        ("FWD", "FWD", "C"),
    ],
)
def test_zone_prefix_and_side(zone, prefix, side):
    assert zone_prefix(zone) == prefix
    assert zone_side(zone) == side


@pytest.mark.parametrize(
    "side,expected",
    [("L", "R"), ("R", "L"), ("C", "C"), ("UNKNOWN", "C")],
)
def test_mirror_side(side, expected):
    assert mirror_side(side) == expected


def test_make_zone_handles_goalkeeper():
    assert make_zone("GK", "L") == "GK"
    assert make_zone("DEF", "R") == "DEF-R"


def test_random_adjacent_zone_returns_valid(monkeypatch):
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    zone = "MID-C"
    candidate = random_adjacent_zone(zone)
    assert candidate in ZONE_GRID
    assert candidate != zone


def test_random_adjacent_zone_falls_back_when_no_adjacent(monkeypatch):
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    zone = "UNKNOWN"
    result = random_adjacent_zone(zone)
    assert result == zone or result in ZONE_GRID


def test_forward_dribble_zone_stays_in_column(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.5)
    zone = "DM-L"
    assert forward_dribble_zone(zone) == "MID-L"


def test_forward_dribble_zone_allows_diagonal(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.0)
    monkeypatch.setattr(random, "choice", lambda seq: 1)
    zone = "MID-L"
    result = forward_dribble_zone(zone, diag_prob=0.5)
    assert result in ZONE_GRID
    assert zone_side(result) in {"L", "C"}
    assert zone_prefix(result) == "AM"


@pytest.mark.parametrize(
    "zone,expected",
    [
        ("GK", "DEF-C"),
        ("DEF-L", "DM-L"),
        ("DM-C", "MID-C"),
        ("AM-R", "FWD-R"),
        ("FWD-C", "FWD-C"),
        ("XYZ-L", "XYZ-L"),
    ],
)
def test_next_zone(zone, expected):
    assert next_zone(zone) == expected


@pytest.mark.parametrize(
    "zone,flip,expected",
    [
        ("GK", False, "FWD-C"),
        ("DEF-L", False, "FWD-L"),
        ("DEF-L", True, "FWD-R"),
        ("AM-C", False, "DM-C"),
        ("WING", False, "WING"),
        ("UNKNOWN", False, "UNKNOWN"),
    ],
)
def test_mirrored_zone(zone, flip, expected):
    assert mirrored_zone(zone, flip_side=flip) == expected


def test_zone_conditions_mapping():
    class Dummy:
        def __init__(self, position):
            self.position = position

    gk_condition = zone_conditions("GK")
    assert gk_condition(Dummy("Goalkeeper")) is True
    assert gk_condition(Dummy("Center Back")) is False

    left_def = zone_conditions("DEF-L")
    assert left_def(Dummy("Left Back")) is True
    assert left_def(Dummy("Right Back")) is False

    dm_condition = zone_conditions("DM-C")
    assert dm_condition(Dummy("Central Midfielder")) is True
    assert dm_condition(Dummy("Defensive Midfielder")) is True
    assert dm_condition(Dummy("Attacking Midfielder")) is False

    am_condition = zone_conditions("AM-R")
    assert am_condition(Dummy("Attacking Midfielder")) is True
    assert am_condition(Dummy("Right Midfielder")) is False

    fwd_condition = zone_conditions("FWD-L")
    assert fwd_condition(Dummy("Center Forward")) is True
    assert fwd_condition(Dummy("Goalkeeper")) is False

    any_condition = zone_conditions("ANY")
    assert any_condition(Dummy("Whatever")) is True
