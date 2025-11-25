# players/api_views.py
import json

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Player
from .services.avatar import generate_and_save_avatar


def _grouped_attributes(player: Player):
    """Собрать атрибуты игрока по группам (вратарь/полевой)."""
    groups = Player.GOALKEEPER_GROUPS if player.is_goalkeeper else Player.FIELD_PLAYER_GROUPS
    out = {}
    for group_name, attrs in groups.items():
        out[group_name] = [{"key": a, "value": int(getattr(player, a, 0))} for a in attrs]
    return out


def _abs(request, path: str) -> str:
    """Сделать абсолютный URL из относительного (удобно для фронта)."""
    if not path:
        return path
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return request.build_absolute_uri(path)


@require_GET
def player_detail_api(request, pk: int):
    """GET /api/players/<id>/ — детали игрока для фронта."""
    p = get_object_or_404(Player, pk=pk)

    # Национальность (может быть пустой)
    nat_code = str(p.nationality) if getattr(p, "nationality", None) else None
    try:
        nat_name = p.nationality.name if getattr(p, "nationality", None) else None
    except Exception:
        nat_name = nat_code

    # Клуб
    club_obj = None
    if p.club_id:
        club_obj = {"id": p.club_id, "name": getattr(p.club, "name", None)}

    # Аватар
    avatar_url = _abs(request, p.avatar.url) if getattr(p, "avatar", None) else None

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
        "avatar_url": avatar_url,
        "last_trained_at": p.last_trained_at.isoformat() if p.last_trained_at else None,
        "last_training_changes": p.last_training_summary if p.last_training_summary else None,
        "attributes": _grouped_attributes(p),
    }
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


@login_required
@require_POST
def player_generate_avatar_api(request, pk: int):
    """
    POST /api/players/<id>/avatar/ — РУЧНАЯ генерация аватара по запросу пользователя.
    Никакой автоматической генерации нет: вызываем ТОЛЬКО когда менеджер нажал кнопку.
    Доступ: владелец клуба этого игрока или суперпользователь.
    """
    p = get_object_or_404(Player, pk=pk)

    user = request.user
    # Простейшая проверка прав: попробуем угадать поле владельца клуба.
    is_owner = False
    try:
        club = getattr(p, "club", None)
        owner_id = None
        if club is not None:
            owner_id = getattr(club, "owner_id", None) or getattr(club, "user_id", None) or getattr(club, "manager_id", None)
        is_owner = (owner_id == user.id)
    except Exception:
        is_owner = False

    if not (user.is_superuser or is_owner):
        return HttpResponseForbidden("You are not allowed to generate avatar for this player.")

    if not settings.OPENAI_API_KEY:
        return HttpResponseBadRequest("OpenAI API key is not configured.")

    url = generate_and_save_avatar(p, overwrite=False)
    if not url:
        return HttpResponseBadRequest("Failed to generate avatar.")

    return JsonResponse({"avatar_url": _abs(request, url)})


@login_required
@require_POST
def player_extra_training_api(request, pk: int):
    """
    POST /api/players/<id>/extra-training/ - запускает «дополнительную тренировку»
    для указанного игрока (аналог boost_player_ajax, но в REST-формате).
    Ожидает JSON {"group": "<group_name>"}.
    """
    player = get_object_or_404(Player, pk=pk)

    user = request.user
    # Проверяем право управлять игроком (владельцем клуба)
    if player.club and getattr(player.club, "owner", None) != user:
        return JsonResponse(
            {
                "success": False,
                "message": "У вас нет прав запускать дополнительные тренировки для этого игрока.",
            },
            status=403,
        )

    try:
        payload = json.loads(request.body.decode() or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = {}

    if player.is_goalkeeper:
        groups_map = Player.GOALKEEPER_GROUPS
    else:
        groups_map = Player.FIELD_PLAYER_GROUPS

    group_name = (payload.get("group") or "").strip()
    if not group_name:
        # По умолчанию берем первую доступную группу
        group_name = next(iter(groups_map.keys()), "")

    if group_name not in groups_map:
        return JsonResponse(
            {
                "success": False,
                "message": "Неизвестная группа атрибутов.",
                "available_groups": list(groups_map.keys()),
            },
            status=400,
        )

    cost = player.get_boost_cost()
    if getattr(user, "tokens", 0) < cost:
        return JsonResponse(
            {
                "success": False,
                "message": "Недостаточно токенов для дополнительной тренировки.",
                "next_cost": cost,
                "tokens_left": getattr(user, "tokens", 0),
            },
            status=400,
        )

    attrs_in_group = groups_map[group_name]
    if player.is_goalkeeper:
        all_attrs = list({attr for values in Player.GOALKEEPER_GROUPS.values() for attr in values})
    else:
        all_attrs = list({attr for values in Player.FIELD_PLAYER_GROUPS.values() for attr in values})

    other_attrs = [attr for attr in all_attrs if attr not in attrs_in_group]

    old_values = {attr: getattr(player, attr, 0) for attr in all_attrs}

    # Списываем токены
    user.tokens -= cost
    user.save(update_fields=["tokens"])

    # +1 к каждой характеристике выбранной группы
    for attr in attrs_in_group:
        current = getattr(player, attr, 0)
        setattr(player, attr, current + 1)

    # +1 к двум случайным характеристикам вне группы
    import random

    random_attrs = other_attrs or all_attrs
    for _ in range(2):
        if not random_attrs:
            break
        attr = random.choice(random_attrs)
        current = getattr(player, attr, 0)
        setattr(player, attr, current + 1)

    player.boost_count += 1
    player.save()

    new_values = {attr: getattr(player, attr, 0) for attr in all_attrs}
    changes = {attr: new_values[attr] - old_values[attr] for attr in new_values if new_values[attr] != old_values[attr]}

    response_player = {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "full_name": player.full_name,
        "age": player.age,
        "position": player.position,
        "player_class": player.player_class,
        "overall_rating": player.overall_rating,
        "experience": int(getattr(player, "experience", 0)),
        "is_goalkeeper": player.is_goalkeeper,
        "club": {"id": player.club_id, "name": getattr(player.club, "name", None)} if player.club_id else None,
        "boost_count": player.boost_count,
        "next_boost_cost": player.get_boost_cost(),
        "in_bloom": player.is_in_bloom,
        "avatar_url": _abs(request, player.avatar.url) if getattr(player, "avatar", None) else None,
        "attributes": _grouped_attributes(player),
    }

    return JsonResponse(
        {
            "success": True,
            "message": "Дополнительная тренировка выполнена.",
            "group": group_name,
            "changes": changes,
            "tokens_left": getattr(user, "tokens", 0),
            "player": response_player,
        },
        json_dumps_params={"ensure_ascii": False},
    )
