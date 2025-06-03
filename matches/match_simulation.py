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
from matches.utils import extract_player_id

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
        # Defensive/Central midfielders. The initial logic only handled
        # "Defensive Midfielder" or the short "CM" abbreviation which meant
        # players registered as "Central Midfielder" were ignored. When no
        # candidates matched the zone the function would fall back to choosing
        # any available player – sometimes even the goalkeeper.  Include the
        # full position names so a proper recipient is always found.
        return lambda p: (
            p.position in ["Defensive Midfielder", "Central Midfielder", "CM"]
            or ("Midfielder" in p.position and "Defensive" in p.position)
        )
    elif zone_upper == "AM":
        return lambda p: ("Midfielder" in p.position and "Attacking" in p.position) or p.position == "CAM"
    elif zone_upper == "WING":
         return lambda p: p.position in ["LW", "RW", "LM", "RM"]
    elif zone_upper == "FWD":
        return lambda p: "Forward" in p.position or "Striker" in p.position or p.position == "ST" or p.position == "CF"
    else: # 'ANY' или неизвестная зона
        return lambda p: True 

def choose_player(team: Club, zone: str, exclude_ids: set = None, match: Match = None) -> Player | None:
    """
    Выбирает случайного игрока из стартового состава команды для указанной зоны.
    """
    if not team or not match:
        logger.error("choose_player called with None team or None match")
        return None
    if exclude_ids is None:
        exclude_ids = set()

    # Определяем, какой состав использовать
    lineup = match.home_lineup if team.id == match.home_team_id else match.away_lineup
    if not lineup:
        logger.error(f"No lineup found for team {team.name} in match {match.id}")
        return None

    # Получаем id игроков из состава (корректно извлекаем id даже если это dict)
    lineup_player_ids = []
    for slot, player_val in lineup.items():
        player_id = extract_player_id(player_val)
        if player_id:
            try:
                lineup_player_ids.append(int(player_id))
            except Exception:
                continue
    try:
        all_players = team.player_set.all()
        lineup_players = [p for p in all_players if p.id in lineup_player_ids]
        available_players = [p for p in lineup_players if p.id not in exclude_ids]

        if not available_players:
            return None

        candidates = []
        if zone != "ANY":
            condition = zone_conditions(zone)
            candidates = [p for p in available_players if condition(p)]

        if candidates:
            # ИЗМЕНЕНИЕ: Взвешенный выбор для защитников
            if zone.upper() == "DEF":
                weights = [max(p.positioning, 0) for p in candidates]
                if any(weights):
                    return random.choices(candidates, weights=weights, k=1)[0]
            return random.choice(candidates)
        elif available_players:
            return random.choice(available_players)
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get players for team {team.id} in choose_player: {e}")
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

def decrease_stamina(team, player, val):
    pass

def increase_stamina(team, player, val):
    pass

def decrease_morale(team, player, val):
    pass

def increase_morale(team, player, val):
    pass

# --- Probability helper functions ---
def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def pass_success_probability(
    passer: Player,
    recipient: Player,
    opponent: Player | None,
    *,
    is_goalkeeper_pass: bool = False,
) -> float:
    # Slightly higher base chance so passes succeed more often, especially
    # goalkeeper distributions which were failing too frequently in practice.
    base = 0.7 if is_goalkeeper_pass else 0.6

    # Passing and vision continue to provide the main boost.  Values are in the
    # range 0-100 so the maximum bonus is around +1.0 when both stats are high.
    bonus = (passer.passing + passer.vision) / 200

    # Receiver positioning also helps.  Unpositioned passes still have a chance
    # but we favour well‑positioned targets.
    rec_bonus = recipient.positioning / 200 if recipient else 0

    penalty = 0
    if opponent:
        # Reduce the weight of defensive skills so a single opponent does not
        # negate a reasonable passing attempt quite as often.
        penalty = (opponent.marking + opponent.tackling) / 400
    stamina_factor = passer.stamina / 100
    morale_factor = 0.5 + passer.morale / 200
    return clamp((base + bonus + rec_bonus - penalty) * stamina_factor * morale_factor)


def shot_success_probability(shooter: Player, goalkeeper: Player | None) -> float:
    base = 0.1
    bonus = (shooter.finishing + shooter.long_range + shooter.accuracy) / 300
    penalty = 0
    if goalkeeper:
        penalty = (goalkeeper.reflexes + goalkeeper.handling + goalkeeper.positioning) / 300
    stamina_factor = shooter.stamina / 100
    morale_factor = 0.5 + shooter.morale / 200
    return clamp((base + bonus - penalty) * stamina_factor * morale_factor)


def foul_probability(tackler: Player, dribbler: Player) -> float:
    base = 0.05
    diff = tackler.tackling - dribbler.dribbling
    return clamp(base + diff / 200)

def simulate_one_action(match: Match) -> dict:
    """
    Симулирует ОДНО действие в матче (пас, перехват, удар и т.д.)
    Возвращает словарь с информацией о действии и событии
    """
    # Константы вероятностей (те же, что в simulate_one_minute)
    PASS_SUCCESS_PROB = 0.65 
    SHOT_SUCCESS_PROB = 0.18 
    FOUL_PROB = 0.12 
    INJURY_PROB = 0.05 
    GK_PASS_SUCCESS_PROB = 0.90
    
    # Определяем текущее состояние
    current_player = match.current_player_with_ball
    current_zone = match.current_zone
    possessing_team = None
    
    # Определяем команду владения
    if current_player:
        if current_player.club_id == match.home_team_id:
            possessing_team = match.home_team
        elif current_player.club_id == match.away_team_id:
            possessing_team = match.away_team
    
    # Если нет текущего игрока, начинаем с вратаря домашней команды
    if not current_player or not possessing_team:
        possessing_team = match.home_team
        current_player = choose_player(possessing_team, "GK", match=match)
        if not current_player:
            return {
                'event': None,
                'action_type': 'error',
                'continue': False
            }
        match.current_player_with_ball = current_player
        match.current_zone = "GK"
    
    # Обновляем индикатор владения
    match.possession_indicator = 1 if possessing_team.id == match.home_team_id else 2
    
    
    # Основная логика действия в зависимости от зоны
    if current_zone == "FWD":
        # Зона атаки - удар по воротам
        match.st_shoots += 1
        shooter = current_player
        opponent_team = get_opponent_team(match, possessing_team)
        goalkeeper = choose_player(opponent_team, "GK", match=match)
        is_goal = random.random() < shot_success_probability(shooter, goalkeeper)
        
        if is_goal:
            if possessing_team.id == match.home_team_id:
                match.home_score += 1
            else:
                match.away_score += 1
            
            event_data = {
                'match': match,
                'minute': match.current_minute,
                'event_type': 'goal',
                'player': shooter,
                'description': f"GOAL!!! {shooter.first_name} {shooter.last_name} ({possessing_team.name})! Score: {match.home_score}-{match.away_score}"
            }
        else:
            event_data = {
                'match': match,
                'minute': match.current_minute,
                'event_type': 'shot_miss',
                'player': shooter,
                'description': f"Missed shot by {shooter.first_name} {shooter.last_name} ({possessing_team.name})."
            }
        
        # После удара мяч переходит к вратарю соперника
        opponent_team = get_opponent_team(match, possessing_team)
        new_keeper = choose_player(opponent_team, "GK", match=match)
        if new_keeper:
            match.current_player_with_ball = new_keeper
            match.current_zone = "GK"
        
        return {
            'event': event_data,
            'action_type': 'shot',
            'continue': False  # Конец атаки
        }
    
    else:
        # Попытка паса в следующую зону
        transition_map = {
            "GK": "DEF",
            "DEF": "DM", 
            "DM": "MID",
            "MID": "AM",
            "AM": "FWD"
        }
        
        target_zone = transition_map.get(current_zone, current_zone)
        match.st_possessions += 1
        
        recipient = choose_player(possessing_team, target_zone, exclude_ids={current_player.id}, match=match)

        opponent_team = get_opponent_team(match, possessing_team)
        opponent = choose_player(opponent_team, target_zone, match=match)
        pass_prob = pass_success_probability(
            current_player,
            recipient,
            opponent,
            is_goalkeeper_pass=current_zone == "GK",
        ) if recipient else 0

        if recipient:
            if random.random() < pass_prob:
                match.st_passes += 1

                event_data = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'pass',
                    'player': current_player,
                    'related_player': recipient,
                    'description': f"Pass: {current_player.last_name} -> {recipient.last_name} ({current_zone}->{target_zone})"
                }

                match.current_player_with_ball = recipient
                match.current_zone = target_zone

                # После паса возможен фол
                fouler = choose_player(opponent_team, "ANY", match=match)
                if fouler:
                    foul_chance = foul_probability(fouler, recipient)
                    if random.random() < foul_chance:
                        match.st_fouls += 1
                        foul_event = {
                            'match': match,
                            'minute': match.current_minute,
                            'event_type': 'foul',
                            'player': fouler,
                            'related_player': recipient,
                            'description': f"Foul! {fouler.last_name} ({opponent_team.name}) on {recipient.last_name} in {target_zone}.",
                        }
                        return {
                            'event': event_data,
                            'additional_event': foul_event,
                            'action_type': 'pass',
                            'continue': True,
                        }

                return {
                    'event': event_data,
                    'action_type': 'pass',
                    'continue': True,
                }
            else:
                # Неудачный пас и возможный перехват
                opponent_team = get_opponent_team(match, possessing_team)
                interceptor = choose_player(opponent_team, current_zone, match=match)

                # Событие попытки паса
                pass_event = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'pass',
                    'player': current_player,
                    'related_player': recipient,
                    'description': f"Pass attempt: {current_player.last_name} -> {recipient.last_name} ({current_zone}->{target_zone})",
                }

                if interceptor:
                    interception_event = {
                        'match': match,
                        'minute': match.current_minute,
                        'event_type': 'interception',
                        'player': interceptor,
                        'related_player': current_player,
                        'description': f"INTERCEPTION! {interceptor.last_name} ({opponent_team.name}) from {current_player.last_name} in {current_zone}.",
                    }

                    # Мяч переходит к перехватившему или к вратарю его команды
                    new_keeper = choose_player(opponent_team, "GK", match=match)
                    if new_keeper:
                        match.current_player_with_ball = new_keeper
                        match.current_zone = "GK"
                    else:
                        match.current_player_with_ball = interceptor
                        match.current_zone = "DEF"

                    return {
                        'event': pass_event,
                        'additional_event': interception_event,
                        'action_type': 'interception',
                        'continue': False  # Смена владения
                    }

                return {
                    'event': pass_event,
                    'action_type': 'failed_interception',
                    'continue': False
                }
        else:
            # Не нашли получателя
            return {
                'event': None,
                'action_type': 'no_recipient',
                'continue': False
            }

# Конец файла match_simulation.py