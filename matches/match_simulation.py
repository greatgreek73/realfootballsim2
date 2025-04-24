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

def send_update(match, possessing_team):
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
        "st_shoots": match.st_shoots,
        "st_passes": match.st_passes,
        "st_posessions": match.st_posessions,
        "st_fouls": match.st_fouls,
        "st_injury": match.st_injury,
        "status": match.status,
        "players": choose_players(possessing_team, 'GK'),
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
    # commented cause : make sure after failed shot the ball might end with any of team member
    # condition = zone_conditions(zone)
    # candidates = [p for p in team.player_set.all() if condition(p) and p.id not in exclude_ids]
    # if candidates:
    #     return random.choice(candidates)
    candidates = [p for p in team.player_set.all() if p.id not in exclude_ids]
    if candidates:
        return random.choice(candidates)
    return None

def choose_players(team: Club, zone: str, exclude_ids: set = None):
    """
    Выбирает случайного игрока из команды, удовлетворяющего условию для зоны.
    Если кандидатов нет, возвращает случайного игрока (с исключением exclude_ids).
    """
    if exclude_ids is None:
        exclude_ids = set()
    # commented cause : make sure after failed shot the ball might end with any of team member
    # condition = zone_conditions(zone)
    # candidates = [p for p in team.player_set.all() if condition(p) and p.id not in exclude_ids]
    # if candidates:
    #     return random.choice(candidates)
    candidates = [p for p in team.player_set.all() if p.id not in exclude_ids]
    return candidates

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

def process_injury(match):
    match.status = 'paused'
    shot_miss_desc = (f"Match paused.")
    MatchEvent.objects.create(
        match=match,
        minute=match.current_minute,
        event_type='match_paused',
        description=shot_miss_desc
        )
    logger.info(shot_miss_desc)
    return

def decrease_stamina(team, player, val):
    return

def increase_stamina(team, player, val):
    return

def decrease_morale(team, player, val):
    return

def increase_morale(team, player, val):
    return

def simulate_one_minute(match):
    """
    Симулирует одну минуту матча, создавая события и обновляя состояние.
    """
    PASS_SUCCESS_PROB = 0.6
    SHOT_SUCCESS_PROB = 0.15
    # BALL_OUT_PROB = 0.6
    BOUNCE_PROB = 0.7
    FOUL_PROB = 0.15
    INJURY_PROB = 0.3
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
            decrease_stamina('all', 'all', 1)

            # Определяем владеющую команду
            if match.current_player_with_ball:
                if match.current_player_with_ball in match.home_team.player_set.all():
                    possessing_team = match.home_team
                    match.current_posses = 1
                else:
                    possessing_team = match.away_team
                    match.current_posses = 2
            else:
                possessing_team = match.home_team
                match.current_posses = 1
                starting_player = choose_player(match.home_team, "GK")
                match.current_player_with_ball = starting_player
                match.st_posessions += 1

            # Создаем событие начала минуты
            start_event_desc = f"Entering minutes {minute} of game: Team {possessing_team} starting to attack."
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
                if random.random() < FOUL_PROB:
                    match.st_fouls += 1
                    #To DO : process foul
                    if random.random() < INJURY_PROB:
                        match.st_injury += 1
                        process_injury(match)
                        decrease_morale(possessing_team, 'all', 1)
                    
                if match.current_zone != "FWD":
                    target_zone = transition_map.get(match.current_zone, match.current_zone)
                    match.st_posessions += 1
                    if random.random() < PASS_SUCCESS_PROB:
                        new_player = choose_player(possessing_team, target_zone,
                            exclude_ids={match.current_player_with_ball.id} if match.current_player_with_ball else set())
                        if new_player:
                            match.st_passes += 1
                            pass_event_desc = (f"Successfull pass from: {match.current_player_with_ball.first_name if match.current_player_with_ball else 'Unknown'} "
                                               f"to player {new_player.first_name} {new_player.last_name} in zone {target_zone}.")
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
                        intercept_desc = (f"Interception! {interceptor.first_name} {interceptor.last_name} from team {opponent_team} "
                                          f"Ball intercepted in zone {match.current_zone}.")
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
                    match.st_shoots += 1
                    if random.random() < SHOT_SUCCESS_PROB:
                        if possessing_team == match.home_team:
                            match.home_score += 1
                        else:
                            match.away_score += 1
                        shooter = match.current_player_with_ball
                        shot_event_desc = (f"Goal! {shooter.first_name} {shooter.last_name} for team {possessing_team} "
                                           f"scores a goal in {minute} minute!")
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
                        shot_miss_desc = (f"Missed a shot! {shooter.first_name} {shooter.last_name} lost a shot at {minute} minute.")
                        MatchEvent.objects.create(
                            match=match,
                            minute=minute,
                            event_type='shot_miss',
                            player=shooter,
                            description=shot_miss_desc
                        )
                        logger.info(shot_miss_desc)
                    if random.random() < BOUNCE_PROB:
                        bounced_team = possessing_team
                    else:
                        bounced_team = get_opponent_team(match, possessing_team)
                    new_owner = choose_player(bounced_team, "GK")
                    match.current_player_with_ball = new_owner
                    match.current_zone = "GK"
                    # match.save()
                    send_update(match, possessing_team)
                    break

                send_update(match, possessing_team)

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

def passed_time(match, t):
    if match.current_posses ==1:
        possesing_team = match.home_team
    else:
        possesing_team = match.away_team
    if t >0 and t <31:
        decrease_stamina(possesing_team,'',10)
    if t >30 and t <41:
        decrease_stamina(possesing_team,'',8)
    if t >40 and t <51:
        decrease_stamina(possesing_team,'',5)
    if t >50 and t <61:
        decrease_stamina(possesing_team,'',3)
    if t >60 and t <71:
        decrease_stamina(possesing_team,'',2)
    if t >70 and t <81:
        decrease_stamina(possesing_team,'',1)
    if t >80 and t <91:
        decrease_stamina(possesing_team,'',0.5)
    if t >90 and t <101:
        decrease_stamina(possesing_team,'',0.2)
    return

def change_all_morale_value():
    return

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
                logger.warning(f"simulate_match: match {match.id} not in status scheduled => bypassing.")
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
            if match.status == 'paused':
                time.sleep(5)  #wait for user action
                match.status = 'in_progress'
            passed_time(match, _)
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

        logger.info(f"simulate_match({match_id}) finished: {match.home_score}-{match.away_score}")

    except Match.DoesNotExist:
        logger.error(f"simulate_match: матч {match_id} не найден.")
    except Exception as e:
        logger.error(f"simulate_match({match_id}) => {str(e)}")
        raise
