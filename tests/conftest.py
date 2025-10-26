from datetime import date

import pytest
from django.contrib.auth import get_user_model

from clubs.models import Club
from players.models import Player
from tournaments.models import Season


@pytest.fixture
def user_with_club(db):
    """
    Factory fixture returning (user, club) with configurable balance.
    """

    def _create(username="user", club_name="Test FC", money=10000, tokens=0):
        User = get_user_model()
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="StrongPass123!",
        )
        user.money = money
        user.tokens = tokens
        user.save()
        club = Club.objects.create(name=club_name, country="GB", owner=user)
        return user, club

    return _create


@pytest.fixture
def player_factory(db):
    """
    Factory fixture for creating players with unique names.
    """

    def _create(club, first_name="Player", position="Central Midfielder", idx=1, **extra):
        return Player.objects.create(
            first_name=f"{first_name}{idx}",
            last_name=f"Test{idx}",
            age=extra.get("age", 22),
            position=position,
            club=club,
            nationality=extra.get("nationality", "GB"),
            **{k: v for k, v in extra.items() if k not in {"age", "nationality"}},
        )

    return _create


@pytest.fixture
def active_season(db):
    """
    Ensure there is an active season for transfer history records.
    """
    next_number = (Season.objects.order_by("-number").first() or Season(number=0)).number + 1
    return Season.objects.create(
        number=next_number,
        name=f"Season {next_number}",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
        is_active=True,
    )
