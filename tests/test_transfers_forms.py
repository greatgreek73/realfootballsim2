import pytest
from django import forms

from transfers.forms import TransferListingForm, TransferOfferForm
from transfers.models import TransferListing


pytestmark = pytest.mark.django_db


def test_transfer_listing_form_rejects_price_below_player_value(user_with_club, player_factory):
    user, club = user_with_club()
    player = player_factory(club, idx=1)

    form = TransferListingForm(
        data={
            "player": player.id,
            "asking_price": 10,  # less than minimal 50
            "duration": 30,
            "description": "",
        },
        club=club,
    )

    assert form.is_valid() is False
    assert "asking_price" in form.errors


def test_transfer_listing_form_accepts_valid_payload(user_with_club, player_factory):
    user, club = user_with_club()
    player = player_factory(club, idx=2)

    form = TransferListingForm(
        data={
            "player": player.id,
            "asking_price": 200,
            "duration": 60,
            "description": "Ready to sell",
        },
        club=club,
    )

    assert form.is_valid()
    listing = form.save(commit=False)
    assert listing.player == player
    assert listing.asking_price == 200


def test_transfer_offer_form_requires_listing_and_club():
    form = TransferOfferForm(data={"bid_amount": 100})
    assert form.is_valid() is False
    assert form.non_field_errors()


def test_transfer_offer_form_validates_bid_amount_and_balance(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller", club_name="Seller FC")
    buyer_user, buyer_club = user_with_club(username="buyer", club_name="Buyer FC", money=150)
    player = player_factory(seller_club, idx=3)
    listing = TransferListing.objects.create(player=player, club=seller_club, asking_price=100)

    form = TransferOfferForm(
        data={"bid_amount": 90, "message": "Let's bargain"},
        transfer_listing=listing,
        bidding_club=buyer_club,
    )
    assert form.is_valid() is False
    assert "bid_amount" in form.errors

    form = TransferOfferForm(
        data={"bid_amount": 120, "message": "Final offer"},
        transfer_listing=listing,
        bidding_club=buyer_club,
    )
    assert form.is_valid()


def test_transfer_offer_form_flags_insufficient_funds(user_with_club, player_factory):
    seller_user, seller_club = user_with_club(username="seller2", club_name="Seller 2")
    buyer_user, buyer_club = user_with_club(username="buyer2", club_name="Buyer 2", money=50)
    player = player_factory(seller_club, idx=4)
    listing = TransferListing.objects.create(player=player, club=seller_club, asking_price=80)

    form = TransferOfferForm(
        data={"bid_amount": 80},
        transfer_listing=listing,
        bidding_club=buyer_club,
    )
    assert form.is_valid() is False
    assert "bid_amount" in form.errors
