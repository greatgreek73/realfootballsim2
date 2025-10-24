import pytest

from players.training_logic import calculate_training_points


class DummyPlayer:
    def __init__(self, age_modifier, bloom_bonus, in_bloom):
        self._age_modifier = age_modifier
        self._bloom_bonus = bloom_bonus
        self.is_in_bloom = in_bloom

    def get_age_training_modifier(self):
        return self._age_modifier

    def get_bloom_bonus(self):
        return self._bloom_bonus


@pytest.mark.parametrize(
    "age_mod, bloom_bonus, in_bloom, expected",
    [
        (1.0, 0.5, False, 3),  # базовый случай без bloom
        (1.0, 0.5, True, 4),   # тот же игрок, но в bloom (3 + 3*0.5 = 4.5 -> 4)
        (0.4, 0.2, False, 1),  # возраст снижает очки, минимум ограничен единицей
    ],
)
def test_calculate_training_points(age_mod, bloom_bonus, in_bloom, expected):
    player = DummyPlayer(age_mod, bloom_bonus, in_bloom)
    assert calculate_training_points(player) == expected
