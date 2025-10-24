import collections

import pytest
from django.utils.timezone import now

from clubs.models import Club
from clubs.services import generate_initial_players
from players.models import Player


@pytest.mark.django_db
def test_generate_initial_players_creates_expected_roster():
    club = Club.objects.create(name="Test FC", country="GB", is_bot=True)
    assert Player.objects.filter(club=club).count() == 0

    generate_initial_players(club)

    players = Player.objects.filter(club=club)
    assert players.count() == 16

    # Все имена уникальны
    names = {(p.first_name, p.last_name) for p in players}
    assert len(names) == players.count()

    # Проверяем распределение позиций
    positions = collections.Counter(p.position for p in players)
    assert positions == collections.Counter(
        {
            "Goalkeeper": 2,
            "Right Back": 1,
            "Center Back": 3,
            "Left Back": 1,
            "Left Midfielder": 1,
            "Central Midfielder": 4,
            "Right Midfielder": 1,
            "Center Forward": 3,
        }
    )

    assert all(p.player_class == 4 for p in players)
    assert all(p.age == 17 for p in players)
