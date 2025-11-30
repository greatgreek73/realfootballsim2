import pytest

from matches.engines.markov_runtime import (
    COEFF_CONFIG,
    compute_coeff_pack,
    _ratio_to_coeff,
    _adjust_advancing_transitions,
)


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


def test_pass_success_and_press_force_move_coeffs():
    attacker = _player({"passing": 90, "vision": 88, "work_rate": 85, "dribbling": 80, "composure": 82})
    defender = _player({"marking": 60, "positioning": 60, "tackling": 60, "work_rate": 60})
    pack = compute_coeff_pack(attacker, defender)
    assert pack["pass_success"] > 1.0
    assert pack["pass_block"] < 1.0
    # Press force/resist should be complementary
    assert pack["press_force"] > 0.0
    assert pack["press_resist"] > 0.0


def test_header_and_long_shot_coeffs_are_capped():
    attacker = _player({"heading": 99, "strength": 95, "aerial": 90, "balance": 90, "long_range": 95, "accuracy": 95, "finishing": 95})
    defender = _player({"aerial": 60, "positioning": 60, "strength": 60, "marking": 60, "positioning": 60, "handling": 60, "reflexes": 60})
    pack = compute_coeff_pack(attacker, defender)
    assert pack["header_attack"] <= COEFF_CONFIG["header"]["cap_high"]
    assert pack["long_attack"] <= COEFF_CONFIG["long_shot"]["cap_high"]


def test_adjust_advancing_transitions_uses_pass_and_press():
    transitions = [
        {"to": "OPEN_PLAY_FINAL", "possession": "same", "p": 0.5},
        {"to": "OPEN_PLAY_DEF", "possession": "other", "p": 0.5},
    ]
    adjusted = _adjust_advancing_transitions(
        transitions,
        state="OPEN_PLAY_MID",
        possession="home",
        attack_coeffs={"home": 1.0, "away": 1.0},
        defense_coeffs={"home": 1.0, "away": 1.0},
        dynamic_attack=1.0,
        dynamic_defense=1.0,
        pass_coeff=1.2,
        press_coeff=0.8,
    )
    # Should boost same-possession transition relative to turnover
    p_same = next(t for t in adjusted if t["possession"] == "same")["p"]
    p_other = next(t for t in adjusted if t["possession"] != "same")["p"]
    assert p_same > p_other
    assert pytest.approx(p_same + p_other, rel=1e-6) == 1.0
