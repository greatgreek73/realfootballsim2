# tournaments/tasks.py

import time
import logging
from typing import Optional, Iterable
from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.conf import settings
from django.core.management import call_command
from matches.models import Match, MatchEvent
from matches.engines.markov_runtime import simulate_markov_minute
from players.models import Player, get_player_line
from clubs.models import Club
from .models import Season, Championship, League
import random
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("match_creation")


ZONE_HINT_TO_FIELD = {
    "DEF": "DEF-C",
    "MID": "MID-C",
    "FINAL": "AM-C",
}
ZONE_TEXT = {
    "DEF": "the defensive third",
    "MID": "midfield",
    "FINAL": "the final third",
}


def _map_zone_from_markov(zone_hint: Optional[str], fallback: str) -> str:
    if not zone_hint:
        return fallback or "MID-C"
    return ZONE_HINT_TO_FIELD.get(zone_hint.upper(), fallback or "MID-C")


def _possession_indicator_from_markov(possession: Optional[str]) -> int:
    if possession == "home":
        return 1
    if possession == "away":
        return 2
    return 0


def _serialize_event_for_ws(event: MatchEvent) -> dict:
    return {
        "id": event.id,
        "minute": event.minute,
        "event_type": event.event_type,
        "description": event.description,
        "personality_reason": event.personality_reason,
        "player_name": f"{event.player.first_name} {event.player.last_name}" if event.player else "",
        "related_player_name": f"{event.related_player.first_name} {event.related_player.last_name}" if event.related_player else "",
    }


def _team_display(match: Match, side: Optional[str]) -> str:
    if side == "home":
        return match.home_team.name
    if side == "away":
        return match.away_team.name
    return "Unknown team"


def _zone_text(zone: Optional[str]) -> str:
    if not zone:
        return "midfield"
    return ZONE_TEXT.get(zone.upper(), zone.lower())


def _map_markov_event_to_match_event(match: Match, raw_event: dict) -> Optional[dict]:
    label = (raw_event.get("label") or "").upper()
    frm = (raw_event.get("from") or "").upper()
    turnover = bool(raw_event.get("turnover"))
    zone_label = _zone_text(raw_event.get("zone"))
    
    # If an individual player (actor) is part of the event, we use them
    raw_actor_name = raw_event.get("actor_name")
    raw_actor_id = raw_event.get("actor_id")
    
    # Fallback to team name if no player
    team_actor = _team_display(match, raw_event.get("prev_possession") or raw_event.get("possession"))
    actor_display = raw_actor_name if raw_actor_name else team_actor

    result = {}
    if raw_actor_id:
        try:
            result["player"] = Player.objects.get(pk=raw_actor_id)
        except Player.DoesNotExist:
            pass

    if label == "SHOT:GOAL":
        if raw_actor_name:
            description = f"Goal! {raw_actor_name} scores for {team_actor} from {zone_label}!"
        else:
            description = f"Goal! {team_actor} score from {zone_label}."
        result.update({"event_type": "goal", "description": description})
        return result

    if label in {"SHOT:MISS", "SHOT:BLOCK"}:
        description = f"{actor_display} takes a shot from {zone_label} but misses the target."
        result.update({"event_type": "shot_miss", "description": description})
        return result

    if frm == "FOUL":
        description = f"Foul by {actor_display} in {zone_label}."
        result.update({"event_type": "foul", "description": description})
        return result
        
    if turnover:
        winner_side = raw_event.get("possession")
        winner_team = _team_display(match, winner_side)
        description = f"Turnover! {winner_team} gain possession in {zone_label}."
        result.update({"event_type": "interception", "description": description})
        return result
    return None


def _mark_match_error(match_id: int, reason: str) -> None:
    try:
        updated = Match.objects.filter(pk=match_id).update(
            status='error',
            waiting_for_next_minute=False,
        )
        if updated:
            logger.warning(f"⚠️ Матч ID={match_id} помечен как error: {reason}")
    except Exception:
        logger.exception(f"⚠️ Не удалось обновить статус матча ID={match_id} после ошибки: {reason}")


@shared_task(name='tournaments.simulate_active_matches', bind=True)
def simulate_active_matches(self):
    """
    Симуляция минут матча на основе марковского движка.
    Запускается периодически (например, каждые 2 секунды).
    """
    now = timezone.now()
    logger.info(f"🔁 [simulate_active_matches] Запуск симуляции активных матчей в {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("🔍 Нет матчей со статусом 'in_progress'.")
        return "No matches in progress"

    logger.info(f"✅ Найдено {matches.count()} матчей для марковской симуляции.")

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    processed = 0

    for match in matches:
        try:
            logger.info(f"🔒 Блокировка матча ID={match.id} для марковской минуты...")
            with transaction.atomic():
                match_locked = (
                    Match.objects.select_for_update()
                    .select_related('home_team', 'away_team')
                    .get(id=match.id)
                )

                if match_locked.status != 'in_progress':
                    continue

                dirty_fields = []
                if match_locked.started_at is None:
                    match_locked.started_at = now
                    dirty_fields.append('started_at')
                if match_locked.last_minute_update is None:
                    match_locked.last_minute_update = now
                    dirty_fields.append('last_minute_update')

                if match_locked.waiting_for_next_minute:
                    if dirty_fields:
                        match_locked.save(update_fields=dirty_fields)
                    logger.info(f"⏭️ Матч ID={match_locked.id} ждёт завершения текущей минуты, пропуск.")
                    continue

                # --- Prepare Rosters for Runtime ---
                # We need to transform the match lineup (dict of slot -> player info)
                # into the format expected by markov_runtime:
                # rosters = {
                #   "home": {"GK": [...], "DEF": [...], "MID": [...], "FWD": [...]},
                #   "away": {"GK": [...], ...}
                # }

                rosters_map = {"home": {}, "away": {}}
                
                def _build_team_roster(team_side, lineup_data):
                    # lineup_data: {'1': {'playerId': '101', ...}, ...} OR {'1': 101, ...}
                    if not lineup_data: 
                        return
                    
                    pids = []
                    for slot, p_info in lineup_data.items():
                        if isinstance(p_info, dict):
                            pid = p_info.get('playerId')
                        else:
                            # Assume it's an ID directly (int or str) if not a dict
                            pid = p_info
                            
                        if pid: 
                            pids.append(pid)
                    
                    if not pids: 
                        return

                    # Bulk fetch players with optimized stats
                    players_qs = Player.objects.filter(id__in=pids)
                    
                    for p in players_qs:
                        # Get line (GK, DEF, MID, FWD)
                        line = get_player_line(p)
                        
                        # Build minimal stats dict for the engine
                        # We sum attributes or take overall for simple comparison
                        stats = {
                            "overall": p.overall_rating
                        }
                        
                        player_entry = {
                            "id": p.id,
                            "name": p.last_name,  # or full_name
                            "stats": stats,
                        }
                        
                        if line not in rosters_map[team_side]:
                            rosters_map[team_side][line] = []
                        rosters_map[team_side][line].append(player_entry)

                _build_team_roster("home", match_locked.home_lineup)
                _build_team_roster("away", match_locked.away_lineup)

                seed_value = int(match_locked.markov_seed or match_locked.id)
                result = simulate_markov_minute(
                    seed=seed_value,
                    token=match_locked.markov_token,
                    home_name=match_locked.home_team.name,
                    away_name=match_locked.away_team.name,
                    rosters=rosters_map,
                )
                minute_summary = result["minute_summary"]
                counts = minute_summary.get("counts", {})
                totals = minute_summary.get("score_total", {})

                pass_events = 0

                match_locked.markov_seed = seed_value
                match_locked.markov_token = minute_summary.get("token")
                match_locked.markov_coefficients = minute_summary.get("coefficients")
                match_locked.markov_last_summary = minute_summary
                match_locked.home_score = totals.get("home", match_locked.home_score)
                match_locked.away_score = totals.get("away", match_locked.away_score)
                match_locked.st_shoots += counts.get("shot", 0)
                match_locked.st_fouls += counts.get("foul", 0)
                match_locked.st_possessions += 1
                match_locked.possession_indicator = _possession_indicator_from_markov(
                    minute_summary.get("possession_end")
                )
                match_locked.current_zone = _map_zone_from_markov(
                    minute_summary.get("zone_end"),
                    match_locked.current_zone,
                )
                match_locked.last_minute_update = timezone.now()

                reg_minutes = result.get("regulation_minutes", 90)
                minute_number = minute_summary.get("minute", match_locked.current_minute)
                match_locked.waiting_for_next_minute = True
                if minute_number >= reg_minutes:
                    match_locked.status = 'finished'
                    match_locked.waiting_for_next_minute = False
                    match_locked.current_minute = reg_minutes

                match_locked.st_passes += pass_events
                match_locked.save()

                created_events = []

                # 1. Global narrative (e.g. Kick-off)
                for line in minute_summary.get("pure_narrative") or []:
                    event = MatchEvent.objects.create(
                        match=match_locked,
                        minute=minute_number,
                        event_type="info",
                        description=line,
                    )
                    created_events.append(event)

                # 2. Tick events (one per tick max)
                for raw_event in minute_summary.get("events") or []:
                    mapped = _map_markov_event_to_match_event(match_locked, raw_event)
                    if mapped:
                        event_kwargs = {
                            "match": match_locked,
                            "minute": minute_number,
                            "event_type": mapped.get("event_type", "info"),
                            "description": mapped.get("description", ""),
                        }
                        if mapped.get("player"):
                           event_kwargs["player"] = mapped["player"]
                        
                        event = MatchEvent.objects.create(**event_kwargs)
                        
                        created_events.append(event)
                        if mapped.get("stat") == "pass":
                            pass_events += 1
                    elif raw_event.get("narrative"):
                        event = MatchEvent.objects.create(
                            match=match_locked,
                            minute=minute_number,
                            event_type="info",
                            description=raw_event["narrative"],
                        )
                        created_events.append(event)

                processed += 1
                possessing_team_id = None
                if match_locked.possession_indicator == 1:
                    possessing_team_id = str(match_locked.home_team_id)
                elif match_locked.possession_indicator == 2:
                    possessing_team_id = str(match_locked.away_team_id)

                if channel_layer:
                    message_payload = {
                        "type": "match_update",
                        "data": {
                            "match_id": match_locked.id,
                            "minute": minute_number,
                            "home_score": match_locked.home_score,
                            "away_score": match_locked.away_score,
                            "status": match_locked.status,
                            "st_shoots": match_locked.st_shoots,
                            "st_passes": match_locked.st_passes,
                            "st_possessions": match_locked.st_possessions,
                            "st_fouls": match_locked.st_fouls,
                            "st_injury": match_locked.st_injury,
                            "home_momentum": match_locked.home_momentum,
                            "away_momentum": match_locked.away_momentum,
                            "current_zone": match_locked.current_zone,
                            "possessing_team_id": possessing_team_id,
                            "events": [_serialize_event_for_ws(evt) for evt in created_events],
                            "partial_update": True,
                            "markov_minute": minute_summary,
                        },
                    }
                    try:
                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            message_payload,
                        )
                    except Exception as ws_error:  # pragma: no cover - best effort broadcast
                        logger.warning(
                            "⚠️ WebSocket broadcast failed for match %s: %s",
                            match_locked.id,
                            ws_error,
                        )

        except Match.DoesNotExist:
            logger.warning(f"❌ Матч ID={match.id} исчез из базы во время симуляции.")
        except OperationalError as e:
            logger.error(f"🔒 Ошибка блокировки базы данных для матча {match.id}: {e}")
        except Exception as e:
            logger.exception(f"🔥 Ошибка при симуляции матча {match.id}: {e}")
            _mark_match_error(match.id, str(e))

    if processed == 0:
        return "No eligible matches for Markov minute"
    return f"Simulated Markov minutes for {processed} matches"


@shared_task(name='tournaments.check_season_end', bind=True)
def check_season_end(self):
    """
    ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╤В ╨╛╨║╨╛╨╜╤З╨░╨╜╨╕╨╡ ╤Б╨╡╨╖╨╛╨╜╨░ ╨╕ ╤Б╨╛╨╖╨┤╨░╤С╤В ╨╜╨╛╨▓╤Л╨╣ ╨┐╤А╨╕ ╨╜╨╡╨╛╨▒╤Е╨╛╨┤╨╕╨╝╨╛╤Б╤В╨╕.
    ╨Ч╨░╨┐╤Г╤Б╨║╨░╨╡╤В╤Б╤П, ╨║ ╨┐╤А╨╕╨╝╨╡╤А╤Г, ╤А╨░╨╖ ╨▓ ╨┤╨╡╨╜╤М ╨╕╨╗╨╕ ╤А╨░╨╖ ╨▓ ╤З╨░╤Б (╤Б╨╛╨│╨╗╨░╤Б╨╜╨╛ ╨╜╨░╤Б╤В╤А╨╛╨╣╨║╨░╨╝ Celery Beat).
    """
    try:
        with transaction.atomic():
            # ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝ select_for_update ╨┤╨╗╤П ╨┐╤А╨╡╨┤╨╛╤В╨▓╤А╨░╤Й╨╡╨╜╨╕╤П ╨│╨╛╨╜╨╛╨║ ╨┐╤А╨╕ ╨┐╤А╨╛╨▓╨╡╤А╨║╨╡/╨╖╨░╨▓╨╡╤А╤И╨╡╨╜╨╕╨╕ ╤Б╨╡╨╖╨╛╨╜╨░
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()

            is_end_date_passed = today > current_season.end_date

            # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝, ╨▓╤Б╨╡ ╨╗╨╕ ╨╝╨░╤В╤З╨╕ ╤Б╨╡╨╖╨╛╨╜╨░ ╨╖╨░╨▓╨╡╤А╤И╨╡╨╜╤Л
            all_matches_in_season = Match.objects.filter(
                championshipmatch__championship__season=current_season
            )
            finished_matches_count = all_matches_in_season.filter(status='finished').count()
            total_matches_count = all_matches_in_season.count() # ╨Ю╨▒╤Й╨╡╨╡ ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨╝╨░╤В╤З╨╡╨╣ ╨▓ ╤Б╨╡╨╖╨╛╨╜╨╡

            # ╨г╤Б╨╗╨╛╨▓╨╕╨╡ ╨╖╨░╨▓╨╡╤А╤И╨╡╨╜╨╕╤П: ╨┤╨░╤В╨░ ╨┐╤А╨╛╤И╨╗╨░ ╨Ш ╨▓╤Б╨╡ ╨╝╨░╤В╤З╨╕ ╤Б╤Л╨│╤А╨░╨╜╤Л (╨╕╨╗╨╕ ╨╜╨╡╤В ╨╝╨░╤В╤З╨╡╨╣)
            all_matches_played = (total_matches_count == 0 or finished_matches_count == total_matches_count)

            if is_end_date_passed and all_matches_played:
                # ╨Э╨░ ╨▓╤Б╤П╨║╨╕╨╣ ╤Б╨╗╤Г╤З╨░╨╣ ╨╡╤Й╨╡ ╤А╨░╨╖ ╨┐╤А╨╛╨▓╨╡╤А╨╕╨╝ ╨╜╨╡╨╖╨░╨▓╨╡╤А╤И╨╡╨╜╨╜╤Л╨╡ ╨╝╨░╤В╤З╨╕ (╤Е╨╛╤В╤П all_matches_played ╨┤╨╛╨╗╨╢╨╜╨╛ ╨▒╤Л╨╗╨╛ ╤Н╤В╨╛ ╨┐╨╛╨║╤А╤Л╤В╤М)
                unfinished_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress', 'paused'] # ╨Ф╨╛╨▒╨░╨▓╨╕╨╝ paused
                ).count()

                if unfinished_matches > 0:
                    return f"Season {current_season.number} has {unfinished_matches} unfinished matches"

                call_command('handle_season_transitions')

                current_season.is_active = False
                current_season.save()

                call_command('create_new_season')

                new_season = Season.objects.get(is_active=True)
                championships = Championship.objects.filter(season=new_season)
                total_teams = sum(c.teams.count() for c in championships)
                return (
                    f"Season {current_season.number} ended. "
                    f"New season {new_season.number} created."
                )
            else:
                 return f"Season {current_season.number} is still active"

    except Season.DoesNotExist:
        try:
             # ╨Я╨╛╨┐╤Л╤В╨║╨░ ╤Б╨╛╨╖╨┤╨░╤В╤М ╤Б╨╡╨╖╨╛╨╜, ╨╡╤Б╨╗╨╕ ╨╜╨╕ ╨╛╨┤╨╜╨╛╨│╨╛ ╨░╨║╤В╨╕╨▓╨╜╨╛╨│╨╛ ╨╜╨╡╤В
             call_command('create_new_season')
             return "No active season found, created initial season."
        except Exception as e_create:
             return "No active season found, failed to create initial one."
    except Exception as e:
        # ╨Э╨╡ ╨┐╨╡╤А╨╡╨▓╤Л╨▒╤А╨░╤Б╤Л╨▓╨░╨╡╨╝ ╨╛╤И╨╕╨▒╨║╤Г, ╤З╤В╨╛╨▒╤Л ╨╜╨╡ ╨╛╤Б╤В╨░╨╜╨░╨▓╨╗╨╕╨▓╨░╤В╤М Celery Beat
        return f"Error in season end check: {str(e)}"


def extract_player_ids_from_lineup(current_lineup):
    """
    ╨Ш╨╖╨▓╨╗╨╡╨║╨░╨╡╤В ID ╨╕╨│╤А╨╛╨║╨╛╨▓ ╨╕╨╖ ╤Б╨╗╨╛╨▓╨░╤А╤П ╤Б╨╛╤Б╤В╨░╨▓╨░ (╨║╨╗╤О╤З╨╕ '0'-'10').
    ╨Ю╨╢╨╕╨┤╨░╨╡╤В, ╤З╤В╨╛ current_lineup - ╤Н╤В╨╛ ╨▓╨╜╤Г╤В╤А╨╡╨╜╨╜╨╕╨╣ ╤Б╨╗╨╛╨▓╨░╤А╤М {'0': {...}, '1': {...}, ...}.
    """
    player_ids = set()
    if not isinstance(current_lineup, dict):
        return player_ids

    for slot_index_str, player_data in current_lineup.items():
        if isinstance(player_data, dict):
            pid_str = player_data.get('playerId')
            if pid_str:
                try:
                    player_ids.add(int(pid_str))
                except (ValueError, TypeError):
                    pass
        # ╨Ь╨╛╨╢╨╜╨╛ ╨┤╨╛╨▒╨░╨▓╨╕╤В╤М ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╤Г ╤Б╤В╨░╤А╨╛╨│╨╛ ╤Д╨╛╤А╨╝╨░╤В╨░, ╨╡╤Б╨╗╨╕ ╨╛╨╜ ╨╡╤Й╨╡ ╨│╨┤╨╡-╤В╨╛ ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В╤Б╤П
        # else: ...

    return player_ids


# --- ╨Ш╨б╨Я╨а╨Р╨Т╨Ы╨Х╨Э╨Э╨Р╨п ╨д╨г╨Э╨Ъ╨ж╨Ш╨п complete_lineup ---
def complete_lineup(club: Club, current_lineup: dict):
    """
    ╨Ф╨╛╨┐╨╛╨╗╨╜╤П╨╡╤В ╨┐╨╡╤А╨╡╨┤╨░╨╜╨╜╤Л╨╣ ╤Б╨╛╤Б╤В╨░╨▓ ╨┤╨╛ 11 ╨╕╨│╤А╨╛╨║╨╛╨▓, ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╤П ╤Б╤Г╤Й╨╡╤Б╤В╨▓╤Г╤О╤Й╨╕╤Е
    ╨╕ ╨┤╨╛╨▒╨░╨▓╨╗╤П╤П ╨╜╨╡╨┤╨╛╤Б╤В╨░╤О╤Й╨╕╤Е ╤Б╨╗╤Г╤З╨░╨╣╨╜╤Л╨╝ ╨╛╨▒╤А╨░╨╖╨╛╨╝ ╨▒╨╡╨╖ ╨┤╤Г╨▒╨╗╨╕╤А╨╛╨▓╨░╨╜╨╕╤П.
    ╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╤В ╨┐╨╛╨╗╨╜╤Л╨╣ ╤Б╨╛╤Б╤В╨░╨▓ (╤Б╨╗╨╛╨▓╨░╤А╤М 0-10) ╨╕╨╗╨╕ None, ╨╡╤Б╨╗╨╕ ╨╜╨╡╨▓╨╛╨╖╨╝╨╛╨╢╨╜╨╛.
    ╨Ю╨╢╨╕╨┤╨░╨╡╤В current_lineup ╨▓ ╤Д╨╛╤А╨╝╨░╤В╨╡ {'0': {...}, '1': {...}, ...}.
    """
    all_players_qs = club.player_set.all()
    all_players_map = {p.id: p for p in all_players_qs} # ╨б╨╗╨╛╨▓╨░╤А╤М ╨┤╨╗╤П ╨▒╤Л╤Б╤В╤А╨╛╨│╨╛ ╨┤╨╛╤Б╤В╤Г╨┐╨░ ╨┐╨╛ ID
    total_players_in_club = len(all_players_map)

    if total_players_in_club < 11:
        return None

    final_lineup = {} # ╨а╨╡╨╖╤Г╨╗╤М╤В╨░╤В ╨▒╤Г╨┤╨╡╤В ╨╖╨┤╨╡╤Б╤М (╨║╨╛╨┐╨╕╤П ╨╕╨╗╨╕ ╨┤╨╛╨┐╨╛╨╗╨╜╨╡╨╜╨╜╤Л╨╣)
    used_player_ids = set()

    # --- 1. ╨Ю╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╨╝ ╤В╨╡╨║╤Г╤Й╨╕╨╣ ╤Б╨╛╤Б╤В╨░╨▓ (╨║╨╗╤О╤З╨╕ '0' - '10') ---
    if isinstance(current_lineup, dict):
        for slot_index_str, player_data in current_lineup.items():
            # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨║╨╛╤А╤А╨╡╨║╤В╨╜╨╛╤Б╤В╤М ╨║╨╗╤О╤З╨░ ╤Б╨╗╨╛╤В╨░
            try:
                slot_index_int = int(slot_index_str)
                if not (0 <= slot_index_int <= 10):
                    continue
            except (ValueError, TypeError):
                continue

            if not isinstance(player_data, dict):
                continue

            player_id_str = player_data.get('playerId')
            if not player_id_str:
                continue

            try:
                player_id = int(player_id_str)
                if player_id in used_player_ids:
                    continue

                player_obj = all_players_map.get(player_id)
                if not player_obj:
                    continue

                # ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨╕╨│╤А╨╛╨║╨░ ╨╕╨╖ ╤В╨╡╨║╤Г╤Й╨╡╨│╨╛ ╤Б╨╛╤Б╤В╨░╨▓╨░ ╨▓ ╨╕╤В╨╛╨│╨╛╨▓╤Л╨╣
                final_lineup[slot_index_str] = {
                    "playerId": str(player_obj.id),
                    "slotType": player_data.get("slotType", "unknown"), # ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╤В╨╕╨┐ ╤Б╨╗╨╛╤В╨░, ╨╡╤Б╨╗╨╕ ╨╡╤Б╤В╤М
                    "slotLabel": player_data.get("slotLabel", f"SLOT_{slot_index_str}"),
                    "playerPosition": player_obj.position
                }
                used_player_ids.add(player_id)

            except (ValueError, TypeError):
                continue

    # --- 2. ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨╕ ╨┤╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨▓╤А╨░╤В╨░╤А╤П, ╨╡╤Б╨╗╨╕ ╨╡╨│╨╛ ╨╜╨╡╤В ---
    if '0' not in final_lineup:
        # ╨Ш╤Й╨╡╨╝ ╨▓╤А╨░╤В╨░╤А╤П ╤Б╤А╨╡╨┤╨╕ ╨Э╨Х╨╕╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╨╜╨╜╤Л╤Е ╨╕╨│╤А╨╛╨║╨╛╨▓
        available_gks = [
            p for p_id, p in all_players_map.items()
            if p.position == 'Goalkeeper' and p_id not in used_player_ids
        ]
        if not available_gks:
            return None # ╨Э╨╡ ╨╝╨╛╨╢╨╡╨╝ ╤Б╤Д╨╛╤А╨╝╨╕╤А╨╛╨▓╨░╤В╤М ╤Б╨╛╤Б╤В╨░╨▓ ╨▒╨╡╨╖ ╨▓╤А╨░╤В╨░╤А╤П

        keeper = available_gks[0] # ╨С╨╡╤А╨╡╨╝ ╨┐╨╡╤А╨▓╨╛╨│╨╛ ╨┤╨╛╤Б╤В╤Г╨┐╨╜╨╛╨│╨╛
        final_lineup['0'] = {
            "playerId": str(keeper.id),
            "slotType": "goalkeeper",
            "slotLabel": "GK",
            "playerPosition": keeper.position
        }
        used_player_ids.add(keeper.id)

    # --- 3. ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨╜╨╡╨┤╨╛╤Б╤В╨░╤О╤Й╨╕╤Е ╨┐╨╛╨╗╨╡╨▓╤Л╤Е ╨╕╨│╤А╨╛╨║╨╛╨▓ ---
    needed_players = 11 - len(final_lineup)
    if needed_players <= 0:
        # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝, ╤З╤В╨╛ ╨▓╤Б╨╡ ╨║╨╗╤О╤З╨╕ 0-10 ╨╡╤Б╤В╤М
        if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
            return final_lineup # ╨б╨╛╤Б╤В╨░╨▓ ╤Г╨╢╨╡ ╨┐╨╛╨╗╨╜╤Л╨╣ ╨╕ ╨║╨╛╤А╤А╨╡╨║╤В╨╜╤Л╨╣
        else:
            return None # ╨Э╨╡╨╛╨╢╨╕╨┤╨░╨╜╨╜╨░╤П ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤П

    # ╨Ш╤Й╨╡╨╝ ╨┤╨╛╤Б╤В╤Г╨┐╨╜╤Л╤Е ╨┐╨╛╨╗╨╡╨▓╤Л╤Е ╨╕╨│╤А╨╛╨║╨╛╨▓ (╨╜╨╡ ╨▓╤А╨░╤В╨░╤А╨╡╨╣ ╨╕ ╨╜╨╡ ╨╕╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╨╜╨╜╤Л╤Е)
    available_field_players = [
        p for p_id, p in all_players_map.items()
        if p.position != 'Goalkeeper' and p_id not in used_player_ids
    ]

    if len(available_field_players) < needed_players:
        return None # ╨Э╨╡ ╤Е╨▓╨░╤В╨░╨╡╤В ╨╕╨│╤А╨╛╨║╨╛╨▓ ╨┤╨╗╤П ╨┤╨╛╨║╨╛╨╝╨┐╨╗╨╡╨║╤В╨░╤Ж╨╕╨╕

    # ╨Т╤Л╨▒╨╕╤А╨░╨╡╨╝ ╤Б╨╗╤Г╤З╨░╨╣╨╜╤Л╤Е ╨╕╨╖ ╨┤╨╛╤Б╤В╤Г╨┐╨╜╤Л╤Е
    chosen_fillers = random.sample(available_field_players, needed_players)
    filler_idx = 0

    # ╨Ч╨░╨┐╨╛╨╗╨╜╤П╨╡╨╝ ╨┐╤Г╤Б╤В╤Л╨╡ ╤Б╨╗╨╛╤В╤Л 1-10
    for i in range(1, 11):
        slot_key = str(i)
        if slot_key not in final_lineup:
            if filler_idx < len(chosen_fillers):
                player_to_add = chosen_fillers[filler_idx]
                final_lineup[slot_key] = {
                    "playerId": str(player_to_add.id),
                    "slotType": "auto", # ╨в╨╕╨┐ ╤Б╨╗╨╛╤В╨░ ╨╜╨╡ ╨╕╨╖╨▓╨╡╤Б╤В╨╡╨╜, ╤Б╤В╨░╨▓╨╕╨╝ ╨░╨▓╤В╨╛
                    "slotLabel": f"AUTO_{slot_key}",
                    "playerPosition": player_to_add.position
                }
                used_player_ids.add(player_to_add.id) # ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨╜╨░ ╨▓╤Б╤П╨║╨╕╨╣ ╤Б╨╗╤Г╤З╨░╨╣
                filler_idx += 1
            else:
                return None # ╨Ю╤И╨╕╨▒╨║╨░ ╨▓ ╨╗╨╛╨│╨╕╨║╨╡

    # ╨д╨╕╨╜╨░╨╗╤М╨╜╨░╤П ╨┐╤А╨╛╨▓╨╡╤А╨║╨░
    if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
        return final_lineup
    else:
        return None # ╨Э╨╡ ╤Г╨┤╨░╨╗╨╛╤Б╤М ╤Б╨╛╨▒╤А╨░╤В╤М 11 ╨╕╨│╤А╨╛╨║╨╛╨▓ ╨╕╨╗╨╕ ╨║╨╗╤О╤З╨╕ ╨╜╨╡ 0-10


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches(match_ids: Optional[Iterable[int]] = None):
    """
    Переводит матчи из scheduled в in_progress и копирует/дополняет составы команд.
    Если переданы match_ids, запускает только выбранные матчи.
    """
    now = timezone.now()

    matches_to_process = Match.objects.filter(status='scheduled', datetime__lte=now)
    if match_ids:
        matches_to_process = matches_to_process.filter(id__in=match_ids)

    started_count = 0
    skipped_count = 0

    for match in matches_to_process:
        try:
            with transaction.atomic():
                match_locked = Match.objects.select_for_update().get(pk=match.pk)
                if match_locked.status != 'scheduled' or match_locked.datetime > timezone.now():
                    skipped_count += 1
                    continue

                final_home_lineup = None
                final_away_lineup = None
                home_tactic = 'balanced'
                away_tactic = 'balanced'

                home_data_from_club = match_locked.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(home_data_from_club, dict) or 'lineup' not in home_data_from_club:
                    home_data_from_club = {"lineup": {}, "tactic": "balanced"}

                home_lineup_from_club = home_data_from_club.get('lineup', {})
                home_tactic = home_data_from_club.get('tactic', 'balanced')

                if isinstance(home_lineup_from_club, dict) and len(home_lineup_from_club) >= 11 and all(str(i) in home_lineup_from_club for i in range(11)):
                    final_home_lineup = home_lineup_from_club
                else:
                    completed_home = complete_lineup(match_locked.home_team, home_lineup_from_club)
                    if completed_home is None:
                        skipped_count += 1
                        continue
                    final_home_lineup = completed_home

                away_data_from_club = match_locked.away_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(away_data_from_club, dict) or 'lineup' not in away_data_from_club:
                    away_data_from_club = {"lineup": {}, "tactic": "balanced"}

                away_lineup_from_club = away_data_from_club.get('lineup', {})
                away_tactic = away_data_from_club.get('tactic', 'balanced')

                if isinstance(away_lineup_from_club, dict) and len(away_lineup_from_club) >= 11 and all(str(i) in away_lineup_from_club for i in range(11)):
                    final_away_lineup = away_lineup_from_club
                else:
                    completed_away = complete_lineup(match_locked.away_team, away_lineup_from_club)
                    if completed_away is None:
                        skipped_count += 1
                        continue
                    final_away_lineup = completed_away

                if final_home_lineup and final_away_lineup:
                    match_locked.home_lineup = final_home_lineup
                    match_locked.home_tactic = home_tactic
                    match_locked.away_lineup = final_away_lineup
                    match_locked.away_tactic = away_tactic
                    match_locked.status = 'in_progress'
                    now_ts = timezone.now()
                    match_locked.started_at = now_ts
                    match_locked.last_minute_update = now_ts
                    match_locked.waiting_for_next_minute = False
                    match_locked.save()
                    started_count += 1
                else:
                    skipped_count += 1
                    continue

        except Match.DoesNotExist:
            skipped_count += 1
        except OperationalError:
            skipped_count += 1
        except Exception:
            skipped_count += 1

    return f"{started_count} matches started, {skipped_count} skipped."

@shared_task(name='tournaments.advance_match_minutes')
def advance_match_minutes():
    """Advance match minutes based on real elapsed time."""
    now = timezone.now()
    matches = Match.objects.filter(status='in_progress')
    if not matches:
        return 'No matches to update'

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from django.core.cache import cache

    channel_layer = get_channel_layer()

    for match in matches:
        if match.last_minute_update is None:
            match.last_minute_update = now
            match.save(update_fields=["last_minute_update"])
            continue

        if not match.waiting_for_next_minute:
            continue

        elapsed = (now - match.last_minute_update).total_seconds()
        if elapsed < settings.MATCH_MINUTE_REAL_SECONDS:
            continue

        if match.current_minute < 90:
            match.current_minute += 1
            # info_event removed to reduce clutter

            if channel_layer:
                possessing_team_id = None
                if match.possession_indicator == 1:
                    possessing_team_id = str(match.home_team_id)
                elif match.possession_indicator == 2:
                    possessing_team_id = str(match.away_team_id)

                payload = {
                    "type": "match_update",
                    "data": {
                        "match_id": match.id,
                        "minute": match.current_minute,
                        "home_score": match.home_score,
                        "away_score": match.away_score,
                        "status": match.status,
                        "st_shoots": match.st_shoots,
                        "st_passes": match.st_passes,
                        "st_possessions": match.st_possessions,
                        "st_fouls": match.st_fouls,
                        "st_injury": match.st_injury,
                        "home_momentum": match.home_momentum,
                        "away_momentum": match.away_momentum,
                        "current_zone": match.current_zone,
                        "possessing_team_id": possessing_team_id,
                        "events": [],  # No event for minute transition
                        "partial_update": True,
                        "action_based": True,
                    },
                }

                async_to_sync(channel_layer.group_send)(
                    f"match_{match.id}",
                    payload,
                )

        cache.delete(f"match_{match.id}_actions_in_minute")
        match.waiting_for_next_minute = False
        match.last_minute_update = match.last_minute_update + timedelta(
            seconds=settings.MATCH_MINUTE_REAL_SECONDS
        )
        match.save()

    return f'Updated {matches.count()} matches'

# --- ╨Ъ╨Ю╨Э╨Х╨ж ╨д╨Р╨Щ╨Ы╨Р tournaments/tasks.py ---
