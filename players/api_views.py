# players/api_views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from .models import Player

def _grouped_attributes(player: Player):
    # Берём правильные группы для вратаря/полевого
    groups = Player.GOALKEEPER_GROUPS if player.is_goalkeeper else Player.FIELD_PLAYER_GROUPS
    out = {}
    for group_name, attrs in groups.items():
        out[group_name] = [{"key": a, "value": int(getattr(player, a, 0))} for a in attrs]
    return out

@require_GET
def player_detail_api(request, pk: int):
    p = get_object_or_404(Player, pk=pk)

    # Национальность может быть пустой
    nat_code = str(p.nationality) if getattr(p, "nationality", None) else None
    try:
        nat_name = p.nationality.name if getattr(p, "nationality", None) else None
    except Exception:
        nat_name = nat_code

    club_obj = None
    if p.club_id:
        club_obj = {"id": p.club_id, "name": getattr(p.club, "name", None)}

    data = {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "full_name": f"{p.first_name} {p.last_name}".strip(),
        "age": p.age,
        "nationality": {"code": nat_code, "name": nat_name},
        "position": p.position,
        "player_class": p.player_class,
        "overall_rating": p.overall_rating,
        "experience": int(getattr(p, "experience", 0)),
        "is_goalkeeper": p.is_goalkeeper,
        "club": club_obj,
        "boost_count": p.boost_count,
        "next_boost_cost": p.get_boost_cost(),
        "in_bloom": p.is_in_bloom,
        "attributes": _grouped_attributes(p),
    }
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
