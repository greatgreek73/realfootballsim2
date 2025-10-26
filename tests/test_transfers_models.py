from datetime import timedelta

import pytest
from django.utils import timezone

from transfers.models import (
    TransferHistory,
    TransferListing,
    TransferOffer,
)


pytestmark = pytest.mark.django_db


def create_listing(player, club, **kwargs):
    defaults = {
        "asking_price": 150,
        "listed_at": timezone.now(),
        "duration": 30,
        "expires_at": None,
    }
    defaults.update(kwargs)
    return TransferListing.objects.create(player=player, club=club, **defaults)


def create_offer(listing, club, amount=200, status="pending"):
    return TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=club,
        bid_amount=amount,
        status=status,
    )


def test_transfer_listing_save_sets_expires_at(user_with_club, player_factory):
    _, club = user_with_club()
    player = player_factory(club, idx=10)
    listed_at = timezone.now()
    listing = TransferListing(
        player=player,
        club=club,
        asking_price=180,
        listed_at=listed_at,
        duration=60,
    )
    listing.save()
    assert listing.expires_at == pytest.approx(listed_at + timedelta(minutes=60))


def test_transfer_listing_is_expired(user_with_club, player_factory):
    _, club = user_with_club(username="seller-exp")
    player = player_factory(club, idx=11)
    past_listing = create_listing(
        player, club, expires_at=timezone.now() - timedelta(minutes=1)
    )
    future_listing = create_listing(
        player_factory(club, idx=12), club, expires_at=timezone.now() + timedelta(minutes=5)
    )

    assert past_listing.is_expired() is True
    assert future_listing.is_expired() is False


def test_transfer_listing_time_remaining_handles_status(user_with_club, player_factory):
    _, club = user_with_club(username="seller-time")
    player = player_factory(club, idx=13)
    listing = create_listing(
        player,
        club,
        expires_at=timezone.now() + timedelta(seconds=120),
    )
    remaining = listing.time_remaining()
    assert 0 < remaining <= 120

    listing.status = "completed"
    assert listing.time_remaining() == 0


def test_transfer_listing_cancel_updates_offers(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-cancel")
    buyer_user, buyer_club = user_with_club(username="buyer-cancel", club_name="Buyer FC")
    player = player_factory(seller_club, idx=14)
    listing = create_listing(player, seller_club)
    pending_offer = create_offer(listing, buyer_club, amount=220, status="pending")
    create_offer(listing, buyer_club, amount=210, status="accepted")

    assert listing.cancel() is True
    listing.refresh_from_db()
    pending_offer.refresh_from_db()
    assert listing.status == "cancelled"
    assert pending_offer.status == "cancelled"


def test_transfer_listing_complete_rejects_pending_offers(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-complete")
    buyer_user, buyer_club = user_with_club(username="buyer-complete", club_name="Buyer CF")
    player = player_factory(seller_club, idx=15)
    listing = create_listing(player, seller_club)
    pending_offer = create_offer(listing, buyer_club, amount=230)

    assert listing.complete() is True
    listing.refresh_from_db()
    pending_offer.refresh_from_db()
    assert listing.status == "completed"
    assert pending_offer.status == "rejected"


def test_transfer_listing_expire_handles_active_and_inactive(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-expire")
    buyer_user, buyer_club = user_with_club(username="buyer-expire", club_name="Buyer Exp")
    player = player_factory(seller_club, idx=16)
    active_listing = create_listing(
        player,
        seller_club,
        expires_at=timezone.now() - timedelta(seconds=1),
        status="active",
    )
    pending_offer = create_offer(active_listing, buyer_club, status="pending")

    assert active_listing.expire() is True
    active_listing.refresh_from_db()
    pending_offer.refresh_from_db()
    assert active_listing.status == "expired"
    assert pending_offer.status == "cancelled"

    inactive_listing = create_listing(
        player_factory(seller_club, idx=17),
        seller_club,
        expires_at=timezone.now() - timedelta(seconds=1),
        status="completed",
    )
    assert inactive_listing.expire() is False


def test_transfer_listing_get_highest_offer_returns_top_pending(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-highest")
    buyer_user1, buyer_club1 = user_with_club(username="buyer-highest1", club_name="Buyer H1")
    buyer_user2, buyer_club2 = user_with_club(username="buyer-highest2", club_name="Buyer H2")
    player = player_factory(seller_club, idx=18)
    listing = create_listing(player, seller_club)
    create_offer(listing, buyer_club1, amount=200, status="pending")
    top_offer = create_offer(listing, buyer_club2, amount=250, status="pending")
    create_offer(listing, buyer_club2, amount=260, status="rejected")

    assert listing.get_highest_offer() == top_offer


def test_transfer_offer_save_triggers_extend_for_new_pending_offer(monkeypatch, user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-extend")
    buyer_user, buyer_club = user_with_club(username="buyer-extend", club_name="Buyer Extend")
    player = player_factory(seller_club, idx=19)
    listing = create_listing(player, seller_club)

    calls = {"count": 0}

    def fake_extend(self):
        calls["count"] += 1
        return True

    monkeypatch.setattr(TransferOffer, "extend_auction_if_needed", fake_extend)

    offer = TransferOffer(transfer_listing=listing, bidding_club=buyer_club, bid_amount=200)
    offer.save()
    assert calls["count"] == 1

    calls["count"] = 0
    offer.save()
    assert calls["count"] == 0


def test_transfer_offer_extend_auction_if_needed_extends_when_under_threshold(monkeypatch, user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-extend2")
    player = player_factory(seller_club, idx=20)
    listing = create_listing(
        player,
        seller_club,
        expires_at=timezone.now() + timedelta(seconds=20),
    )

    now = timezone.now()
    monkeypatch.setattr(TransferListing, "time_remaining", lambda self: 20)
    monkeypatch.setattr("transfers.models.timezone", timezone)
    monkeypatch.setattr("django.utils.timezone.now", lambda: now)

    offer = TransferOffer(transfer_listing=listing, bidding_club=seller_club, bid_amount=100)
    assert offer.extend_auction_if_needed() is True
    listing.refresh_from_db()
    assert listing.expires_at == now + timedelta(seconds=30)

    monkeypatch.setattr(TransferListing, "time_remaining", lambda self: 45)
    assert offer.extend_auction_if_needed() is False


def test_transfer_offer_accept_success_flow(user_with_club, player_factory, active_season):
    seller_user, seller_club = user_with_club(username="seller-accept", money=500)
    buyer_user, buyer_club = user_with_club(username="buyer-accept", club_name="Buyer Accept", money=1000)
    player = player_factory(seller_club, idx=21)
    listing = create_listing(player, seller_club, status="active")
    offer = TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=buyer_club,
        bid_amount=300,
        status="pending",
    )

    assert offer.accept() is True

    buyer_user.refresh_from_db()
    seller_user.refresh_from_db()
    player.refresh_from_db()
    listing.refresh_from_db()

    assert buyer_user.money == 700
    assert seller_user.money == 800
    assert player.club == buyer_club
    assert offer.status == "accepted"
    assert listing.status == "completed"
    assert TransferHistory.objects.filter(
        player=player, from_club=seller_club, to_club=buyer_club, transfer_fee=300
    ).exists()


def test_transfer_offer_accept_fails_when_insufficient_funds(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-accept-fail", money=500)
    buyer_user, buyer_club = user_with_club(username="buyer-accept-fail", club_name="Buyer Fail", money=50)
    player = player_factory(seller_club, idx=22)
    listing = create_listing(player, seller_club, status="active")
    offer = TransferOffer.objects.create(
        transfer_listing=listing,
        bidding_club=buyer_club,
        bid_amount=300,
        status="pending",
    )

    assert offer.accept() is False
    offer.refresh_from_db()
    assert offer.status == "pending"
    assert listing.status == "active"


def test_transfer_offer_reject_and_cancel(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller-reject")
    buyer_user, buyer_club = user_with_club(username="buyer-reject", club_name="Buyer Reject")
    player = player_factory(seller_club, idx=23)
    listing = create_listing(player, seller_club)
    offer = create_offer(listing, buyer_club, amount=210)

    assert offer.reject() is True
    assert offer.status == "rejected"

    assert offer.cancel() is True
    assert offer.status == "cancelled"
