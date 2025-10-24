import pytest

from players.utils import generate_player_stats


@pytest.mark.parametrize(
    "position, player_class, expected_keys",
    [
        (
            "Goalkeeper",
            3,
            {
                "strength",
                "stamina",
                "morale",
                "base_morale",
                "pace",
                "positioning",
                "reflexes",
                "handling",
                "aerial",
                "command",
                "distribution",
                "one_on_one",
                "rebound_control",
                "shot_reading",
                "bloom_type",
                "bloom_start_age",
                "bloom_seasons_left",
            },
        ),
        (
            "Center Forward",
            4,
            {
                "strength",
                "stamina",
                "morale",
                "base_morale",
                "pace",
                "positioning",
                "marking",
                "tackling",
                "work_rate",
                "passing",
                "crossing",
                "dribbling",
                "flair",
                "heading",
                "finishing",
                "long_range",
                "vision",
                "accuracy",
                "bloom_type",
                "bloom_start_age",
                "bloom_seasons_left",
            },
        ),
    ],
)
def test_generate_player_stats_structure(position, player_class, expected_keys):
    stats = generate_player_stats(position, player_class)
    assert set(stats.keys()) == expected_keys
    for key, value in stats.items():
        if key in {"bloom_type", "bloom_start_age", "bloom_seasons_left"}:
            continue
        assert 1 <= value <= 99


def test_generate_player_stats_position_modifiers():
    left_back_samples = [generate_player_stats("Left Back", 3) for _ in range(200)]
    forward_samples = [generate_player_stats("Center Forward", 3) for _ in range(200)]

    lb_pace_avg = sum(s["pace"] for s in left_back_samples) / len(left_back_samples)
    cf_pace_avg = sum(s["pace"] for s in forward_samples) / len(forward_samples)
    assert lb_pace_avg > cf_pace_avg

    lb_crossing_avg = sum(s["crossing"] for s in left_back_samples) / len(left_back_samples)
    cf_crossing_avg = sum(s["crossing"] for s in forward_samples) / len(forward_samples)
    assert lb_crossing_avg > cf_crossing_avg

    cf_finishing_avg = sum(s["finishing"] for s in forward_samples) / len(forward_samples)
    lb_finishing_avg = sum(s["finishing"] for s in left_back_samples) / len(left_back_samples)
    assert cf_finishing_avg > lb_finishing_avg

    cf_heading_avg = sum(s["heading"] for s in forward_samples) / len(forward_samples)
    lb_heading_avg = sum(s["heading"] for s in left_back_samples) / len(left_back_samples)
    assert cf_heading_avg > lb_heading_avg


@pytest.mark.parametrize("player_class", [1, 3, 5])
def test_generate_player_stats_class_modifier(player_class):
    stats = generate_player_stats("Central Midfielder", player_class)
    non_bloom_keys = [k for k in stats if not k.startswith("bloom")]
    average_score = sum(stats[k] for k in non_bloom_keys) / len(non_bloom_keys)

    stats_high_class = generate_player_stats("Central Midfielder", 5)
    average_high = sum(stats_high_class[k] for k in non_bloom_keys) / len(non_bloom_keys)

    if player_class < 5:
        assert average_score >= average_high
