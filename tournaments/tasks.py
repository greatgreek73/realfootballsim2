# tournaments/tasks.py

import time
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.conf import settings
from django.core.management import call_command
from matches.models import Match, MatchEvent
from players.models import Player # ╨г╨▒╨╡╨┤╨╕╤В╨╡╤Б╤М, ╤З╤В╨╛ ╨╕╨╝╨┐╨╛╤А╤В ╨╡╤Б╤В╤М
from clubs.models import Club     # ╨г╨▒╨╡╨┤╨╕╤В╨╡╤Б╤М, ╤З╤В╨╛ ╨╕╨╝╨┐╨╛╤А╤В ╨╡╤Б╤В╤М
from .models import Season, Championship, League
import random # ╨г╨▒╨╡╨┤╨╕╤В╨╡╤Б╤М, ╤З╤В╨╛ ╨╕╨╝╨┐╨╛╤А╤В ╨╡╤Б╤В╤М
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("match_creation")


@shared_task(name='tournaments.simulate_active_matches', bind=True)
def simulate_active_matches(self):
    """
    ╨Я╨╛╤И╨░╨│╨╛╨▓╨░╤П ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╤П ╨╝╨░╤В╤З╨╡╨╣ - ╤В╨╡╨┐╨╡╤А╤М ╨┐╨╛ ╨Ф╨Х╨Щ╨б╨в╨Т╨Ш╨п╨Ь, ╨░ ╨╜╨╡ ╨┐╨╛ ╨╝╨╕╨╜╤Г╤В╨░╨╝.
    ╨Ч╨░╨┐╤Г╤Б╨║╨░╨╡╤В╤Б╤П ╨┐╨╡╤А╨╕╨╛╨┤╨╕╤З╨╡╤Б╨║╨╕ (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А, ╨║╨░╨╢╨┤╤Л╨╡ 2 ╤Б╨╡╨║╤Г╨╜╨┤╤Л).
    """
    now = timezone.now()
    logger.info(f"ЁЯФБ [simulate_active_matches] ╨Ч╨░╨┐╤Г╤Б╨║ ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕ ╨░╨║╤В╨╕╨▓╨╜╤Л╤Е ╨╝╨░╤В╤З╨╡╨╣ ╨▓ {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("ЁЯФН ╨Э╨╡╤В ╨╝╨░╤В╤З╨╡╨╣ ╤Б╨╛ ╤Б╤В╨░╤В╤Г╤Б╨╛╨╝ 'in_progress'.")
        return "No matches in progress"

    logger.info(f"тЬЕ ╨Э╨░╨╣╨┤╨╡╨╜╨╛ {matches.count()} ╨╝╨░╤В╤З╨╡╨╣ ╨┤╨╗╤П ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕.")

    from matches.match_simulation import simulate_one_action, send_update
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from django.core.cache import cache
    
    channel_layer = get_channel_layer()

    for match in matches:
        try:
            logger.info(f"ЁЯФТ ╨Я╨╛╨┐╤Л╤В╨║╨░ ╨▒╨╗╨╛╨║╨╕╤А╨╛╨▓╨║╨╕ ╨╝╨░╤В╤З╨░ ID={match.id} ╨┤╨╗╤П ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕...")

            with transaction.atomic():
                match_locked = Match.objects.select_for_update().get(id=match.id)

                # ╨Ш╨╜╨╕╤Ж╨╕╨░╨╗╨╕╨╖╨╕╤А╤Г╨╡╨╝ ╨▓╤А╨╡╨╝╤П ╨╜╨░╤З╨░╨╗╨░ ╨╕ ╨┐╨╛╤Б╨╗╨╡╨┤╨╜╨╡╨│╨╛ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╤П, ╨╡╤Б╨╗╨╕ ╨╜╨╡ ╤Г╤Б╤В╨░╨╜╨╛╨▓╨╗╨╡╨╜╤Л
                if match_locked.started_at is None:
                    match_locked.started_at = timezone.now()
                    match_locked.save(update_fields=['started_at'])
                    logger.info(f"тЬЕ ╨г╤Б╤В╨░╨╜╨╛╨▓╨╗╨╡╨╜╨╛ ╨▓╤А╨╡╨╝╤П ╨╜╨░╤З╨░╨╗╨░ ╨┤╨╗╤П ╨╝╨░╤В╤З╨░ ID={match_locked.id}")

                if match_locked.last_minute_update is None:
                    match_locked.last_minute_update = timezone.now()
                    match_locked.save(update_fields=['last_minute_update'])
                    logger.info(f"тЬЕ ╨г╤Б╤В╨░╨╜╨╛╨▓╨╗╨╡╨╜╨╛ ╨▓╤А╨╡╨╝╤П ╨┐╨╛╤Б╨╗╨╡╨┤╨╜╨╡╨│╨╛ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╤П ╨┤╨╗╤П ╨╝╨░╤В╤З╨░ ID={match_locked.id}")

                # ╨Х╤Б╨╗╨╕ ╨╛╨╢╨╕╨┤╨░╨╡╨╝ ╨╜╨░╤З╨░╨╗╨░ ╤Б╨╗╨╡╨┤╤Г╤О╤Й╨╡╨╣ ╨╝╨╕╨╜╤Г╤В╤Л, ╨┐╤А╨╛╨┐╤Г╤Б╨║╨░╨╡╨╝ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╤Г
                if match_locked.waiting_for_next_minute:
                    logger.info(
                        f"тПня╕П ╨Ь╨░╤В╤З ID={match_locked.id} ╨╢╨┤╤С╤В ╤Б╨╗╨╡╨┤╤Г╤О╤Й╤Г╤О ╨╝╨╕╨╜╤Г╤В╤Г, ╨┐╤А╨╛╨┐╤Г╤Б╨║."
                    )
                    continue
                
                # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ ╤Б╤З╨╡╤В╤З╨╕╨║ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣ ╨╕╨╖ ╨║╨╡╤И╨░
                cache_key = f"match_{match_locked.id}_actions_in_minute"
                actions_in_current_minute = cache.get(cache_key, 0)
                
                # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝, ╨╜╨╡ ╨╖╨░╨║╨╛╨╜╤З╨╕╨╗╤Б╤П ╨╗╨╕ ╨╝╨░╤В╤З
                if match_locked.current_minute >= 90:
                    match_locked.status = 'finished'
                    match_locked.save()
                    cache.delete(cache_key)  # ╨Ю╤З╨╕╤Й╨░╨╡╨╝ ╨║╨╡╤И
                    logger.info(f"ЁЯПБ ╨Ь╨░╤В╤З ID={match_locked.id} ╨╖╨░╨▓╨╡╤А╤И╨╡╨╜")
                    continue
                
                # ╨б╨╕╨╝╤Г╨╗╨╕╤А╤Г╨╡╨╝ ╨╛╨┤╨╜╨╛ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡
                logger.info(
                    f"тЪЩя╕П ╨б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╤П ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П ╨┤╨╗╤П ╨╝╨░╤В╤З╨░ ID={match_locked.id}, "
                    f"╨╝╨╕╨╜╤Г╤В╨░ {match_locked.current_minute}, ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡ #{actions_in_current_minute + 1}"
                )
                
                result = simulate_one_action(match_locked)

                possessing_team_id = None
                if match_locked.possession_indicator == 1:
                    possessing_team_id = str(match_locked.home_team_id)
                elif match_locked.possession_indicator == 2:
                    possessing_team_id = str(match_locked.away_team_id)

                # ╨Х╤Б╨╗╨╕ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡ ╨╖╨░╨▓╨╡╤А╤И╨░╨╡╤В ╨░╤В╨░╨║╤Г, ╨╢╨┤╤С╨╝ ╤Б╨╗╨╡╨┤╤Г╤О╤Й╨╡╨╣ ╨╝╨╕╨╜╤Г╤В╤Л
                if result.get('continue', True) is False:
                    match_locked.waiting_for_next_minute = True
                
                
                # ╨б╨╛╨╖╨┤╨░╨╡╨╝ ╤Б╨╛╨▒╤Л╤В╨╕╨╡, ╨╡╤Б╨╗╨╕ ╨╛╨╜╨╛ ╨╡╤Б╤В╤М
                if result.get('event'):
                    event = MatchEvent.objects.create(**result['event'])
                    logger.info(
                        f"тЬЕ ╨Ф╨╡╨╣╤Б╤В╨▓╨╕╨╡ ╤Б╨╛╨╖╨┤╨░╨╜╨╛: {result['action_type']} "
                        f"╨┤╨╗╤П ╨╝╨░╤В╤З╨░ ID={match_locked.id}"
                    )
                    
                    # ╨Ю╤В╨┐╤А╨░╨▓╨╗╤П╨╡╨╝ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ ╨б╨а╨Р╨Ч╨г ╤З╨╡╤А╨╡╨╖ WebSocket
                    if channel_layer:
                        event_data = {
                            "minute": event.minute,
                            "event_type": event.event_type,
                            "description": event.description,
                            "personality_reason": event.personality_reason,
                            "player_name": f"{event.player.first_name} {event.player.last_name}" if event.player else "",
                            "related_player_name": f"{event.related_player.first_name} {event.related_player.last_name}" if event.related_player else ""
                        }

                        
                        message_payload = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
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
                                "events": [event_data],
                                "partial_update": True,
                                "action_based": True  # ╨Э╨╛╨▓╤Л╨╣ ╤Д╨╗╨░╨│ ╨┤╨╗╤П ╨┐╨╛╤И╨░╨│╨╛╨▓╨╛╨╣ ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕
                            }
                        }
                        
                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            message_payload
                        )
                        
                        logger.info(
                            f"ЁЯУб ╨б╨╛╨▒╤Л╤В╨╕╨╡ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜╨╛ ╤З╨╡╤А╨╡╨╖ WebSocket ╨┤╨╗╤П ╨╝╨░╤В╤З╨░ ID={match_locked.id}"
                        )
                
                # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨┤╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А, ╤В╤А╨░╨▓╨╝╨░ ╨┐╨╛╤Б╨╗╨╡ ╤Д╨╛╨╗╨░)
                if result.get('additional_event'):
                    add_event = MatchEvent.objects.create(**result['additional_event'])
                    # ╨Ю╤В╨┐╤А╨░╨▓╨╗╤П╨╡╨╝ ╨╕ ╨╡╨│╨╛ ╤З╨╡╤А╨╡╨╖ WebSocket
                    if channel_layer:
                        add_event_data = {
                            "minute": add_event.minute,
                            "event_type": add_event.event_type,
                            "description": add_event.description,
                            "personality_reason": add_event.personality_reason,
                            "player_name": f"{add_event.player.first_name} {add_event.player.last_name}" if add_event.player else "",
                            "related_player_name": ""
                        }
                        
                        add_message_payload = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
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
                                "events": [add_event_data],
                                "partial_update": True,
                                "action_based": True
                            }
                        }
                        
                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload
                        )

                # ╨Ю╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╨╝ ╨▓╤В╨╛╤А╨╛╨╡ ╨┤╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А, ╤Г╨┤╨░╤А ╨┐╨╛╤Б╨╗╨╡ ╨┐╨╡╤А╨╡╤Е╨▓╨░╤В╨░)
                if result.get('second_additional_event'):
                    add_event2 = MatchEvent.objects.create(**result['second_additional_event'])
                    if channel_layer:
                        add_event_data2 = {
                            "minute": add_event2.minute,
                            "event_type": add_event2.event_type,
                            "description": add_event2.description,
                            "personality_reason": add_event2.personality_reason,
                            "player_name": f"{add_event2.player.first_name} {add_event2.player.last_name}" if add_event2.player else "",
                            "related_player_name": ""
                        }

                        add_message_payload2 = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
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
                                "events": [add_event_data2],
                                "partial_update": True,
                                "action_based": True
                            }
                        }

                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload2
                        )

                # ╨Ю╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╨╝ ╤В╤А╨╡╤В╤М╨╡ ╨┤╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╤Б╨╛╨▒╤Л╤В╨╕╨╡
                if result.get('third_additional_event'):
                    add_event3 = MatchEvent.objects.create(**result['third_additional_event'])
                    if channel_layer:
                        add_event_data3 = {
                            "minute": add_event3.minute,
                            "event_type": add_event3.event_type,
                            "description": add_event3.description,
                            "personality_reason": add_event3.personality_reason,
                            "player_name": f"{add_event3.player.first_name} {add_event3.player.last_name}" if add_event3.player else "",
                            "related_player_name": ""
                        }

                        add_message_payload3 = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
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
                                "events": [add_event_data3],
                                "partial_update": True,
                                "action_based": True
                            }
                        }

                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload3
                        )

                # ╨Х╤Б╨╗╨╕ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ ╨╜╨╡ ╤Б╨╛╨╖╨┤╨░╨╜╨╛, ╨╛╤В╨┐╤А╨░╨▓╨╗╤П╨╡╨╝ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡ ╤Б╨╛╤Б╤В╨╛╤П╨╜╨╕╤П
                if result.get('event') is None:
                    possessing_team = None
                    player_with_ball = match_locked.current_player_with_ball
                    if player_with_ball:
                        if player_with_ball.club_id == match_locked.home_team_id:
                            possessing_team = match_locked.home_team
                        elif player_with_ball.club_id == match_locked.away_team_id:
                            possessing_team = match_locked.away_team
                    send_update(match_locked, possessing_team)
                
                # ╨г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╨╝ ╤Б╤З╨╡╤В╤З╨╕╨║ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣
                actions_in_current_minute += 1
                cache.set(cache_key, actions_in_current_minute, timeout=300)  # 5 ╨╝╨╕╨╜╤Г╤В ╤В╨░╨╣╨╝╨░╤Г╤В
                
                # ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╤Б╨╛╤Б╤В╨╛╤П╨╜╨╕╨╡ ╨╝╨░╤В╤З╨░
                match_locked.save()

        except Match.DoesNotExist:
            logger.warning(f"тЭМ ╨Ь╨░╤В╤З ID={match.id} ╨╕╤Б╤З╨╡╨╖ ╨╕╨╖ ╨▒╨░╨╖╤Л ╨▓╨╛ ╨▓╤А╨╡╨╝╤П ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕.")
        except OperationalError as e:
            logger.error(f"ЁЯФТ ╨Ю╤И╨╕╨▒╨║╨░ ╨▒╨╗╨╛╨║╨╕╤А╨╛╨▓╨║╨╕ ╨▒╨░╨╖╤Л ╨┤╨░╨╜╨╜╤Л╤Е ╨┤╨╗╤П ╨╝╨░╤В╤З╨░ {match.id}: {e}")
        except Exception as e:
            logger.exception(f"ЁЯФе ╨Ю╤И╨╕╨▒╨║╨░ ╨┐╤А╨╕ ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕ ╨╝╨░╤В╤З╨░ {match.id}: {e}")

    return f"Simulated actions for {matches.count()} matches"



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
def start_scheduled_matches():
    """
    ╨Я╨╡╤А╨╡╨▓╨╛╨┤╨╕╤В ╨╝╨░╤В╤З╨╕ ╨╕╨╖ scheduled ╨▓ in_progress ╨╕ ╨║╨╛╨┐╨╕╤А╤Г╨╡╤В/╨┤╨╛╨┐╨╛╨╗╨╜╤П╨╡╤В ╤Б╨╛╤Б╤В╨░╨▓╤Л ╨║╨╛╨╝╨░╨╜╨┤.
    """
    now = timezone.now()

    # ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝ transaction.atomic ╨┤╨╗╤П ╨║╨░╨╢╨┤╨╛╨╣ ╨║╨╛╨╝╨░╨╜╨┤╤Л ╨╛╤В╨┤╨╡╨╗╤М╨╜╨╛,
    # ╤З╤В╨╛╨▒╤Л ╨╛╤И╨╕╨▒╨║╨░ ╨▓ ╨╛╨┤╨╜╨╛╨╣ ╨╜╨╡ ╨╛╤В╨║╨░╤В╤Л╨▓╨░╨╗╨░ ╨┤╤А╤Г╨│╨╕╨╡.
    matches_to_process = Match.objects.filter(
        status='scheduled',
        datetime__lte=now
    )
    started_count = 0
    skipped_count = 0

    for match in matches_to_process:
        try:
            with transaction.atomic():
                # ╨С╨╗╨╛╨║╨╕╤А╤Г╨╡╨╝ ╨╝╨░╤В╤З ╨╜╨░ ╨▓╤А╨╡╨╝╤П ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╕
                match_locked = Match.objects.select_for_update().get(pk=match.pk)

                # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╤Б╤В╨░╤В╤Г╤Б ╨╡╤Й╨╡ ╤А╨░╨╖ ╨▓╨╜╤Г╤В╤А╨╕ ╤В╤А╨░╨╜╨╖╨░╨║╤Ж╨╕╨╕, ╨▓╨┤╤А╤Г╨│ ╨╛╨╜ ╨╕╨╖╨╝╨╡╨╜╨╕╨╗╤Б╤П
                if match_locked.status != 'scheduled' or match_locked.datetime > timezone.now():
                    skipped_count += 1
                    continue

                final_home_lineup = None
                final_away_lineup = None
                home_tactic = 'balanced'
                away_tactic = 'balanced'

                # --- ╨Ю╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╨╝ ╨┤╨╛╨╝╨░╤И╨╜╤О╤О ╨║╨╛╨╝╨░╨╜╨┤╤Г ---
                home_data_from_club = match_locked.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(home_data_from_club, dict) or 'lineup' not in home_data_from_club:
                     home_data_from_club = {"lineup": {}, "tactic": "balanced"}

                home_lineup_from_club = home_data_from_club.get('lineup', {})
                home_tactic = home_data_from_club.get('tactic', 'balanced')

                if isinstance(home_lineup_from_club, dict) and len(home_lineup_from_club) >= 11 and all(str(i) in home_lineup_from_club for i in range(11)):
                     # ╨Х╤Б╨╗╨╕ ╤Б╨╛╤Б╤В╨░╨▓ ╨▓ ╨║╨╗╤Г╨▒╨╡ ╤Г╨╢╨╡ ╨┐╨╛╨╗╨╜╤Л╨╣ (11 ╨╕╨│╤А╨╛╨║╨╛╨▓, ╨║╨╗╤О╤З╨╕ 0-10), ╨┐╤А╨╛╤Б╤В╨╛ ╨▒╨╡╤А╨╡╨╝ ╨╡╨│╨╛
                     final_home_lineup = home_lineup_from_club
                else:
                     # ╨Х╤Б╨╗╨╕ ╤Б╨╛╤Б╤В╨░╨▓ ╨╜╨╡╨┐╨╛╨╗╨╜╤Л╨╣ ╨╕╨╗╨╕ ╨╜╨╡╨║╨╛╤А╤А╨╡╨║╤В╨╜╤Л╨╣, ╨┐╤Л╤В╨░╨╡╨╝╤Б╤П ╨┤╨╛╨┐╨╛╨╗╨╜╨╕╤В╤М
                     completed_home = complete_lineup(match_locked.home_team, home_lineup_from_club)
                     if completed_home is None:
                         skipped_count += 1
                         continue # ╨Я╤А╨╛╨┐╤Г╤Б╨║╨░╨╡╨╝ ╤Н╤В╨╛╤В ╨╝╨░╤В╤З, ╨╛╤В╨║╨░╤В╤Л╨▓╨░╨╡╨╝ ╤В╤А╨░╨╜╨╖╨░╨║╤Ж╨╕╤О ╨┤╨╗╤П ╨╜╨╡╨│╨╛
                     final_home_lineup = completed_home

                # --- ╨Ю╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╨╝ ╨│╨╛╤Б╤В╨╡╨▓╤Г╤О ╨║╨╛╨╝╨░╨╜╨┤╤Г (╨░╨╜╨░╨╗╨╛╨│╨╕╤З╨╜╨╛) ---
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
                         continue # ╨Я╤А╨╛╨┐╤Г╤Б╨║╨░╨╡╨╝ ╤Н╤В╨╛╤В ╨╝╨░╤В╤З
                     final_away_lineup = completed_away

                # --- ╨Х╤Б╨╗╨╕ ╨╛╨▒╨░ ╤Б╨╛╤Б╤В╨░╨▓╨░ ╨│╨╛╤В╨╛╨▓╤Л, ╤Б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╨╕ ╨╝╨╡╨╜╤П╨╡╨╝ ╤Б╤В╨░╤В╤Г╤Б ---
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
                    # ╨н╤В╨░ ╨▓╨╡╤В╨║╨░ ╨╜╨╡ ╨┤╨╛╨╗╨╢╨╜╨░ ╤Б╤А╨░╨▒╨╛╤В╨░╤В╤М, ╨╡╤Б╨╗╨╕ continue ╨▓╤Л╤И╨╡ ╨╛╤В╤А╨░╨▒╨╛╤В╨░╨╗╨╕ ╨┐╤А╨░╨▓╨╕╨╗╤М╨╜╨╛
                    skipped_count += 1
                    continue

        except Match.DoesNotExist:
             skipped_count += 1
        except OperationalError as e_lock:
             skipped_count += 1
        except Exception as e_match:
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
            info_event = MatchEvent.objects.create(
                match=match,
                minute=match.current_minute,
                event_type="info",
                description=f"Minute {match.current_minute}: Play continues...",
            )

            if channel_layer:
                info_event_data = {
                    "minute": info_event.minute,
                    "event_type": info_event.event_type,
                    "description": info_event.description,
                    "player_name": "",
                    "related_player_name": "",
                }

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
                        "events": [info_event_data],
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
