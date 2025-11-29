import pytest

from matches.engines.markov_runtime import COEFF_CONFIG, compute_coeff_pack, _ratio_to_coeff


def _player(stats):
    return {"stats": stats}


def test_progress_mid_scales_with_attacker_strength():
    attacker = _player({"passing": 90, "vision": 88, "dribbling": 86, "work_rate": 85})
    defender = _player({"tackling": 60, "marking": 60, "positioning": 60, "strength": 60})
    pack = compute_coeff_pack(attacker, defender)
    assert pack["progress_mid_attack"] > 1.0
    assert pack["progress_mid_defense"] < 1.0
    assert pack["progress_mid_attack"] <= COEFF_CONFIG["progress_mid"]["cap_high"]


def test_shot_vs_keeper_scales_both_sides():
    weak_shooter = _player({"finishing": 60, "long_range": 60, "accuracy": 60})
    strong_keeper = _player({"reflexes": 90, "handling": 90, "positioning": 90, "aerial": 90, "command": 90})
    pack = compute_coeff_pack(weak_shooter, strong_keeper)
    assert pack["shot_attack"] < 1.0
    assert pack["gk_save"] > 1.0
    assert pack["gk_save"] <= COEFF_CONFIG["shot"]["cap_high"]


def test_ratio_to_coeff_is_clamped():
    att, deff = _ratio_to_coeff(200.0, 10.0, cap_low=0.5, cap_high=1.2)
    assert att == pytest.approx(1.2)
    assert deff == pytest.approx(0.8)
