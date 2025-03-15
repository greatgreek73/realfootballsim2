import random
import logging
from django.db import transaction
from django.utils import timezone
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
import time
# Для рассылки обновлений через WebSocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def send_update(match):
    recent_events_qs = match.events.all().order_by('-id')[:5]
    recent_events = list(reversed(recent_events_qs))
    events_data = []
    for e in recent_events:
        events_data.append({
            "minute": e.minute,
            "event_type": e.event_type,
            "description": e.description,
            "player": f"{e.player.first_name} {e.player.last_name}" if e.player else ""
        })
    channel_layer = get_channel_layer()
    update_data = {
        "minute": match.current_minute,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "status": match.status,
        "events": events_data,
    }
    async_to_sync(channel_layer.group_send)(
        f"match_{match.id}",
        {
            "type": "match_update",
            "data": update_data
        }
    )

def zone_conditions(zone: str):
    """
    Возвращает функцию-предикат для проверки, подходит ли игрок для указанной зоны.
    """
    if zone == "GK":
        return lambda p: p.position == "Goalkeeper"
    elif zone == "DEF":
        return lambda p: "Back" in p.position or "Defender" in p.position
    elif zone in ["DM", "AM"]:
        return lambda p: "Midfielder" in p.position
    elif zone == "FWD":
        return lambda p: "Forward" in p.position
    else:
        return lambda p: True

def choose_player(team: Club, zone: str, exclude_ids: set = None) -> Player:
    """
    Выбирает случайного игрока из команды, удовлетворяющего условию для зоны.
    Если кандидатов нет, возвращает случайного игрока (с исключением exclude_ids).
    """
    if exclude_ids is None:
        exclude_ids = set()
    condition = zone_conditions(zone)
    candidates = [p for p in team.player_set.all() if condition(p) and p.id not in exclude_ids]
    if candidates:
        return random.choice(candidates)
    candidates = [p for p in team.player_set.all() if p.id not in exclude_ids]
    if candidates:
        return random.choice(candidates)
    return None

def get_opponent_team(match: Match, possessing_team: Club) -> Club:
    """
    Возвращает противоположную команду для данной.
    """
    return match.away_team if possessing_team == match.home_team else match.home_team

def auto_select_lineup(club: Club) -> dict:
    """
    Простейшая автогенерация состава (4-4-2).
    Возвращает словарь вида:
      {
        "lineup": {
          "0": {"playerId": "123", "slotType": "goalkeeper", "slotLabel": "GK"},
          ...
        },
        "tactic": "balanced"
      }
    Если у клуба менее 11 игроков, возвращает пустой состав.
    """
    players = list(club.player_set.all())
    if len(players) < 11:
        return {"lineup": {}, "tactic": "balanced"}
    gk = next((p for p in players if p.position == "Goalkeeper"), None)
    if not gk:
        gk = players[0]
    used_ids = {gk.id}
    defenders = [p for p in players if ("Back" in p.position or "Defender" in p.position) and p.id not in used_ids][:4]
    used_ids.update(d.id for d in defenders)
    midfielders = [p for p in players if "Midfielder" in p.position and p.id not in used_ids][:4]
    used_ids.update(m.id for m in midfielders)
    forwards = [p for p in players if "Forward" in p.position and p.id not in used_ids][:2]
    used_ids.update(f.id for f in forwards)
    lineup_dict = {}
    lineup_dict["0"] = {"playerId": str(gk.id), "slotType": "goalkeeper", "slotLabel": "GK"}
    slot_index = 1
    for d in defenders:
        lineup_dict[str(slot_index)] = {"playerId": str(d.id), "slotType": "defender", "slotLabel": f"DEF{slot_index}"}
        slot_index += 1
    for m in midfielders:
        lineup_dict[str(slot_index)] = {"playerId": str(m.id), "slotType": "midfielder", "slotLabel": f"MID{slot_index}"}
        slot_index += 1
    for f in forwards:
        lineup_dict[str(slot_index)] = {"playerId": str(f.id), "slotType": "forward", "slotLabel": f"FWD{slot_index}"}
        slot_index += 1
    return {"lineup": lineup_dict, "tactic": "balanced"}

def ensure_match_lineup_set(match: Match, for_home: bool) -> None:
    """
    Проверяет, есть ли у команды состав (в поле team.lineup).
    Если отсутствует или состав неполный (<11 игроков), генерирует автосостав.
    """
    team = match.home_team if for_home else match.away_team
    club_lineup = team.lineup
    if (not club_lineup or not isinstance(club_lineup, dict) or
        "lineup" not in club_lineup or len(club_lineup["lineup"]) < 11):
        new_lineup = auto_select_lineup(team)
        if for_home:
            match.home_lineup = new_lineup
        else:
            match.away_lineup = new_lineup
    else:
        if for_home:
            match.home_lineup = club_lineup
        else:
            match.away_lineup = club_lineup

def simulate_one_minute(match):
    """
    Симулирует одну минуту матча, создавая события и обновляя состояние.
    """
    PASS_SUCCESS_PROB = 0.6
    SHOT_SUCCESS_PROB = 0.15
    transition_map = {"GK": "DEF", "DEF": "DM", "DM": "AM", "AM": "FWD"}

    try:
        with transaction.atomic():
            # Получаем матч и проверяем его статус
            # match = Match.objects.select_for_update().get(id=match_id)
            if match.status != 'in_progress':
                logger.debug(f"simulate_one_minute: матч {match.id} не в процессе, пропускаем.")
                return match
            if match.current_minute >= 90:
                match.status = 'finished'
                # match.save()
                return match

            minute = match.current_minute + 1

            # Определяем владеющую команду
            if match.current_player_with_ball:
                if match.current_player_with_ball in match.home_team.player_set.all():
                    possessing_team = match.home_team
                else:
                    possessing_team = match.away_team
            else:
                possessing_team = match.home_team
                starting_player = choose_player(match.home_team, "GK")
                match.current_player_with_ball = starting_player

            # Создаем событие начала минуты
            start_event_desc = f"Начало минуты {minute}: команда {possessing_team} начинает атаку."
            MatchEvent.objects.create(
                match=match,
                minute=minute,
                event_type='info',
                description=start_event_desc
            )
            logger.info(start_event_desc)
            send_update(match)

            # Симулируем события минуты
            subevents = 3
            for i in range(subevents):
                if match.current_zone != "FWD":
                    target_zone = transition_map.get(match.current_zone, match.current_zone)
                    if random.random() < PASS_SUCCESS_PROB:
                        new_player = choose_player(possessing_team, target_zone,
                            exclude_ids={match.current_player_with_ball.id} if match.current_player_with_ball else set())
                        if new_player:
                            pass_event_desc = (f"Пас успешен: {match.current_player_with_ball.first_name if match.current_player_with_ball else 'Unknown'} "
                                               f"передаёт мяч {new_player.first_name} {new_player.last_name} в зону {target_zone}.")
                            MatchEvent.objects.create(
                                match=match,
                                minute=minute,
                                event_type='pass',
                                player=match.current_player_with_ball,
                                description=pass_event_desc
                            )
                            logger.info(pass_event_desc)
                            match.current_player_with_ball = new_player
                            match.current_zone = target_zone
                            # match.save()
                        else:
                            raise Exception("Не удалось найти игрока для паса.")
                    else:
                        opponent_team = get_opponent_team(match, possessing_team)
                        interceptor = choose_player(opponent_team, match.current_zone)
                        intercept_desc = (f"Перехват! {interceptor.first_name} {interceptor.last_name} из команды {opponent_team} "
                                          f"перехватывает мяч в зоне {match.current_zone}.")
                        MatchEvent.objects.create(
                            match=match,
                            minute=minute,
                            event_type='interception',
                            player=interceptor,
                            description=intercept_desc
                        )
                        logger.info(intercept_desc)
                        match.current_player_with_ball = interceptor
                        match.current_zone = "GK"
                        match.save()
                        send_update(match)
                        break
                else:
                    if random.random() < SHOT_SUCCESS_PROB:
                        if possessing_team == match.home_team:
                            match.home_score += 1
                        else:
                            match.away_score += 1
                        shooter = match.current_player_with_ball
                        shot_event_desc = (f"Успешный удар! {shooter.first_name} {shooter.last_name} из команды {possessing_team} "
                                           f"забивает гол на {minute} минуте!")
                        MatchEvent.objects.create(
                            match=match,
                            minute=minute,
                            event_type='goal',
                            player=shooter,
                            description=shot_event_desc
                        )
                        logger.info(shot_event_desc)
                    else:
                        shooter = match.current_player_with_ball
                        shot_miss_desc = (f"Удар промахнулся! {shooter.first_name} {shooter.last_name} не реализует шанс на {minute} минуте.")
                        MatchEvent.objects.create(
                            match=match,
                            minute=minute,
                            event_type='shot_miss',
                            player=shooter,
                            description=shot_miss_desc
                        )
                        logger.info(shot_miss_desc)
                    opponent_team = get_opponent_team(match, possessing_team)
                    new_owner = choose_player(opponent_team, "GK")
                    match.current_player_with_ball = new_owner
                    match.current_zone = "GK"
                    # match.save()
                    send_update(match)
                    break

                send_update(match)

            # Обновляем минуту и проверяем завершение матча
            match.current_minute = minute
            if match.current_minute >= 90:
                match.status = 'finished'
            # match.save()
            
            # Запускаем трансляцию событий в Celery-задаче
            from .tasks import broadcast_minute_events_in_chunks
            broadcast_minute_events_in_chunks.delay(match.id, minute, duration=5)
            return match

    except Match.DoesNotExist:
        logger.error(f"simulate_one_minute: матч {match.id} не найден.")
    except Exception as e:
        logger.error(f"simulate_one_minute({match.id}) => {str(e)}")
        raise

def simulate_match(match_id: int):
    """
    Полная симуляция матча (от 0 до 90 минут) в реальном времени.
    Каждая игровая минута длится 60 секунд, а внутриминутные события с интервалом в 10 секунд.
    Если match.status == 'scheduled', инициализирует составы, счёт, минуту, статус 'in_progress',
    устанавливает начальное владение (вратарь домашней команды, зона GK) и запускает симуляцию минуты за минутой.
    Если после 90 минут матч не завершён, устанавливает статус 'finished' и current_minute=90.
    """
    try:
        with transaction.atomic():
            match = Match.objects.select_for_update().get(id=match_id)
            if match.status != 'scheduled':
                logger.warning(f"simulate_match: матч {match.id} не в статусе scheduled => пропускаем.")
                return
            ensure_match_lineup_set(match, True)
            ensure_match_lineup_set(match, False)
            match.home_score = 0
            match.away_score = 0
            match.current_minute = 0
            match.status = 'in_progress'
            starting_player = choose_player(match.home_team, "GK")
            match.current_player_with_ball = starting_player
            match.current_zone = "GK"
            match.save()
            send_update(match)

        for _ in range(90):
            match = simulate_one_minute(match)
            match.save()
            match.refresh_from_db()
            if match.status == 'finished':
                break

        if match.status != 'finished':
            with transaction.atomic():
                match = Match.objects.select_for_update().get(id=match_id)
                match.status = 'finished'
                match.current_minute = 90
                match.save()
                send_update(match)

        logger.info(f"simulate_match({match_id}) завершён: {match.home_score}-{match.away_score}")

    except Match.DoesNotExist:
        logger.error(f"simulate_match: матч {match_id} не найден.")
    except Exception as e:
        logger.error(f"simulate_match({match_id}) => {str(e)}")
        raise
