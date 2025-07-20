import pytest
from matches.match_simulation import (
    clamp, clamp_int, mirror_side,
    make_zone, random_adjacent_zone, zone_side
)

def test_clamp_variants():
    assert clamp(-10, 0, 1) == 0
    assert clamp(2.5, 0, 2) == 2
    assert clamp(0.7, 0, 1) == 0.7
    assert clamp_int(150, 0, 100) == 100

@pytest.mark.parametrize("side", ["L", "R"])
def test_mirror_side_idempotent(side):
    assert mirror_side(mirror_side(side)) == side

def test_make_zone():
    assert make_zone("MID", "R") == "MID-R"

def test_adjacent_zone_stays_in_grid():
    base = "DEF-C"
    for _ in range(50):
        z = random_adjacent_zone(base)
        assert zone_side(z) in {"L", "C", "R"}
