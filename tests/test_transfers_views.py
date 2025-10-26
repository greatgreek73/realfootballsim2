from datetime import timedelta

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from transfers import views as transfer_views
from transfers.forms import TransferListingForm
from transfers.models import TransferHistory, TransferListing, TransferOffer
from tournaments.models import Season


pytestmark = pytest.mark.django_db


def create_listing(player, club, **extra):
    defaults = {
        "asking_price": 200,
        "status": "active",
        "listed_at": timezone.now(),
        "duration": 30,
        "expires_at": timezone.now() + timedelta(minutes=30),
    }
    defaults.update(extra)
    return TransferListing.objects.create(player=player, club=club, **defaults)


def test_transfer_market_lists_active_offers(client, user_with_club, player_factory):
    user, club = user_with_club(username="market-user")
    other_user, other_club = user_with_club(username="market-seller", club_name="Seller FC")
    player = player_factory(other_club, idx=30, position="Striker")
    listing = create_listing(player, other_club)

    client.force_login(user)
    url = reverse("transfers:transfer_market") + "?position=Striker"
    response = client.get(url)
    assert response.status_code == 200
    page = response.context["listings"]
    assert listing in page.object_list
    assert response.context["filters"]["position"] == "Striker"


def test_transfer_listing_detail_for_seller(client, user_with_club, player_factory):
    seller, club = user_with_club(username="seller-detail")
    buyer, buyer_club = user_with_club(username="buyer-detail", club_name="Buyer Detail")
    player = player_factory(club, idx=31)
    listing = create_listing(player, club)
    offer = TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=buyer_club,
        bid_amount=250,
        status="pending",
    )

    client.force_login(seller)
    response = client.get(reverse("transfers:transfer_listing_detail", args=[listing.id]))
    assert response.status_code == 200
    assert offer in list(response.context["all_offers"])


def test_transfer_listing_detail_for_buyer(client, user_with_club, player_factory):
    seller, club = user_with_club(username="seller-detail2", club_name="Seller Detail 2")
    buyer, buyer_club = user_with_club(username="buyer-detail2", club_name="Buyer Detail 2")
    player = player_factory(club, idx=32)
    listing = create_listing(player, club)
    offer = TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=buyer_club,
        bid_amount=260,
        status="pending",
    )

    client.force_login(buyer)
    response = client.get(reverse("transfers:transfer_listing_detail", args=[listing.id]))
    assert response.status_code == 200
    assert offer in list(response.context["user_offers"])
    assert response.context["is_seller"] is False


def test_create_transfer_listing_get_and_post(client, user_with_club, player_factory):
    user, club = user_with_club(username="creator")
    player = player_factory(club, idx=33)
    client.force_login(user)

    response = client.get(reverse("transfers:create_transfer_listing") + f"?player={player.id}")
    assert response.status_code == 200
    form = response.context["form"]
    assert isinstance(form, TransferListingForm)

    post_data = {
        "player": player.id,
        "asking_price": 250,
        "duration": 30,
        "description": "Available immediately",
    }
    response = client.post(reverse("transfers:create_transfer_listing"), post_data)
    assert response.status_code == 302
    assert TransferListing.objects.filter(player=player, club=club).exists()


def test_club_transfers_view_context(client, user_with_club, player_factory):
    user, club = user_with_club(username="club-view")
    player = player_factory(club, idx=34)
    listing = create_listing(player, club)
    TransferOffer.objects.create(
        transfer_listing=listing, bidding_club=club, bid_amount=200, status="pending"
    )
    client.force_login(user)

    response = client.get(reverse("transfers:club_transfers"))
    assert response.status_code == 200
    assert listing in list(response.context["active_listings"])
    assert player not in response.context["players_not_listed"]


def test_cancel_transfer_listing_redirects_with_message(client, user_with_club):
    user, _ = user_with_club(username="cancel-listing-user")
    client.force_login(user)
    response = client.get(reverse("transfers:cancel_transfer_listing", args=[1]))
    assert response.status_code == 302
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert messages


def test_cancel_transfer_offer_redirects(client, user_with_club, player_factory):
    seller, club = user_with_club(username="cancel-offer-seller")
    buyer, buyer_club = user_with_club(username="cancel-offer-buyer", club_name="Cancel Buyer")
    player = player_factory(club, idx=35)
    listing = create_listing(player, club)
    offer = TransferOffer.objects.create(
        transfer_listing=listing, bidding_club=buyer_club, bid_amount=210, status="pending"
    )

    client.force_login(buyer)
    response = client.get(reverse("transfers:cancel_transfer_offer", args=[offer.id]))
    assert response.status_code == 302


def test_accept_transfer_offer_redirects(client, user_with_club):
    user, _ = user_with_club(username="accept-offer-user")
    client.force_login(user)
    response = client.get(reverse("transfers:accept_transfer_offer", args=[1]))
    assert response.status_code == 302


def test_reject_transfer_offer_requires_seller(client, user_with_club, player_factory):
    seller, club = user_with_club(username="reject-seller", club_name="Reject Seller FC")
    buyer, buyer_club = user_with_club(username="reject-buyer", club_name="Reject Buyer FC")
    player = player_factory(club, idx=36)
    listing = create_listing(player, club)
    offer = TransferOffer.objects.create(
        transfer_listing=listing, bidding_club=buyer_club, bid_amount=220, status="pending"
    )

    client.force_login(buyer)
    response = client.get(reverse("transfers:reject_transfer_offer", args=[offer.id]))
    assert response.status_code == 403

    client.force_login(seller)
    response = client.get(reverse("transfers:reject_transfer_offer", args=[offer.id]))
    assert response.status_code == 302
    offer.refresh_from_db()
    assert offer.status == "rejected"


def test_transfer_history_filters(client, user_with_club, player_factory, active_season):
    seller, seller_club = user_with_club(username="history-seller", club_name="History Seller FC")
    buyer, buyer_club = user_with_club(username="history-buyer", club_name="History Buyer FC")
    player = player_factory(seller_club, idx=37)
    listing = create_listing(player, seller_club, status="completed")
    TransferHistory.objects.create(
        player=player,
        from_club=seller_club,
        to_club=buyer_club,
        transfer_fee=300,
        season=active_season,
    )

    transfer_views.Season = Season  # ensure symbol available within view module

    client.force_login(seller)
    url = reverse("transfers:transfer_history") + f"?club={seller_club.id}&season={active_season.id}"
    response = client.get(url)
    assert response.status_code == 200
    transfers = response.context["transfers"]
    assert transfers.count() == 1


def test_expire_transfer_listing_requires_expired_active_listing(client, user_with_club, player_factory):
    seller, club = user_with_club(username="expire-seller")
    buyer, buyer_club = user_with_club(username="expire-buyer", club_name="Expire Buyer")
    player = player_factory(club, idx=38)
    listing = create_listing(player, club, expires_at=timezone.now() + timedelta(minutes=5))

    client.force_login(seller)
    url = reverse("transfers:expire_transfer_listing", args=[listing.id])
    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["success"] is False

    listing.expires_at = timezone.now() - timedelta(seconds=1)
    listing.save(update_fields=["expires_at"])
    offer = TransferOffer.objects.create(
        transfer_listing=listing, bidding_club=buyer_club, bid_amount=250, status="pending"
    )

    response = client.post(url)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_listing_info_returns_expected_payload(client, user_with_club, player_factory):
    seller, club = user_with_club(username="info-seller")
    player = player_factory(club, idx=39)
    listing = create_listing(player, club, expires_at=timezone.now() + timedelta(minutes=10))
    TransferOffer.objects.create(
        transfer_listing=listing, bidding_club=club, bid_amount=260, status="pending"
    )

    response = client.get(reverse("transfers:get_listing_info", args=[listing.id]))
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["highest_bid"] >= listing.asking_price

    listing.status = "expired"
    listing.save(update_fields=["status"])
    response = client.get(reverse("transfers:get_listing_info", args=[listing.id]))
    assert response.status_code == 200
    assert response.json()["success"] is False
