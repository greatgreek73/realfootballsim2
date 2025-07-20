"""
conftest.py — фикстуры для тестов симуляции.
Правки: используем Club вместо Team.
"""

import pytest
import factory
from random import randint
from django.apps import apps

# — модели ——————————————————————————————————————————————
Team   = apps.get_model("clubs",   "Club")     # ← заменили Team → Club
Player = apps.get_model("players", "Player")
Match  = apps.get_model("matches", "Match")

# — фабрики —————————————————————————————————————————————
class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Club{n}")

class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player

    team = factory.SubFactory(TeamFactory)
    first_name = factory.Sequence(lambda n: f"Name{n}")
    last_name  = "Test"

    finishing = factory.LazyFunction(lambda: randint(50, 80))
    passing   = factory.LazyFunction(lambda: randint(50, 80))
    tackling  = factory.LazyFunction(lambda: randint(50, 80))

# — фикстура матча с 22 игроками ————————————————
@pytest.fixture
def match_with_lineups(db):
    home = TeamFactory()
    away = TeamFactory()

    PlayerFactory.create_batch(11, team=home)
    PlayerFactory.create_batch(11, team=away)

    match = Match.objects.create(
        home_team=home,
        away_team=away,
        status="NOT_STARTED",
    )
    return match
