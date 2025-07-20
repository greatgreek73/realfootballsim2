from types import SimpleNamespace
import pytest
from matches.match_simulation import (
    clamp, zone_prefix, mirror_side,
    pass_success_probability
)

# ─── 1. zone_prefix ───
def test_zone_prefix():
    assert zone_prefix("MID-L") == "MID"

# ─── 2. pass_success_probability ───
def make_stub(**kwargs):
    # Создаём «пустой» объект с нужными полями
    defaults = dict(
        passing=50, vision=50, positioning=50, heading=50,
        marking=50, tackling=50,
        stamina=100, morale=50,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)

def test_pass_probability_range():
    passer = make_stub(passing=70, vision=70)
    recipient = make_stub(positioning=60, heading=40)
    opponent = make_stub(marking=40, tackling=40)
    p = pass_success_probability(
        passer, recipient, opponent,
        from_zone="MID-C", to_zone="ATT-C"
    )
    assert 0.0 <= p <= 1.0
