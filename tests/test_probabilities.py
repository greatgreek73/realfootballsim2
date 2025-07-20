# tests/test_probabilities.py
from types import SimpleNamespace
from matches.match_simulation import (
    shot_success_probability,
    long_shot_success_probability,
)

def make_stub(**stats):
    base = dict(
        # атакующие скиллы
        finishing=60, long_range=55, accuracy=50,
        # кипер / поле
        reflexes=50, handling=50, positioning=50,
        # общие
        stamina=100, morale=50,
    )
    base.update(stats)
    return SimpleNamespace(**base)

def test_shot_probability_range():
    striker = make_stub(finishing=80)
    keeper  = make_stub()              # дефолтные статы
    p = shot_success_probability(striker, keeper)
    assert 0.0 <= p <= 1.0

def test_long_vs_close_shot():
    striker = make_stub(finishing=70, long_range=70)
    keeper  = make_stub()
    long  = long_shot_success_probability(striker, keeper)
    close = shot_success_probability(striker, keeper)
    assert close > long      # ближний удар опаснее
