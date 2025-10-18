import logging
import random
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, List, Optional, Sequence

from django.db import transaction
from django.utils import timezone

from matches.models import Match, MatchBroadcastEvent, MatchEvent
from matches.realtime_clock import RealtimeConfig, get_realtime_config
from matches.utils import extract_player_id

logger = logging.getLogger(__name__)

RAW_EVENT_KEYS = (
    "event",
    "additional_event",
    "second_additional_event",
    "third_additional_event",
)

BROADCAST_KIND_DEFAULT = "micro_pass"
PAUSE_SHORT_RANGE = (1, 3)


@dataclass
class BroadcastItem:
    idx: int
    scheduled_at: timezone.datetime
    payload: dict
    idempotency_key: str


def _store_match_event(match: Match, payload: Optional[dict]) -> Optional[MatchEvent]:
    if not payload:
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
    data = {key: value for key, value in payload.items() if key in allowed_fields}
    data.setdefault("match", match)
    data.setdefault("minute", match.current_minute)
    return MatchEvent.objects.create(**data)


def _simulate_minute_actions(match: Match, max_actions: int) -> List[MatchEvent]:
    from matches.match_simulation import simulate_one_action

    created: List[MatchEvent] = []
    steps = 0
    while steps < max_actions:
        steps += 1
        result = simulate_one_action(match)
        for key in RAW_EVENT_KEYS:
            stored = _store_match_event(match, result.get(key))
            if stored:
                created.append(stored)
        match.save()
        if not result.get("continue", True):
            break
    return created


def ensure_minute_events(match: Match, *, max_actions: int = 8) -> List[MatchEvent]:
    existing = list(
        match.events.filter(minute=match.current_minute).select_related("player", "related_player")
    )
    if existing:
        return existing
    logger.debug(
        "No MatchEvent records found for match %s minute %s, simulating minute.",
        match.id,
        match.current_minute,
    )
    return _simulate_minute_actions(match, max_actions=max_actions)


def _team_players_from_lineup(match: Match, team) -> List:
    lineup_attr = "home_lineup" if team.id == match.home_team_id else "away_lineup"
    lineup = getattr(match, lineup_attr)
    player_ids: List[int] = []
    if isinstance(lineup, dict):
        for slot_value in lineup.values():
            pid = extract_player_id(slot_value)
            if pid:
                try:
                    player_ids.append(int(pid))
                except ValueError:
                    continue
    elif isinstance(lineup, str):
        for chunk in lineup.split(","):
            chunk = chunk.strip()
            if chunk.isdigit():
                player_ids.append(int(chunk))
    if player_ids:
        players = list(team.player_set.filter(id__in=player_ids))
        if players:
            return players
    return list(team.player_set.all())


def _pick_players(team_players: Sequence, count: int = 2) -> List:
    if not team_players:
        return []
    if len(team_players) <= count:
        return list(team_players)
    return random.sample(list(team_players), count)


def _goal_side_team(match: Match, events: Sequence[MatchEvent]):
    for event in reversed(events):
        if event.player_id:
            return event.player.club if hasattr(event.player, "club") else None
    return None


def _team_in_possession(match: Match, minute_events: Sequence[MatchEvent]):
    if match.possession_indicator == 1:
        return match.home_team
    if match.possession_indicator == 2:
        return match.away_team
    last_team = _goal_side_team(match, minute_events)
    if last_team:
        return last_team
    return match.home_team


def _build_pass_text(passer, receiver, extra: Optional[str] = None) -> str:
    if passer and receiver:
        base = f"{passer.last_name} keeps it simple for {receiver.last_name}"
    elif passer:
        base = f"{passer.last_name} keeps the ball moving and looks up"
    else:
        base = "The attack slows for a heartbeat, searching for space"
    if extra:
        return f"{base} — {extra}"
    return base


def _convert_event_to_micro(event: MatchEvent, match: Match, config: RealtimeConfig) -> dict:
    kind_map = {
        "goal": "goal",
        "shot_miss": "shot_miss",
        "pass": "micro_pass",
        "dribble": "micro_pass",
        "interception": "interception",
        "counterattack": "micro_pass",
        "foul": "lost_chance",
        "match_end": "lost_chance",
        "match_start": "micro_pass",
    }
    kind = kind_map.get(event.event_type, BROADCAST_KIND_DEFAULT)
    description = event.description or ""
    text = description or f"{event.get_event_type_display()}!"
    if kind == "micro_pass" and not description:
        extra = None
        if event.related_player:
            extra = f"{event.related_player.last_name} is already on the move"
        text = _build_pass_text(event.player, event.related_player, extra=extra)

    score_update = None
    if event.event_type == "goal":
        score_update = {
            "home": match.home_score,
            "away": match.away_score,
            "minute": event.minute,
        }
    payload = {
        "display_text": text,
        "kind": kind,
        "game_minute": event.minute,
        "team_id": event.player.club_id if event.player_id else None,
        "players": [pid for pid in [event.player_id, event.related_player_id] if pid],
        "zone_hint": getattr(match, "current_zone", None),
    }
    if event.personality_reason:
        payload["note"] = event.personality_reason
    if score_update:
        payload["score_update"] = score_update
    return payload


def _build_filler_events(match: Match, team, num_events: int, used_players: Optional[Sequence] = None):
    players = _team_players_from_lineup(match, team)
    fillers = []
    exclude = set(p.id for p in used_players or [] if p)
    for _ in range(num_events):
        pair = _pick_players([p for p in players if p.id not in exclude], 2)
        passer = pair[0] if pair else None
        receiver = pair[1] if len(pair) > 1 else None
        exclude.update({p.id for p in pair})
        text = _build_pass_text(passer, receiver)
        fillers.append(
            {
                "display_text": text,
                "kind": "micro_pass",
                "team_id": team.id if team else None,
                "players": [pid for pid in [getattr(passer, "id", None), getattr(receiver, "id", None)] if pid],
                "game_minute": match.current_minute,
                "zone_hint": getattr(match, "current_zone", None),
            }
        )
    return fillers


def _closing_event(match: Match, team) -> dict:
    team_name = team.name if team else "Team"
    return {
        "display_text": f"{team_name} slow things down and recycle through midfield",
        "kind": "lost_chance",
        "team_id": team.id if team else None,
        "players": [],
        "game_minute": match.current_minute,
        "zone_hint": "MID-C",
    }


def _schedule_events(match: Match, minute: int, minute_start, events: Sequence[dict], config: RealtimeConfig) -> List[BroadcastItem]:
    if not events:
        return []
    seconds_pm = max(config.seconds_per_game_minute, 5)
    max_duration = min(seconds_pm - 1, 50.0)
    if max_duration < 10:
        max_duration = seconds_pm - 0.5
    min_duration = min(35.0, max_duration * 0.7)
    if min_duration < 5.0:
        min_duration = max_duration * 0.5
    if min_duration <= 0:
        min_duration = max_duration * 0.5
    target_duration = random.uniform(min_duration, max_duration) if max_duration > 0 else seconds_pm - 1
    start_offset = min(5.0, max(1.5, target_duration * 0.15))
    offset = random.uniform(1.0, start_offset)
    pause_min, pause_max = config.micro_event_pause_range
    jitter_seconds = config.jitter_ms / 1000.0

    scheduled_items: List[BroadcastItem] = []
    for idx, payload in enumerate(events, start=1):
        jitter = random.uniform(-jitter_seconds, jitter_seconds)
        scheduled_at = minute_start + timedelta(seconds=max(0.0, offset + jitter))
        # Clamp to minute window
        window_end = minute_start + timedelta(seconds=seconds_pm - 0.25)
        if scheduled_at > window_end:
            scheduled_at = window_end
        idempotency_key = f"{match.id}:{minute}:{idx}"
        scheduled_items.append(
            BroadcastItem(
                idx=idx,
                scheduled_at=scheduled_at,
                payload=payload,
                idempotency_key=idempotency_key,
            )
        )
        if idx == len(events):
            break
        pause = random.uniform(pause_min, pause_max)
        # Shorter pause towards the end
        if idx >= len(events) - 2:
            pause = random.uniform(PAUSE_SHORT_RANGE[0], PAUSE_SHORT_RANGE[1])
        offset = min(offset + pause, target_duration)
    return scheduled_items


def build_minute_timeline(
    match: Match,
    *,
    config: Optional[RealtimeConfig] = None,
    minute_events: Optional[Sequence[MatchEvent]] = None,
    minute_start=None,
) -> List[BroadcastItem]:
    """
    Build micro-broadcast items for the current match minute.
    The caller is responsible for persisting (idempotently) and committing the transaction.
    """

    config = config or get_realtime_config()
    if not minute_start:
        minute_start = timezone.now()

    events = list(minute_events) if minute_events is not None else ensure_minute_events(match)
    team = _team_in_possession(match, events)
    used_players = [event.player for event in events if event.player_id]

    filler_needed = max(config.min_events_per_minute - len(events) - 1, 1)
    filler_events = _build_filler_events(match, team, max(filler_needed, 1), used_players=used_players)

    converted = [_convert_event_to_micro(event, match, config) for event in events]
    if not converted:
        converted.append(
            {
                "display_text": "Teams probe without carving out a clear chance.",
                "kind": "lost_chance",
                "team_id": team.id if team else None,
                "players": [],
                "game_minute": match.current_minute,
                "zone_hint": getattr(match, "current_zone", None),
            }
        )

    closing = _closing_event(match, team)

    combined: List[dict] = []
    combined.extend(filler_events)
    combined.extend(converted)
    combined.append(closing)

    if len(combined) > config.max_events_per_minute:
        # Preserve final event and closing remark.
        core = combined[: config.max_events_per_minute - 1]
        core.append(combined[-1])
        combined = core

    if len(combined) < config.min_events_per_minute:
        additional = _build_filler_events(
            match,
            team,
            config.min_events_per_minute - len(combined),
            used_players=used_players,
        )
        combined = combined + additional

    return _schedule_events(match, match.current_minute, minute_start, combined, config)


def persist_broadcast_items(match: Match, minute: int, items: Sequence[BroadcastItem]) -> List[MatchBroadcastEvent]:
    stored = []
    for item in items:
        defaults = {
            "match": match,
            "game_minute": minute,
            "idx_in_minute": item.idx,
            "payload_json": item.payload,
            "scheduled_at": item.scheduled_at,
            "status": MatchBroadcastEvent.STATUS_PENDING,
        }
        obj, created = MatchBroadcastEvent.objects.get_or_create(
            idempotency_key=item.idempotency_key,
            defaults=defaults,
        )
        if not created and obj.status == MatchBroadcastEvent.STATUS_PENDING:
            updates = {}
            if obj.payload_json != item.payload:
                updates["payload_json"] = item.payload
            if obj.scheduled_at != item.scheduled_at:
                updates["scheduled_at"] = item.scheduled_at
            if updates:
                for key, value in updates.items():
                    setattr(obj, key, value)
                obj.save(update_fields=list(updates.keys()))
        stored.append(obj)
        logger.debug(
            "Minute %s event idx=%s scheduled=%s payload=%s",
            minute,
            obj.idx_in_minute,
            obj.scheduled_at,
            obj.payload_json.get("kind"),
        )
    return stored


@transaction.atomic
def build_and_store_minute_timeline(
    match_id: int,
    *,
    config: Optional[RealtimeConfig] = None,
    minute_start=None,
    max_actions: int = 8,
) -> List[MatchBroadcastEvent]:
    match = (
        Match.objects.select_for_update()
        .select_related("home_team", "away_team")
        .get(pk=match_id)
    )
    config = config or get_realtime_config()
    if not config.enabled:
        logger.debug("Realtime broadcast disabled, skipping timeline generation.")
        return []
    minute_start = minute_start or timezone.now()
    minute = match.current_minute
    events = ensure_minute_events(match, max_actions=max_actions)
    items = build_minute_timeline(
        match,
        config=config,
        minute_events=events,
        minute_start=minute_start,
    )
    stored = persist_broadcast_items(match, minute, items)
    match.realtime_last_broadcast_minute = minute
    match.minute_building = False
    match.save(update_fields=['realtime_last_broadcast_minute', 'minute_building'])
    return stored
