from decimal import Decimal

import pytest

from players.models import Player
from players.training import TrainingSettings
from players.training_logic import (
    get_or_create_training_settings,
    calculate_training_points,
    distribute_training_points,
    apply_training_to_player,
    conduct_player_training,
)


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


@pytest.mark.django_db
def test_get_or_create_training_settings_creates_and_reuses_instance():
    player = Player.objects.create(
        first_name="Config",
        last_name="Less",
        age=21,
        position="Central Midfielder",
        club=None,
        nationality="GB",
    )

    assert TrainingSettings.objects.filter(player=player).count() == 0

    settings_first = get_or_create_training_settings(player)

    assert isinstance(settings_first, TrainingSettings)
    assert TrainingSettings.objects.filter(player=player).count() == 1
    assert settings_first.physical_weight == Decimal("16.67")
    assert settings_first.gk_physical_weight == Decimal("33.33")

    settings_second = get_or_create_training_settings(player)
    assert settings_second.pk == settings_first.pk


@pytest.mark.django_db
def test_conduct_player_training_returns_summary(monkeypatch):
    player = Player.objects.create(
        first_name="Trainee",
        last_name="Bloom",
        age=20,
        position="Central Midfielder",
        club=None,
        nationality="GB",
        bloom_start_age=20,
        bloom_seasons_left=0,
    )

    monkeypatch.setattr("players.training_logic.random.choice", lambda seq: seq[0])
    monkeypatch.setattr("players.training_logic.random.random", lambda: 1.0)
    monkeypatch.setattr("players.training_logic.random.randint", lambda a, b: a)

    result = conduct_player_training(player)

    player.refresh_from_db()

    assert player.bloom_seasons_left == 3
    assert TrainingSettings.objects.filter(player=player).count() == 1
    assert result["player_id"] == player.id
    assert result["total_points"] == 6
    assert result["is_in_bloom"] is True
    assert result["bloom_type"] == player.bloom_type
    changes = result["changes"]
    assert "strength" in changes
    total_gain = sum(new - old for old, new in changes.values())
    assert total_gain >= result["total_points"]
    assert result["attributes_improved"] == len(changes)
    assert changes["strength"][1] > changes["strength"][0]
    assert player.strength == changes["strength"][1]


@pytest.mark.django_db
def test_distribute_training_points_field_player():
    player = Player.objects.create(
        first_name="Test",
        last_name="Midfielder",
        age=22,
        position="Central Midfielder",
        club=None,
        nationality="GB",
    )

    TrainingSettings.objects.create(
        player=player,
        physical_weight=Decimal("50"),
        defensive_weight=Decimal("0"),
        attacking_weight=Decimal("0"),
        mental_weight=Decimal("0"),
        technical_weight=Decimal("50"),
        tactical_weight=Decimal("0"),
        gk_physical_weight=Decimal("40"),
        gk_core_skills_weight=Decimal("30"),
        gk_additional_skills_weight=Decimal("30"),
    )

    distribution = distribute_training_points(player, 12)

    assert distribution == {
        "strength": 2,
        "stamina": 2,
        "pace": 2,
        "dribbling": 2,
        "crossing": 2,
        "passing": 2,
    }


@pytest.mark.django_db
def test_apply_training_to_player_increases_attributes(monkeypatch):
    player = Player.objects.create(
        first_name="Grow",
        last_name="Up",
        age=24,
        position="Central Midfielder",
        club=None,
        nationality="GB",
    )
    player.strength = 50
    player.dribbling = 65
    player.save()

    player.get_age_training_modifier = lambda: 1.0

    monkeypatch.setattr("players.training_logic.random.random", lambda: 1.0)

    distribution = {"strength": 2, "dribbling": 1}
    changes = apply_training_to_player(player, distribution)

    player.refresh_from_db()
    assert player.strength == 52
    assert player.dribbling == 66
    assert changes == {"strength": (50, 52), "dribbling": (65, 66)}


@pytest.mark.django_db
def test_apply_training_to_player_may_reduce_for_older_players(monkeypatch):
    player = Player.objects.create(
        first_name="Aging",
        last_name="Star",
        age=33,
        position="Center Back",
        club=None,
        nationality="GB",
    )
    player.pace = 20
    player.save()

    player.get_age_training_modifier = lambda: 0.4

    monkeypatch.setattr("players.training_logic.random.random", lambda: 0.0)
    monkeypatch.setattr("players.training_logic.random.randint", lambda a, b: 2)

    distribution = {"pace": 1}
    changes = apply_training_to_player(player, distribution)

    player.refresh_from_db()
    assert player.pace == 18
    assert changes == {"pace": (20, 18)}
