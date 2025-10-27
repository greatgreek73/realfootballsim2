from datetime import timedelta

import pytest
from django.utils import timezone

from transfers.models import TransferHistory, TransferListing, TransferOffer


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


def test_api_history_my_returns_only_user_club(client, user_with_club, player_factory):
    user, club = user_with_club(username="history-user")
    other_user, other_club = user_with_club(username="history-other", club_name="Other FC")

    player_out = player_factory(club, idx=701)
    player_in = player_factory(other_club, idx=702)
    outsider = player_factory(other_club, idx=703)

    TransferHistory.objects.create(
        player=player_out,
        from_club=club,
        to_club=other_club,
        transfer_fee=100,
    )
    TransferHistory.objects.create(
        player=player_in,
        from_club=other_club,
        to_club=club,
        transfer_fee=150,
    )
    TransferHistory.objects.create(
        player=outsider,
        from_club=other_club,
        to_club=other_club,
        transfer_fee=999,
    )

    client.force_login(user)
    response = client.get("/api/transfers/history/my/")
    assert response.status_code == 200
    data = response.json()
    returned_ids = {item["player"]["id"] for item in data["results"]}
    assert player_out.id in returned_ids
    assert player_in.id in returned_ids
    assert outsider.id not in returned_ids


def test_api_club_dashboard_returns_expected_structure(client, user_with_club, player_factory):
    user, club = user_with_club(username="dashboard-user", money=200000)
    other_user, other_club = user_with_club(username="dashboard-other", club_name="Opponent FC", money=300000)

    listed_player = player_factory(club, idx=801, position="Center Back")
    extra_player = player_factory(club, idx=802, position="Striker")
    listing = TransferListing.objects.create(
        player=listed_player,
        club=club,
        asking_price=500,
        status="active",
        listed_at=timezone.now(),
        duration=30,
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    offer = TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=other_club,
        bid_amount=550,
        status="pending",
    )
    TransferHistory.objects.create(
        player=listed_player,
        from_club=club,
        to_club=other_club,
        transfer_fee=400,
    )

    client.force_login(user)
    response = client.get("/api/transfers/club/")
    assert response.status_code == 200
    data = response.json()

    assert data["club"]["id"] == club.id
    assert any(entry["player"]["id"] == listed_player.id for entry in data["active_listings"])
    assert any(player["id"] == extra_player.id for player in data["players_not_listed"])
    assert any(item["id"] == offer.id for item in data["pending_offers"])
    assert data["history"]
