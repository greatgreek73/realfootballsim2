# clubs/api_views.py
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Club  # поля уточним постепенно

@login_required
def my_club(request):
    # Возьмём первый клуб пользователя (при необходимости уточним логику)
    club = Club.objects.filter(Q(owner=request.user) | Q(manager=request.user)).first()
    if not club:
        return JsonResponse({"detail": "no_club"}, status=404)
    return JsonResponse({"id": club.id})

@login_required
def club_summary(request, club_id: int):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        raise Http404("Club not found")

    # NB: поля ниже — черновой минимум; заполним точно, когда утвердим модель.
    data = {
        "id": club.id,
        "name": getattr(club, "name", f"Club #{club_id}"),
        "country": getattr(club, "country", "") or "",
        "league": getattr(club, "league", "") or "",
        "status": "Owned by " + request.user.username,
        "tokens": getattr(request.user, "tokens", 0),   # временно
        "money": getattr(request.user, "money", 0),     # временно
    }
    return JsonResponse(data)
