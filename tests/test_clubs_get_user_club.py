import pytest
from django.contrib.auth import get_user_model

from clubs.api_views import _get_user_club
from clubs.models import Club


@pytest.mark.django_db
def test_get_user_club_returns_owned_club():
    user = get_user_model().objects.create_user(
        username="owner1", email="owner1@example.com", password="pass123"
    )
    other_user = get_user_model().objects.create_user(
        username="other", email="other@example.com", password="pass123"
    )

    Club.objects.create(name="Neutral FC", country="GB", is_bot=True)
    owned_club = Club.objects.create(name="Owner FC", country="ES", owner=user)
    Club.objects.create(name="Other Owner FC", country="IT", owner=other_user)

    result = _get_user_club(user)

    assert result == owned_club


@pytest.mark.django_db
def test_get_user_club_returns_none_when_user_has_no_club():
    user = get_user_model().objects.create_user(
        username="lonely", email="lonely@example.com", password="pass123"
    )

    Club.objects.create(name="First FC", country="GB", is_bot=True)
    Club.objects.create(name="Second FC", country="FR", is_bot=True)

    result = _get_user_club(user)

    assert result is None
