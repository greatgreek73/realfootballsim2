import json
from typing import Any, Dict, Iterable, Optional

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from clubs.models import Club
from players.models import Player
from tournaments.models import Season
from transfers.forms import TransferListingForm, TransferOfferForm
from transfers.models import TransferHistory, TransferListing, TransferOffer


def _json_auth_required(request: HttpRequest) -> Optional[JsonResponse]:
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)
    return None


def _get_user_club(user) -> Optional[Club]:
    """Attempt to resolve the club linked to the given user."""
    if not user or not user.is_authenticated:
        return None
    for field in ("owner", "manager", "user"):
        try:
            club = Club.objects.filter(**{field: user}).order_by("id").first()
            if club:
                return club
        except Exception:
            continue
    return None


def _serialize_club(club: Optional[Club]) -> Optional[Dict[str, Any]]:
    if not club:
        return None
    return {
        "id": club.id,
        "name": club.name,
        "crest_url": getattr(club, "crest_url", None),
        "owner_id": getattr(club, "owner_id", None),
    }


def _serialize_player(player: Player) -> Dict[str, Any]:
    return {
        "id": player.id,
        "full_name": player.full_name,
        "position": player.position,
        "age": player.age,
        "overall_rating": player.overall_rating,
        "nationality": getattr(player.nationality, "code", None) or getattr(player.nationality, "name", None),
        "club_id": player.club_id,
    }


def _get_highest_offer(listing: TransferListing) -> Optional[TransferOffer]:
    return listing.offers.filter(status="pending").order_by("-bid_amount", "-created_at").first()


def _listing_summary(listing: TransferListing, user_club: Optional[Club]) -> Dict[str, Any]:
    highest = _get_highest_offer(listing)
    time_remaining = None
    if listing.status == "active":
        try:
            time_remaining = listing.time_remaining()
        except Exception:
            time_remaining = None
    summary = {
        "id": listing.id,
        "status": listing.status,
        "asking_price": listing.asking_price,
        "highest_bid": highest.bid_amount if highest else None,
        "listed_at": listing.listed_at.isoformat(),
        "expires_at": listing.expires_at.isoformat() if listing.expires_at else None,
        "time_remaining": time_remaining,
        "player": _serialize_player(listing.player),
        "club": _serialize_club(listing.club),
        "summary": {
            "offers_count": listing.offers.exclude(status="cancelled").count(),
            "is_owner": bool(user_club and listing.club_id == user_club.id),
            "can_bid": bool(
                user_club
                and listing.status == "active"
                and listing.club_id != user_club.id
            ),
        },
    }
    return summary


def _serialize_offer(
    offer: TransferOffer,
    listing: TransferListing,
    user_club: Optional[Club],
) -> Dict[str, Any]:
    is_owner = user_club and listing.club_id == user_club.id
    is_own_offer = user_club and offer.bidding_club_id == user_club.id
    highest = _get_highest_offer(listing)
    return {
        "id": offer.id,
        "bid_amount": offer.bid_amount,
        "status": offer.status,
        "created_at": offer.created_at.isoformat(),
        "message": offer.message,
        "bidding_club": _serialize_club(offer.bidding_club),
        "is_own_offer": bool(is_own_offer),
        "is_highest": bool(highest and highest.id == offer.id),
        "can_cancel": bool(is_own_offer and offer.status == "pending"),
        "can_accept": bool(is_owner and listing.status == "active" and offer.status == "pending"),
        "can_reject": bool(is_owner and listing.status == "active" and offer.status == "pending"),
    }


def _serialize_listing_detail(listing: TransferListing, user_club: Optional[Club]) -> Dict[str, Any]:
    is_owner = user_club and listing.club_id == user_club.id
    summary = _listing_summary(listing, user_club)

    if is_owner:
        offers_qs: Iterable[TransferOffer] = listing.offers.all().order_by("-created_at")
    elif user_club:
        offers_qs = listing.offers.filter(bidding_club=user_club).order_by("-created_at")
    else:
        offers_qs = []

    offers = [_serialize_offer(offer, listing, user_club) for offer in offers_qs]

    return {
        "listing": summary,
        "offers": offers,
        "permissions": {
            "is_owner": bool(is_owner),
            "can_bid": summary["summary"]["can_bid"],
            "can_cancel_listing": bool(is_owner and listing.status == "active"),
            "can_accept_offers": bool(is_owner and listing.status == "active"),
        },
    }


def _serialize_history(entry: TransferHistory) -> Dict[str, Any]:
    return {
        "id": entry.id,
        "player": _serialize_player(entry.player),
        "from_club": _serialize_club(entry.from_club),
        "to_club": _serialize_club(entry.to_club),
        "transfer_fee": entry.transfer_fee,
        "transfer_date": entry.transfer_date.isoformat(),
        "season": {
            "id": entry.season.id,
            "name": getattr(entry.season, "name", str(entry.season)),
        } if entry.season else None,
    }


def _serialize_player_light(player: Player) -> Dict[str, Any]:
    return {
        "id": player.id,
        "full_name": player.full_name,
        "position": player.position,
        "age": player.age,
        "base_value": player.get_purchase_cost(),
    }


def _build_history_response(request: HttpRequest, history_qs: QuerySet) -> JsonResponse:
    try:
        season_id = int(request.GET.get("season_id", "") or 0)
    except ValueError:
        season_id = None
    if season_id:
        history_qs = history_qs.filter(season_id=season_id)

    try:
        club_id = int(request.GET.get("club_id", "") or 0)
    except ValueError:
        club_id = None
    if club_id:
        history_qs = history_qs.filter(Q(from_club_id=club_id) | Q(to_club_id=club_id))

    try:
        player_id = int(request.GET.get("player_id", "") or 0)
    except ValueError:
        player_id = None
    if player_id:
        history_qs = history_qs.filter(player_id=player_id)

    ordering = request.GET.get("ordering") or "-transfer_date"
    allowed = {"-transfer_date", "transfer_date"}
    if ordering not in allowed:
        ordering = "-transfer_date"
    history_qs = history_qs.order_by(ordering, "id")

    try:
        page = max(int(request.GET.get("page", "1") or 1), 1)
    except ValueError:
        page = 1

    try:
        page_size = int(request.GET.get("page_size", "20") or 20)
    except ValueError:
        page_size = 20
    page_size = max(1, min(page_size, 100))

    page_obj, paginator = _paginate_queryset(history_qs, page, page_size)
    results = [_serialize_history(entry) for entry in page_obj]

    return JsonResponse(
        {
            "results": results,
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
        }
    )


def _parse_json_body(request: HttpRequest) -> Dict[str, Any]:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def _paginate_queryset(qs: QuerySet, page: int, page_size: int):
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    return page_obj, paginator


@require_http_methods(["GET", "POST"])
def transfer_listings_list(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        return transfer_listing_create(request)

    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    listings = TransferListing.objects.select_related("player", "club").all()

    status = request.GET.get("status") or "active"
    if status in {"active", "completed", "cancelled", "expired"}:
        listings = listings.filter(status=status)

    position = request.GET.get("position")
    if position:
        listings = listings.filter(player__position=position)

    try:
        min_age = int(request.GET.get("min_age", "") or 0)
    except ValueError:
        min_age = None
    if min_age:
        listings = listings.filter(player__age__gte=min_age)

    try:
        max_age = int(request.GET.get("max_age", "") or 0)
    except ValueError:
        max_age = None
    if max_age:
        listings = listings.filter(player__age__lte=max_age)

    try:
        min_price = int(request.GET.get("min_price", "") or 0)
    except ValueError:
        min_price = None
    if min_price is not None and min_price > 0:
        listings = listings.filter(asking_price__gte=min_price)

    try:
        max_price = int(request.GET.get("max_price", "") or 0)
    except ValueError:
        max_price = None
    if max_price is not None and max_price > 0:
        listings = listings.filter(asking_price__lte=max_price)

    try:
        club_id = int(request.GET.get("club_id", "") or 0)
    except ValueError:
        club_id = None
    if club_id:
        listings = listings.filter(club_id=club_id)

    ordering = request.GET.get("ordering") or "expires_at"
    allowed_ordering = {"expires_at", "-expires_at", "asking_price", "-asking_price"}
    if ordering not in allowed_ordering:
        ordering = "expires_at"
    listings = listings.order_by(ordering)

    try:
        page = max(int(request.GET.get("page", "1") or 1), 1)
    except ValueError:
        page = 1

    try:
        page_size = int(request.GET.get("page_size", "30") or 30)
    except ValueError:
        page_size = 30
    page_size = max(1, min(page_size, 100))

    page_obj, paginator = _paginate_queryset(listings, page, page_size)
    user_club = _get_user_club(request.user)

    results = [_listing_summary(listing, user_club) for listing in page_obj]

    return JsonResponse(
        {
            "results": results,
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
        }
    )


@require_GET
def transfer_listing_detail(request: HttpRequest, listing_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    try:
        listing = (
            TransferListing.objects.select_related("player", "club")
            .prefetch_related("offers__bidding_club")
            .get(id=listing_id)
        )
    except TransferListing.DoesNotExist:
        return JsonResponse({"detail": "Listing not found"}, status=404)

    user_club = _get_user_club(request.user)
    payload = _serialize_listing_detail(listing, user_club)
    return JsonResponse(payload)


@require_POST
def transfer_listing_create(request: HttpRequest) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    if not user_club:
        return JsonResponse({"detail": "You must have a club to list players."}, status=403)

    payload = _parse_json_body(request)
    if "player_id" in payload and "player" not in payload:
        payload["player"] = payload.pop("player_id")
    form = TransferListingForm(payload, club=user_club)
    if not form.is_valid():
        return JsonResponse({"detail": "Invalid data", "errors": form.errors}, status=422)

    listing: TransferListing = form.save(commit=False)
    listing.club = user_club
    if not listing.listed_at:
        listing.listed_at = timezone.now()
    listing.save()

    listing.refresh_from_db()
    response = _serialize_listing_detail(listing, user_club)
    return JsonResponse(response, status=201)


@require_POST
def transfer_listing_cancel(request: HttpRequest, listing_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    try:
        listing = TransferListing.objects.select_related("player", "club").get(id=listing_id)
    except TransferListing.DoesNotExist:
        return JsonResponse({"detail": "Listing not found"}, status=404)

    if not user_club or listing.club_id != user_club.id:
        return JsonResponse({"detail": "You do not have permission to cancel this listing."}, status=403)

    if listing.status != "active":
        return JsonResponse({"detail": "Listing cannot be cancelled."}, status=422)

    listing.cancel()
    listing.refresh_from_db()
    return JsonResponse(_serialize_listing_detail(listing, user_club))


@require_POST
def transfer_listing_expire(request: HttpRequest, listing_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    try:
        listing = TransferListing.objects.select_related("player", "club").prefetch_related("offers").get(id=listing_id)
    except TransferListing.DoesNotExist:
        return JsonResponse({"detail": "Listing not found"}, status=404)

    if not user_club or listing.club_id != user_club.id:
        return JsonResponse({"detail": "You do not have permission to modify this listing."}, status=403)

    if listing.status != "active":
        return JsonResponse({"detail": "Listing is not active."}, status=422)

    highest_offer = _get_highest_offer(listing)
    success = False
    message = "Listing updated."

    if highest_offer:
        success = highest_offer.accept()
        message = "Highest offer accepted."
    else:
        success = listing.expire()
        message = "Listing marked as expired."

    if not success:
        return JsonResponse({"detail": "Unable to update listing."}, status=400)

    listing.refresh_from_db()
    return JsonResponse({"message": message, **_serialize_listing_detail(listing, user_club)})


@require_POST
def transfer_offer_create(request: HttpRequest, listing_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    if not user_club:
        return JsonResponse({"detail": "You must have a club to place offers."}, status=403)

    try:
        listing = TransferListing.objects.select_related("player", "club").get(id=listing_id)
    except TransferListing.DoesNotExist:
        return JsonResponse({"detail": "Listing not found"}, status=404)

    if listing.status != "active":
        return JsonResponse({"detail": "Listing is not active."}, status=422)

    if listing.club_id == user_club.id:
        return JsonResponse({"detail": "You cannot bid on your own listing."}, status=422)

    payload = _parse_json_body(request)
    form = TransferOfferForm(payload, transfer_listing=listing, bidding_club=user_club)
    if not form.is_valid():
        return JsonResponse({"detail": "Invalid data", "errors": form.errors}, status=422)

    with transaction.atomic():
        offer: TransferOffer = form.save(commit=False)
        offer.transfer_listing = listing
        offer.bidding_club = user_club
        offer.save()

    return JsonResponse(_serialize_listing_detail(listing, user_club), status=201)


def _get_offer_with_listing(offer_id: int) -> Optional[TransferOffer]:
    try:
        return (
            TransferOffer.objects.select_related("transfer_listing", "transfer_listing__club", "bidding_club")
            .get(id=offer_id)
        )
    except TransferOffer.DoesNotExist:
        return None


@require_POST
def transfer_offer_cancel(request: HttpRequest, offer_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    offer = _get_offer_with_listing(offer_id)
    if not offer:
        return JsonResponse({"detail": "Offer not found"}, status=404)

    listing = offer.transfer_listing

    if not user_club or offer.bidding_club_id != user_club.id:
        return JsonResponse({"detail": "You do not have permission to cancel this offer."}, status=403)

    if offer.status != "pending":
        return JsonResponse({"detail": "Offer cannot be cancelled."}, status=422)

    offer.cancel()
    listing.refresh_from_db()
    return JsonResponse(_serialize_listing_detail(listing, user_club))


@require_POST
def transfer_offer_reject(request: HttpRequest, offer_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    offer = _get_offer_with_listing(offer_id)
    if not offer:
        return JsonResponse({"detail": "Offer not found"}, status=404)

    listing = offer.transfer_listing
    if not user_club or listing.club_id != user_club.id:
        return JsonResponse({"detail": "You do not have permission to reject this offer."}, status=403)

    if offer.status != "pending":
        return JsonResponse({"detail": "Offer cannot be rejected."}, status=422)

    offer.reject()
    listing.refresh_from_db()
    return JsonResponse(_serialize_listing_detail(listing, user_club))


@require_POST
def transfer_offer_accept(request: HttpRequest, offer_id: int) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    offer = _get_offer_with_listing(offer_id)
    if not offer:
        return JsonResponse({"detail": "Offer not found"}, status=404)

    listing = offer.transfer_listing
    if not user_club or listing.club_id != user_club.id:
        return JsonResponse({"detail": "You do not have permission to accept this offer."}, status=403)

    if offer.status != "pending" or listing.status != "active":
        return JsonResponse({"detail": "Offer cannot be accepted."}, status=422)

    success = offer.accept()
    if not success:
        return JsonResponse({"detail": "Unable to accept offer."}, status=422)

    listing.refresh_from_db()
    return JsonResponse(_serialize_listing_detail(listing, user_club))


@require_GET
def transfer_history_list(request: HttpRequest) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    history = TransferHistory.objects.select_related("player", "from_club", "to_club", "season")
    return _build_history_response(request, history)


@require_GET
def transfer_history_my(request: HttpRequest) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    if not user_club:
        return JsonResponse({"detail": "You must have a club to view transfer history."}, status=404)

    history = TransferHistory.objects.select_related("player", "from_club", "to_club", "season").filter(
        Q(from_club=user_club) | Q(to_club=user_club)
    )
    return _build_history_response(request, history)


@require_GET
def transfer_club_dashboard(request: HttpRequest) -> JsonResponse:
    unauth = _json_auth_required(request)
    if unauth:
        return unauth

    user_club = _get_user_club(request.user)
    if not user_club:
        return JsonResponse({"detail": "You must have a club to view transfers."}, status=404)

    active_listings = (
        TransferListing.objects.select_related("player", "club")
        .filter(club=user_club, status="active")
        .order_by("-listed_at")
    )
    listing_summaries = [_listing_summary(listing, user_club) for listing in active_listings]

    players_not_listed = (
        Player.objects.filter(club=user_club)
        .exclude(id__in=active_listings.values_list("player__id", flat=True))
        .order_by("id")
    )
    player_summaries = [_serialize_player_light(player) for player in players_not_listed]

    pending_offers_qs = (
        TransferOffer.objects.select_related("transfer_listing", "transfer_listing__club", "bidding_club")
        .filter(
            transfer_listing__club=user_club,
            transfer_listing__status="active",
            status="pending",
        )
        .order_by("-created_at")
    )
    offers_payload = [_serialize_offer(offer, offer.transfer_listing, user_club) for offer in pending_offers_qs]

    history_qs = TransferHistory.objects.select_related("player", "from_club", "to_club", "season").filter(
        Q(from_club=user_club) | Q(to_club=user_club)
    ).order_by("-transfer_date")[:20]

    payload = {
        "club": _serialize_club(user_club),
        "active_listings": listing_summaries,
        "players_not_listed": player_summaries,
        "pending_offers": offers_payload,
        "history": [_serialize_history(entry) for entry in history_qs],
    }
    return JsonResponse(payload)
