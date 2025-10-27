import pytest

from transfers.models import TransferListing


pytestmark = pytest.mark.django_db


def test_api_create_listing_accepts_player_id(client, user_with_club, player_factory):
    user, club = user_with_club(username="api-seller", money=500000)
    player = player_factory(club, idx=501)

    client.force_login(user)

    payload = {
        "player_id": player.id,
        "asking_price": 123_000,
        "duration": 30,
        "description": "Available immediately",
    }

    response = client.post(
        "/api/transfers/listings/",
        data=payload,
        content_type="application/json",
    )

    assert response.status_code == 201, response.content
    data = response.json()
    assert data["listing"]["player"]["id"] == player.id
    assert TransferListing.objects.filter(player=player, club=club, status="active").exists()
