import json
from datetime import datetime
from typing import Any, Optional

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from clubs.models import Club
from matches.match_preparation import PreMatchPreparation
from matches.engines.markov_v1 import engine_stub as simulate_one_action
from players.models import Player
from .models import Match, MatchEvent


def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    try:
        return timezone.localtime(dt).isoformat()
    except (ValueError, TypeError):
        return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _serialize_competition(match: Match) -> Optional[dict[str, Any]]:
    try:
        ch_match = match.championshipmatch
    except Exception:
        return None

    championship = ch_match.championship
    return {
        "id": championship.id,
        "name": getattr(championship.league, "name", None),
        "season": getattr(championship.season, "name", None),
        "round": ch_match.round,
        "match_day": ch_match.match_day,
    }


def _serialize_match(match: Match) -> dict[str, Any]:
    return {
        "id": match.id,
        "status": match.status,
        "status_label": match.get_status_display(),
        "processed": match.processed,
        "datetime": _serialize_datetime(match.datetime),
        "started_at": _serialize_datetime(match.started_at),
        "last_minute_update": _serialize_datetime(match.last_minute_update),
        "current_minute": match.current_minute,
        "waiting_for_next_minute": match.waiting_for_next_minute,
        "score": {"home": match.home_score, "away": match.away_score},
        "home": {
            "id": match.home_team_id,
            "name": match.home_team.name,
            "score": match.home_score,
            "tactic": match.home_tactic,
            "lineup": match.home_lineup,
        },
        "away": {
            "id": match.away_team_id,
            "name": match.away_team.name,
            "score": match.away_score,
            "tactic": match.away_tactic,
            "lineup": match.away_lineup,
        },
        "stats": {
            "shoots": match.st_shoots,
            "passes": match.st_passes,
            "possessions": match.st_possessions,
            "fouls": match.st_fouls,
            "injuries": match.st_injury,
            "home_momentum": match.home_momentum,
            "away_momentum": match.away_momentum,
            "home_pass_streak": match.home_pass_streak,
            "away_pass_streak": match.away_pass_streak,
        },
        "competition": _serialize_competition(match),
    }


def _serialize_player(player: Optional[Player]) -> Optional[dict[str, Any]]:
    if not player:
        return None
    return {
        "id": player.id,
        "name": f"{player.first_name} {player.last_name}".strip(),
        "position": player.position,
    }


def _serialize_event(event: MatchEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "minute": event.minute,
        "type": event.event_type,
        "type_label": event.get_event_type_display(),
        "description": event.description,
        "personality_reason": event.personality_reason,
        "timestamp": _serialize_datetime(event.timestamp),
        "player": _serialize_player(event.player),
        "related_player": _serialize_player(event.related_player),
    }


def _store_event(match: Match, event_payload: Optional[dict[str, Any]]) -> Optional[MatchEvent]:
    if not event_payload:
        return None

    allowed_fields = {
        "match",
        "minute",
        "event_type",
        "player",
        "related_player",
        "description",
        "personality_reason",
    }
    data = {key: value for key, value in event_payload.items() if key in allowed_fields}
    data.setdefault("match", match)
    return MatchEvent.objects.create(**data)


def _coerce_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_bool(value: Any) -> Optional[bool]:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    if isinstance(value, bool):
        return value
    return None


@login_required
def match_list_api(request):
    """
    Return a paginated list of matches in JSON format.
    Supported query parameters:
      - club_id: filter by club involvement (home or away)
      - status: match status filter
      - processed: true/false
      - ordering: 'datetime' | '-datetime'
      - page, page_size
    """
    qs = Match.objects.select_related(
        "home_team",
        "away_team",
        "championshipmatch__championship__league",
        "championshipmatch__championship__season",
    )

    club_id = _coerce_int(request.GET.get("club_id"))
    user_club = getattr(request.user, "club", None)
    if club_id:
        qs = qs.filter(Q(home_team_id=club_id) | Q(away_team_id=club_id))
    elif user_club:
        qs = qs.filter(Q(home_team=user_club) | Q(away_team=user_club))

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    processed = _coerce_bool(request.GET.get("processed"))
    if processed is not None:
        qs = qs.filter(processed=processed)

    ordering = request.GET.get("ordering", "-datetime")
    if ordering not in {"datetime", "-datetime"}:
        ordering = "-datetime"
    qs = qs.order_by(ordering)

    page_number = _coerce_int(request.GET.get("page"), 1) or 1
    page_size = _coerce_int(request.GET.get("page_size"), 10) or 10
    page_size = max(1, min(page_size, 100))

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page_number)

    return JsonResponse(
        {
            "results": [_serialize_match(match) for match in page_obj.object_list],
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "page": page_obj.number,
            "page_size": page_obj.paginator.per_page,
        },
        json_dumps_params={"ensure_ascii": False},
    )


@login_required
def match_detail_api(request, pk: int):
    match = get_object_or_404(
        Match.objects.select_related(
            "home_team",
            "away_team",
            "championshipmatch__championship__league",
            "championshipmatch__championship__season",
        ),
        pk=pk,
    )
    return JsonResponse(_serialize_match(match), json_dumps_params={"ensure_ascii": False})


@login_required
def match_events_api(request, pk: int):
    match = get_object_or_404(Match, pk=pk)
    events_qs = match.events.select_related("player", "related_player").order_by("minute", "id")
    return JsonResponse(
        {"match": match.id, "events": [_serialize_event(event) for event in events_qs]},
        json_dumps_params={"ensure_ascii": False},
    )


@login_required
@require_http_methods(["POST"])
def match_create_api(request):
    """
    Create a new match.
    Payload JSON fields:
      - home_team_id (optional, defaults to the user's club if available)
      - away_team_id (optional when auto_opponent=true)
      - datetime (ISO formatted string, optional)
      - auto_start (bool, default True)
      - auto_opponent (bool, default True) - pick a random opponent if away_team_id is omitted
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    home_team_id = payload.get("home_team_id") or getattr(getattr(request.user, "club", None), "id", None)
    if not home_team_id:
        return JsonResponse({"error": "home_team_id is required"}, status=400)

    auto_opponent = payload.get("auto_opponent", True)
    away_team_id = payload.get("away_team_id")

    try:
        home_team = Club.objects.get(pk=home_team_id)
    except Club.DoesNotExist:
        return JsonResponse({"error": "Home team not found"}, status=404)

    if not away_team_id:
        if not auto_opponent:
            return JsonResponse({"error": "away_team_id is required when auto_opponent is false"}, status=400)
        opponent_qs = Club.objects.exclude(pk=home_team_id)
        bot_qs = opponent_qs.filter(is_bot=True)
        opponent = bot_qs.order_by("?").first() or opponent_qs.order_by("?").first()
        if not opponent:
            return JsonResponse({"error": "Unable to find opponent"}, status=400)
        away_team = opponent
    else:
        try:
            away_team = Club.objects.get(pk=away_team_id)
        except Club.DoesNotExist:
            return JsonResponse({"error": "Away team not found"}, status=404)

    datetime_raw = payload.get("datetime")
    if datetime_raw:
        match_datetime = parse_datetime(datetime_raw)
        if match_datetime is None:
            return JsonResponse({"error": "Invalid datetime format"}, status=400)
    else:
        match_datetime = timezone.now()

    auto_start = payload.get("auto_start", True)

    with transaction.atomic():
        match = Match.objects.create(
            home_team=home_team,
            away_team=away_team,
            datetime=match_datetime,
            status="scheduled",
            current_minute=1,
            home_tactic="balanced",
            away_tactic="balanced",
        )

        if auto_start:
            prep = PreMatchPreparation(match)
            if not prep.prepare_match():
                errors = prep.get_validation_errors()
                match.delete()
                return JsonResponse({"error": "Match preparation failed", "details": errors}, status=400)
            match.status = "in_progress"
            match.save()

    return JsonResponse({"match": _serialize_match(match)}, status=201, json_dumps_params={"ensure_ascii": False})


@login_required
@require_http_methods(["POST"])
def match_substitute_api(request, pk: int):
    """
    Register a substitution event for the given match.
    JSON payload fields:
      - out_player_id (required)
      - in_player_id (optional)
      - description (optional)
    """
    match = get_object_or_404(Match, pk=pk)
    if match.status != "in_progress":
        return JsonResponse({"error": "Match is not currently in progress"}, status=400)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    out_player_id = _coerce_int(payload.get("out_player_id"))
    in_player_id = _coerce_int(payload.get("in_player_id"))
    description = payload.get("description")

    if not out_player_id:
        return JsonResponse({"error": "out_player_id is required"}, status=400)

    out_player = Player.objects.filter(pk=out_player_id).first()
    if not out_player:
        return JsonResponse({"error": "Player to substitute out not found"}, status=404)

    in_player = None
    if in_player_id:
        in_player = Player.objects.filter(pk=in_player_id).first()
        if not in_player:
            return JsonResponse({"error": "Player to substitute in not found"}, status=404)

    if description:
        event_description = description
    elif in_player:
        event_description = f"Substitution: {out_player} replaced by {in_player}"
    else:
        event_description = f"Substitution: {out_player} leaves the pitch"

    event = MatchEvent.objects.create(
        match=match,
        minute=match.current_minute,
        event_type="substitution",
        player=out_player,
        related_player=in_player,
        description=event_description,
    )

    if match.st_injury and match.st_injury > 0:
        match.st_injury -= 1
        match.save(update_fields=["st_injury"])

    match.refresh_from_db()

    return JsonResponse(
        {"match": _serialize_match(match), "event": _serialize_event(event)},
        json_dumps_params={"ensure_ascii": False},
    )
