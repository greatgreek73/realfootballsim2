# clubs/api_views.py
import json

from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST

from clubs.models import Club
from clubs.forms import ClubForm
from clubs.services import generate_initial_players
from players.models import Player
from tournaments.models import League


def _first(qs):
    """Безопасно берем первый объект, с сортировкой по id при возможности."""
    try:
        return qs.order_by("id").first()
    except Exception:
        return qs.first()


def _get_user_club(user):
    """Детерминированно выбираем клуб текущего пользователя."""
    for field in ("owner", "manager", "user"):
        try:
            club = _first(Club.objects.filter(**{field: user}))
            if club:
                return club
        except Exception:
            pass
    return None


def _as_text(v):
    """Гарантированно приводим к строке (для FK/Enum и т.п.)."""
    if v is None:
        return ""
    try:
        return str(v)
    except Exception:
        return ""


def _as_number(v):
    """Безопасно приводим к числу (int -> иначе float -> иначе 0)."""
    if v is None:
        return 0
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return 0


def _auth_required_json(request):
    """Return 401 JSON instead of HTML redirect for unauthenticated API calls."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)
    return None


@require_POST
@login_required
def create_club(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    form = ClubForm(payload)
    if not form.is_valid():
        return JsonResponse({"detail": "invalid", "errors": form.errors}, status=400)

    with transaction.atomic():
        club = form.save(commit=False)
        club.owner = request.user
        club.is_bot = False
        club._skip_clean = True

        league = League.objects.filter(country=club.country, level=1).first()
        if not league:
            return JsonResponse({"detail": "league_not_found"}, status=400)

        club.league = league
        club.save()
        generate_initial_players(club)

    return JsonResponse({"detail": "ok", "club": {"id": club.id, "name": club.name}})


def my_club(request):
    # Enforce auth with JSON 401 for API consumers
    unauth = _auth_required_json(request)
    if unauth:
        return unauth
    club = _get_user_club(request.user)
    if not club:
        return JsonResponse({"detail": "no_club"}, status=404)
    return JsonResponse({"id": club.id})


def club_summary(request, club_id: int):
    unauth = _auth_required_json(request)
    if unauth:
        return unauth
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        raise Http404("Club not found")

    name = _as_text(getattr(club, "name", None) or club)
    country = _as_text(getattr(club, "country", None))
    league = _as_text(getattr(club, "league", None))   # FK -> str(...)
    status = f"Owned by {request.user.get_username()}"
    tokens = _as_number(getattr(request.user, "tokens", 0))
    money = _as_number(getattr(request.user, "money", 0))

    return JsonResponse({
        "id": club.id,
        "name": name,
        "country": country,
        "league": league,
        "status": status,
        "tokens": tokens,
        "money": money,
    })


def club_players(request, club_id: int):
    unauth = _auth_required_json(request)
    if unauth:
        return unauth
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        raise Http404("Club not found")

    rows = []
    for p in Player.objects.filter(club=club).order_by("id"):
        cls_val = (
            getattr(p, "player_class", None)
            or getattr(p, "classification", None)
            or getattr(p, "player_class_id", None)
        )
        rows.append({
            "id": p.id,
            "name": _as_text(getattr(p, "name", None) or p),
            "position": _as_text(getattr(p, "position", None)),
            "cls": _as_text(cls_val),
        })
    return JsonResponse({"count": len(rows), "results": rows})
