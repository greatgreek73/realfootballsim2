# Файл match_simulation.py

import random
import logging
from django.db import transaction # Убедитесь, что импорт есть, если будете использовать транзакции внутри
from django.utils import timezone
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
import time
# Для рассылки обновлений через WebSocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def serialize_player(p: Player):
    """Сериализует данные игрока для отправки."""
    if not p:
        return None
    return {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "position": p.position,
        # "overall": p.overall_rating # Раскомментировать при необходимости
    }

# --- ИЗМЕНЕННАЯ ФУНКЦИЯ send_update (без events, с st_possessions) ---
def send_update(match, possessing_team):
    """Отправляет обновление состояния матча (БЕЗ списка событий) через WebSocket."""
    try:
        # --- БЛОК ПОЛУЧЕНИЯ И ФОРМИРОВАНИЯ events_data УДАЛЕН ---

        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Cannot get channel layer. Updates will not be sent.")
            return

        # Получаем текущего игрока и его данные
        current_player = match.current_player_with_ball
        current_player_data = serialize_player(current_player)

        # --- ИСПОЛЬЗУЕМ 'st_possessions' (две 's') ---
        update_data = {
            "type": "match_update", # Важно для consumer.py
            "data": {
                "match_id": match.id,
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "st_shoots": match.st_shoots,
                "st_passes": match.st_passes,
                "st_possessions": match.st_possessions, # <--- Используем правильное имя
                "st_fouls": match.st_fouls,
                "st_injury": match.st_injury,
                "status": match.status,
                "current_player": current_player_data,
                "current_zone": match.current_zone,
                "possessing_team_id": possessing_team.id if possessing_team else None,
                # Ключ "events" УДАЛЕН из отправляемых данных
            }
        }
        # ------------------------------------------

        # Отправляем асинхронно
        async_to_sync(channel_layer.group_send)(
            f"match_{match.id}",
            update_data
        )
    except AttributeError as e:
        # Ловим AttributeError отдельно, если поле еще не применилось миграцией
        if 'st_possessions' in str(e):
             logger.error(f"Error accessing st_possessions for match {match.id}. Did migrations run? Error: {e}")
        else:
             logger.error(f"AttributeError sending update for match {match.id}: {e}")
             # Возможно, стоит перевыбросить ошибку, чтобы увидеть полный traceback
             # raise e 
    except Exception as e:
        logger.error(f"Error sending update for match {match.id}: {e}")


# --- Вспомогательные функции ---
def zone_conditions(zone: str):
    """
    Возвращает функцию-предикат для проверки, подходит ли игрок для указанной зоны.
    """
    zone_upper = zone.upper() # Приводим к верхнему регистру для надежности
    if zone_upper == "GK":
        return lambda p: p.position == "Goalkeeper"
    elif zone_upper == "DEF":
        return lambda p: "Back" in p.position or "Defender" in p.position or p.position == "CB" or p.position == "LB" or p.position == "RB"
    elif zone_upper in ["DM", "MID"]:
        return lambda p: ("Midfielder" in p.position and "Defensive" in p.position) or p.position == "CM"
    elif zone_upper == "AM":
        return lambda p: ("Midfielder" in p.position and "Attacking" in p.position) or p.position == "CAM"
    elif zone_upper == "WING":
         return lambda p: p.position in ["LW", "RW", "LM", "RM"]
    elif zone_upper == "FWD":
        return lambda p: "Forward" in p.position or "Striker" in p.position or p.position == "ST" or p.position == "CF"
    else: # 'ANY' или неизвестная зона
        return lambda p: True 

def choose_player(team: Club, zone: str, exclude_ids: set = None) -> Player | None:
    """
    Выбирает случайного игрока из команды для указанной зоны.
    """
    if not team:
         logger.error("choose_player called with None team")
         return None
    if exclude_ids is None: 
        exclude_ids = set()

    try:
        players = team.player_set.all() 
    except Exception as e:
        logger.error(f"Failed to get players for team {team.id} in choose_player: {e}")
        return None
        
    available_players = [p for p in players if p.id not in exclude_ids]

    if not available_players:
        # logger.warning(f"No available players in team {team.name} (excluding {exclude_ids}) for zone {zone}")
        return None

    candidates = []
    if zone != "ANY": 
        condition = zone_conditions(zone)
        candidates = [p for p in available_players if condition(p)]

    if candidates: 
        return random.choice(candidates)
    elif available_players: 
        # logger.debug(f"No players found for zone '{zone}' in team {team.name}, choosing any.")
        return random.choice(available_players)
    else: 
        return None

def choose_players(team: Club, zone: str, exclude_ids: set = None) -> list[Player]:
    """
    Выбирает ВСЕХ игроков команды, удовлетворяющих условию для зоны.
    """
    if not team:
        logger.error("choose_players called with None team")
        return []
    if exclude_ids is None: 
        exclude_ids = set()
        
    try:
        players = team.player_set.all()
        condition = zone_conditions(zone)
        candidates = [p for p in players if condition(p) and p.id not in exclude_ids]
        return candidates
    except Exception as e:
        logger.error(f"Failed to get players for choose_players (team {team.id}): {e}")
        return []

def get_opponent_team(match: Match, possessing_team: Club) -> Club:
    """Возвращает команду-соперника."""
    if not possessing_team: 
         logger.warning(f"get_opponent_team called with None possessing_team for match {match.id}. Returning home team.")
         return match.home_team 
    return match.away_team if possessing_team.id == match.home_team.id else match.home_team

def auto_select_lineup(club: Club) -> dict | None:
    """
    Пытается сгенерировать автосостав через complete_lineup.
    """
    try:
        from tournaments.tasks import complete_lineup 
        logger.info(f"Attempting to auto-select lineup for club {club.name} (ID: {club.id})")
        generated_lineup_dict = complete_lineup(club, {}) 
        if generated_lineup_dict:
            logger.info(f"Auto-selected lineup for {club.name} generated.")
            return {"lineup": generated_lineup_dict, "tactic": "balanced"} 
        else:
            logger.warning(f"complete_lineup returned None for {club.name}.")
            return None 
    except ImportError:
        logger.error("Could not import complete_lineup from tournaments.tasks. Auto selection failed.")
        return None
    except Exception as e:
        logger.exception(f"Error during auto-selection for {club.name}: {e}")
        return None

def ensure_match_lineup_set(match: Match, for_home: bool) -> bool:
    """
    Проверяет и устанавливает состав команды в матче.
    """
    team = match.home_team if for_home else match.away_team
    lineup_attr = 'home_lineup' if for_home else 'away_lineup'
    tactic_attr = 'home_tactic' if for_home else 'away_tactic'

    club_data = team.lineup 
    club_lineup = {}
    club_tactic = 'balanced'

    if isinstance(club_data, dict):
        club_lineup = club_data.get('lineup', {})
        club_tactic = club_data.get('tactic', 'balanced')

    is_complete = (
        isinstance(club_lineup, dict) and
        len(club_lineup) >= 11 and
        all(str(i) in club_lineup for i in range(11)) # Проверяем ключи 0-10
    )

    if is_complete:
        logger.info(f"Using existing complete lineup from club {team.name} for match {match.id}")
        setattr(match, lineup_attr, club_lineup)
        setattr(match, tactic_attr, club_tactic)
        return True
    else:
        logger.warning(f"Lineup from club {team.name} incomplete/invalid for match {match.id}. Attempting completion/auto-selection...")
        try:
            from tournaments.tasks import complete_lineup
            completed_lineup_dict = complete_lineup(team, club_lineup if isinstance(club_lineup, dict) else {}) 

            if completed_lineup_dict:
                logger.info(f"Successfully completed/generated lineup for {team.name} for match {match.id}")
                setattr(match, lineup_attr, completed_lineup_dict)
                setattr(match, tactic_attr, club_tactic) 
                return True
            else:
                logger.error(f"Failed to complete/generate lineup for {team.name} (ID: {team.id}). Match {match.id} cannot start correctly.")
                return False 
        except ImportError:
             logger.error(f"Could not import complete_lineup from tournaments.tasks for {team.name}. Auto completion failed.")
             return False
        except Exception as e:
             logger.exception(f"Error during lineup completion for {team.name}: {e}")
             return False

# Функции-заглушки
def process_injury(match): logger.warning(f"Injury processing not implemented for match {match.id}")
def decrease_stamina(team, player, val): pass
def increase_stamina(team, player, val): pass
def decrease_morale(team, player, val): pass
def increase_morale(team, player, val): pass


# --- ОСНОВНАЯ ФУНКЦИЯ СИМУЛЯЦИИ МИНУТЫ ---
def simulate_one_minute(match: Match) -> Match | None:
    """
    Симулирует одну минуту матча.
    Возвращает обновленный объект match или текущий в случае ошибки.
    Предполагается, что match.save() будет вызван ВНЕ этой функции.
    """
    PASS_SUCCESS_PROB = 0.65 
    SHOT_SUCCESS_PROB = 0.18 
    BOUNCE_PROB = 0.60 
    FOUL_PROB = 0.12 
    INJURY_PROB = 0.05 
    GK_PASS_SUCCESS_PROB = 0.10 
    GK_INTERCEPTION_SHOT_SUCCESS_PROB = 0.90
    transition_map = {"GK": "DEF", "DEF": "DM", "DM": "MID", "MID":"AM", "AM": "FWD"} 

    try:
        # Проверки статуса и времени матча
        if match.status != 'in_progress':
             logger.debug(f"simulate_one_minute: match {match.id} status '{match.status}', skipping.")
             return match
        if match.current_minute >= 90:
             if match.status != 'finished':
                 logger.info(f"Match {match.id} reached 90 mins, finishing.")
                 match.status = 'finished'
                 send_update(match, match.home_team)
             return match 

        minute = match.current_minute + 1
        logger.debug(f"--- Simulating Minute {minute} for Match {match.id} ---")
        
        # Определение владения
        current_player = match.current_player_with_ball
        possessing_team = None
        if current_player:
            if current_player.club_id == match.home_team_id: possessing_team = match.home_team
            elif current_player.club_id == match.away_team_id: possessing_team = match.away_team
            else: current_player = None 
        if not current_player: 
            possessing_team = match.home_team
            current_player = choose_player(possessing_team, "GK")
            if not current_player: 
                 logger.error(f"Match {match.id}: Home team {possessing_team.name} has no GK!"); match.status = 'error'; return match 
            match.current_player_with_ball = current_player
            match.current_zone = "GK"
            match.st_possessions += 1 # Используем правильное имя поля
            logger.info(f"Match {match.id} min {minute}: Possession reset to home GK {current_player}.")
        match.current_posses = 1 if possessing_team.id == match.home_team.id else 2

        # Событие начала минуты
        start_event_desc = (f"Minute {minute}: Team '{possessing_team.name}' starts with ball. "
                            f"{current_player.first_name} {current_player.last_name} in {match.current_zone}.")
        MatchEvent.objects.create(match=match, minute=minute, event_type='info', description=start_event_desc, player=current_player)
        logger.info(start_event_desc)
        send_update(match, possessing_team) # Отправляем ТОЛЬКО состояние

        minute_action_resolved = False

        # --- ЛОГИКА ВРАТАРЯ ---
        if match.current_zone == "GK":
            logger.info(f"Match {match.id} Min {minute}: GK ({current_player.last_name}) action.")
            gk_player = current_player
            opponent_team = get_opponent_team(match, possessing_team)
            if random.random() < GK_PASS_SUCCESS_PROB: # Пас успешен (10%)
                target_zone = "DEF"
                recipient = choose_player(possessing_team, target_zone, exclude_ids={gk_player.id})
                if recipient:
                    match.st_passes += 1
                    pass_desc = f"GK {gk_player.last_name} passes to Defender {recipient.last_name}."
                    MatchEvent.objects.create(match=match, minute=minute, event_type='pass', player=gk_player, related_player=recipient, description=pass_desc)
                    logger.info(pass_desc)
                    match.current_player_with_ball = recipient; match.current_zone = target_zone
                    send_update(match, possessing_team)
                    minute_action_resolved = True 
                else: # Не найден защитник
                     logger.warning(f"Match {match.id} Min {minute}: GK pass ok, no defender found!")
                     any_player = choose_player(possessing_team, "ANY", exclude_ids={gk_player.id})
                     if any_player: match.current_player_with_ball = any_player; match.current_zone = "DEF"; logger.info(f"Ball to {any_player.last_name}"); send_update(match, possessing_team); minute_action_resolved = True
                     else: logger.error(f"Match {match.id} Min {minute}: No players for {possessing_team.name}!"); minute_action_resolved = False 
            else: # Пас перехвачен (90%)
                interceptor = choose_player(opponent_team, "FWD") 
                if interceptor:
                    intercept_desc = f"INTERCEPTION! GK {gk_player.last_name} pass intercepted by {interceptor.last_name} ({opponent_team.name})!"
                    MatchEvent.objects.create(match=match, minute=minute, event_type='interception', player=interceptor, related_player=gk_player, description=intercept_desc)
                    logger.info(intercept_desc)
                    match.current_player_with_ball = interceptor; possessing_team = opponent_team; match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                    send_update(match, possessing_team) 
                    # Удар
                    logger.info(f"Match {match.id} Min {minute}: {interceptor.last_name} immediate shot!")
                    match.st_shoots += 1; shooter = interceptor
                    is_goal = random.random() < GK_INTERCEPTION_SHOT_SUCCESS_PROB
                    if is_goal: # Гол
                        if possessing_team.id == match.home_team.id: match.home_score += 1
                        else: match.away_score += 1
                        goal_desc = f"GOAL!!! Interception! {shooter.first_name} {shooter.last_name} ({possessing_team.name}) scores! Score: {match.home_score}-{match.away_score}"
                        MatchEvent.objects.create(match=match, minute=minute, event_type='goal', player=shooter, description=goal_desc)
                        logger.info(goal_desc); send_update(match, possessing_team) 
                    else: # Промах
                        miss_desc = f"Missed! {shooter.first_name} {shooter.last_name} fails after interception."
                        MatchEvent.objects.create(match=match, minute=minute, event_type='shot_miss', player=shooter, description=miss_desc)
                        logger.info(miss_desc); send_update(match, possessing_team) 
                    # Сброс
                    reset_team = get_opponent_team(match, possessing_team) 
                    new_owner = choose_player(reset_team, "GK")
                    if new_owner:
                        match.current_player_with_ball = new_owner; match.current_zone = "GK"; possessing_team = reset_team 
                        match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                        logger.info(f"Match {match.id} Min {minute}: Ball resets to GK {new_owner.last_name} ({reset_team.name}).")
                    else: # Аварийный сброс
                         match.current_player_with_ball = choose_player(match.home_team, "GK"); match.current_zone = "GK"; possessing_team = match.home_team; match.current_posses = 1
                         logger.error(f"Match {match.id} Min {minute}: No GK for {reset_team.name}. Reset home GK.")
                    send_update(match, possessing_team) 
                    minute_action_resolved = True 
                else: logger.warning(f"Match {match.id} Min {minute}: GK pass intercepted, no FWD found."); minute_action_resolved = False

        # --- ОБЩИЙ ЦИКЛ СОБЫТИЙ ---
        if not minute_action_resolved:
            subevents = 3 
            for i in range(subevents):
                 if match.status != 'in_progress': break 
                 current_player = match.current_player_with_ball
                 if not current_player: 
                      match.current_player_with_ball = choose_player(match.home_team, "GK"); match.current_zone = "GK"; possessing_team = match.home_team; match.current_posses = 1
                      logger.error(f"Match {match.id} Min {minute}: Lost player! Resetting."); send_update(match, possessing_team)
                      break 
                 logger.debug(f"Sub-event {i+1}: Player {current_player.last_name}, Zone {match.current_zone}")

                 # Фол
                 if random.random() < FOUL_PROB:
                     match.st_fouls += 1
                     opponent_team = get_opponent_team(match, possessing_team); fouler = choose_player(opponent_team, "ANY"); fouled = current_player
                     if fouler and fouled:
                          foul_desc = f"Foul! {fouler.last_name} ({opponent_team.name}) on {fouled.last_name} in {match.current_zone}."
                          MatchEvent.objects.create(match=match, minute=minute, event_type='foul', player=fouler, related_player=fouled, description=foul_desc)
                          logger.info(foul_desc)
                          if random.random() < INJURY_PROB:
                              match.st_injury += 1; injury_desc = f"Injury concern for {fouled.last_name}!"
                              MatchEvent.objects.create(match=match, minute=minute, event_type='injury_concern', player=fouled, description=injury_desc)
                              logger.warning(injury_desc)
                          send_update(match, possessing_team) 

                 # Пас или Удар
                 if match.current_zone != "FWD": # Пас
                     target_zone = transition_map.get(match.current_zone, match.current_zone)
                     # --- ИСПОЛЬЗУЕМ 'st_possessions' (две 's') ---
                     match.st_possessions += 1 # <--- ИЗМЕНЕНО ЗДЕСЬ
                     # ------------------------------------------

                     if random.random() < PASS_SUCCESS_PROB: # Успешный пас
                         recipient = choose_player(possessing_team, target_zone, exclude_ids={current_player.id})
                         if recipient:
                             match.st_passes += 1
                             pass_desc = f"Pass: {current_player.last_name} -> {recipient.last_name} ({match.current_zone}->{target_zone})"
                             MatchEvent.objects.create(match=match, minute=minute, event_type='pass', player=current_player, related_player=recipient, description=pass_desc)
                             logger.info(pass_desc)
                             match.current_player_with_ball = recipient; match.current_zone = target_zone
                             send_update(match, possessing_team)
                         else: logger.warning(f"Match {match.id} Min {minute}: Pass OK, no player in {target_zone}.")
                     else: # Перехват
                         opponent_team = get_opponent_team(match, possessing_team); interceptor = choose_player(opponent_team, match.current_zone) 
                         if interceptor:
                             intercept_desc = f"INTERCEPTION! {interceptor.last_name} ({opponent_team.name}) from {current_player.last_name} in {match.current_zone}."
                             MatchEvent.objects.create(match=match, minute=minute, event_type='interception', player=interceptor, related_player=current_player, description=intercept_desc)
                             logger.info(intercept_desc)
                             new_gk = choose_player(opponent_team, "GK")
                             if not new_gk: match.current_player_with_ball = interceptor; match.current_zone = "DEF" 
                             else: match.current_player_with_ball = new_gk; match.current_zone = "GK"
                             possessing_team = opponent_team
                             match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                             send_update(match, possessing_team) 
                             break # Смена владения
                         else: logger.warning(f"Match {match.id} Min {minute}: Pass failed, no interceptor. Ball out?"); break 
                 else: # Удар (зона FWD)
                     match.st_shoots += 1; shooter = current_player
                     is_goal = random.random() < SHOT_SUCCESS_PROB
                     if is_goal: # Гол
                         if possessing_team.id == match.home_team.id: match.home_score += 1
                         else: match.away_score += 1
                         goal_desc = f"GOAL!!! {shooter.first_name} {shooter.last_name} ({possessing_team.name})! Score: {match.home_score}-{match.away_score}"
                         MatchEvent.objects.create(match=match, minute=minute, event_type='goal', player=shooter, description=goal_desc)
                         logger.info(goal_desc); send_update(match, possessing_team) 
                     else: # Промах
                         miss_desc = f"Missed shot by {shooter.first_name} {shooter.last_name} ({possessing_team.name})."
                         MatchEvent.objects.create(match=match, minute=minute, event_type='shot_miss', player=shooter, description=miss_desc)
                         logger.info(miss_desc); send_update(match, possessing_team) 
                     # Сброс мяча
                     reset_team = get_opponent_team(match, possessing_team) 
                     new_owner = choose_player(reset_team, "GK")
                     if new_owner:
                         match.current_player_with_ball = new_owner; match.current_zone = "GK"; possessing_team = reset_team
                         match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                         logger.info(f"Match {match.id} Min {minute}: Ball resets to GK {new_owner.last_name} ({reset_team.name}).")
                     else: # Аварийный сброс
                          match.current_player_with_ball = choose_player(match.home_team, "GK"); match.current_zone = "GK"; possessing_team = match.home_team; match.current_posses = 1
                          logger.error(f"Match {match.id} Min {minute}: No GK for {reset_team.name}. Reset home GK.")
                     send_update(match, possessing_team) 
                     break # Выход из subevents после удара

        # --- Завершение минуты ---
        match.current_minute = minute
        if match.current_minute >= 90 and match.status != 'finished':
             match.status = 'finished'
             logger.info(f"Match {match.id} FINAL MINUTE {minute}. Finishing.")
             send_update(match, possessing_team if possessing_team else match.home_team) # Финальное обновление состояния

        logger.debug(f"--- Minute {minute} simulation ended for Match {match.id} ---")

        # --- ИЗМЕНЕНО: Вызов задачи Celery РАСКОММЕНТИРОВАН ---
        try:
            # Импорт внутри функции, чтобы избежать проблем с циклическим импортом при запуске
            from .tasks import broadcast_minute_events_in_chunks 
            broadcast_minute_events_in_chunks.delay(match.id, minute, duration=10) 
            logger.debug(f"Scheduled broadcast task for match {match.id}, minute {minute}")
        except ImportError:
             logger.error("Could not import broadcast_minute_events_in_chunks from .tasks. Event broadcasting skipped.")
        except Exception as celery_e:
             logger.exception(f"Error scheduling broadcast task for match {match.id}: {celery_e}")
        # -------------------------------------------------------

        return match 

    # Обработка ЛЮБОЙ ошибки внутри основной симуляции минуты
    except Exception as e:
        # Логируем полную ошибку с traceback
        logger.exception(f"!!! CRITICAL Error in simulate_one_minute for match {match.id} at minute {match.current_minute + 1}: {e}")
        # Можно установить статус матча в 'error', чтобы остановить его симуляцию
        # match.status = 'error' 
        # match.save() # Если меняем статус, нужно сохранить
        return match # Возвращаем текущий объект match, чтобы внешний цикл мог продолжить или остановиться

# Конец файла match_simulation.py