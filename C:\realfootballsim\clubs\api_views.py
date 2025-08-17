# clubs/api_views.py
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from clubs.models import Club
from players.models import Player

def _get_user_club(user):
    """Определяем клуб текущего пользователя (подстройка под разные поля связей)."""
    for field in ("owner", "manager", "user"):
        try:
            qs = Club.objects.filter(**{field: user})
            club = qs.first()
            if club:
                return club
        except Exception:
            pass
    return Club.objects.first()

@login_required
def my_club(request):
    club = _get_user_club(request.user)
    if not club:
        return JsonResponse({"detail": "no_club"}, status=404)
    return JsonResponse({"id": club.id})

@login_required
def club_summary(request, club_id: int):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        raise Http404("Club not found")

    name = getattr(club, "name", f"Club #{club.id}")
    country = getattr(club, "country", "") or ""
    league = getattr(club, "league", "") or ""
    status = "Owned by " + request.user.get_username()
    tokens = getattr(request.user, "tokens", 0) or 0
    money = getattr(request.user, "money", 0) or 0

    return JsonResponse({
        "id": club.id,
        "name": name,
        "country": country,
        "league": league,
        "status": status,
        "tokens": tokens,
        "money": money,
    })

@login_required
def club_players(request, club_id: int):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        raise Http404("Club not found")

    rows = []
    for p in Player.objects.filter(club=club).order_by("id"):
        rows.append({
            "id": p.id,
            "name": getattr(p, "name", str(p)),
            "position": getattr(p, "position", "") or "",
            "cls": (
                getattr(p, "player_class", None)
                or getattr(p, "classification", None)
                or getattr(p, "player_class_id", None)
                or ""
            ),
        })
    return JsonResponse({"count": len(rows), "results": rows})