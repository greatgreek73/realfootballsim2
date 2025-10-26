from types import SimpleNamespace

import pytest

from matches.match_simulation import (
    dribble_success_probability,
    foul_probability,
    long_shot_success_probability,
    pass_success_probability,
    shot_success_probability,
)
from matches.personality_engine import PersonalityModifier


def _make_player(**overrides):
    defaults = dict(
        position="Central Midfielder",
        passing=50,
        vision=50,
        distribution=50,
        command=50,
        positioning=50,
        heading=40,
        stamina=80,
        morale=60,
        finishing=50,
        long_range=50,
        accuracy=50,
        reflexes=40,
        handling=40,
        dribbling=50,
        pace=50,
        flair=40,
        strength=45,
        marking=45,
        tackling=45,
        work_rate=40,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def disable_personality(settings, monkeypatch):
    settings.USE_PERSONALITY_ENGINE = False
    monkeypatch.setattr(
        PersonalityModifier,
        "get_pass_modifier",
        lambda *args, **kwargs: {"accuracy": 0.0, "preference": 0.0, "risk": 0.0},
    )
    monkeypatch.setattr(
        PersonalityModifier,
        "get_shot_modifier",
        lambda *args, **kwargs: {"accuracy": 0.0},
    )
    monkeypatch.setattr(PersonalityModifier, "get_foul_modifier", lambda *args, **kwargs: 0.0)
    return None


def test_pass_success_probability_improves_with_skill():
    passer_low = _make_player(passing=35, vision=35, stamina=65, morale=45)
    passer_high = _make_player(passing=75, vision=70, stamina=80, morale=70)
    recipient = _make_player(positioning=60, heading=30)
    opponent = _make_player(marking=55, tackling=55)

    low = pass_success_probability(
        passer_low,
        recipient,
        opponent,
        from_zone="MID-C",
        to_zone="AM-C",
        momentum=0,
    )
    high = pass_success_probability(
        passer_high,
        recipient,
        opponent,
        from_zone="MID-C",
        to_zone="AM-C",
        momentum=0,
    )

    assert 0.0 <= low <= 1.0
    assert 0.0 <= high <= 1.0
    assert high > low


def test_pass_success_probability_goalkeeper_to_defence_is_high():
    keeper = _make_player(
        position="Goalkeeper",
        distribution=95,
        command=90,
        stamina=100,
        morale=95,
    )
    recipient = _make_player(positioning=80, heading=60)
    opponent = _make_player(marking=40, tackling=40)

    probability = pass_success_probability(
        keeper,
        recipient,
        opponent,
        from_zone="GK",
        to_zone="DEF-C",
        momentum=10,
    )
    assert probability > 0.95
    assert probability <= 1.0


def test_shot_success_probability_respects_goalkeeper():
    shooter = _make_player(finishing=85, long_range=70, accuracy=80, stamina=85, morale=80)
    weak_goalkeeper = _make_player(
        position="Goalkeeper",
        reflexes=30,
        handling=30,
        positioning=30,
    )
    strong_goalkeeper = _make_player(
        position="Goalkeeper",
        reflexes=90,
        handling=88,
        positioning=90,
    )

    vs_weak = shot_success_probability(
        shooter, weak_goalkeeper, momentum=10, match_minute=70, pressure=0.2
    )
    vs_strong = shot_success_probability(
        shooter, strong_goalkeeper, momentum=10, match_minute=70, pressure=0.2
    )

    assert 0.0 <= vs_weak <= 1.0
    assert 0.0 <= vs_strong <= 1.0
    assert vs_weak > vs_strong


def test_long_shot_probability_lower_than_regular():
    shooter = _make_player(finishing=85, long_range=70, accuracy=80, stamina=85, morale=80)
    keeper = _make_player(
        position="Goalkeeper",
        reflexes=70,
        handling=70,
        positioning=70,
    )

    regular = shot_success_probability(shooter, keeper, momentum=0, match_minute=10, pressure=0.2)
    long_range = long_shot_success_probability(
        shooter, keeper, momentum=0, match_minute=10, pressure=0.2
    )

    assert long_range < regular


def test_foul_probability_increases_in_defensive_zone():
    tackler = _make_player(tackling=70, work_rate=60, stamina=70)
    dribbler = _make_player(dribbling=45)

    middle = foul_probability(tackler, dribbler, zone="MID-C")
    defensive = foul_probability(tackler, dribbler, zone="DEF-C")

    assert 0.0 <= middle <= 1.0
    assert 0.0 <= defensive <= 1.0
    assert defensive > middle


def test_dribble_success_probability_boosted_by_momentum():
    attacker = _make_player(dribbling=80, pace=85, flair=75, stamina=80, morale=70)
    defender = _make_player(tackling=60, marking=55, strength=60)

    neutral = dribble_success_probability(attacker, defender, momentum=0)
    positive = dribble_success_probability(attacker, defender, momentum=40)

    assert 0.0 <= neutral <= 1.0
    assert 0.0 <= positive <= 1.0
    assert positive > neutral


def test_foul_probability_extremes():
    disciplined = foul_probability(
        _make_player(tackling=10, work_rate=10, stamina=100),
        _make_player(dribbling=95),
        zone="MID-C",
    )
    aggressive = foul_probability(
        _make_player(tackling=99, work_rate=90, stamina=20),
        _make_player(dribbling=10),
        zone="DEF-C",
    )
    assert 0.0 <= disciplined <= 0.2
    assert 0.8 <= aggressive <= 1.0


def test_dribble_success_probability_extremes():
    elite = dribble_success_probability(
        _make_player(dribbling=99, pace=95, flair=90, stamina=100, morale=90),
        _make_player(tackling=10, marking=10, strength=10),
        momentum=50,
    )
    shutdown = dribble_success_probability(
        _make_player(dribbling=30, pace=30, flair=25, stamina=40, morale=30),
        _make_player(tackling=99, marking=99, strength=95),
        momentum=-50,
    )
    assert 0.8 <= elite <= 1.0
    assert 0.0 <= shutdown <= 0.2
