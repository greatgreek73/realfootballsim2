# Файл match_simulation.py

import random
import logging
from django.db import transaction # Убедитесь, что импорт есть, если будете использовать транзакции внутри
from django.utils import timezone
from django.conf import settings
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
import time
# Для рассылки обновлений через WebSocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from matches.utils import extract_player_id
from matches.commentary import render_comment
from matches.personality_engine import PersonalityModifier, PersonalityDecisionEngine
from matches.narrative_system import NarrativeAIEngine

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
                "home_momentum": match.home_momentum,
                "away_momentum": match.away_momentum,
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
    elif zone_upper == "DEF-L":
        return lambda p: p.position == "Left Back"
    elif zone_upper == "DEF-R":
        return lambda p: p.position == "Right Back"
    elif zone_upper == "DEF-C":
        return lambda p: p.position == "Center Back"
    elif zone_upper.startswith("DEF"):
        return lambda p: "Back" in p.position or "Defender" in p.position or p.position in ["CB", "LB", "RB"]
    elif zone_upper.startswith("DM") or zone_upper == "MID":
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
    elif zone_upper.startswith("AM"):
        return lambda p: (
            ("Midfielder" in p.position and "Attacking" in p.position)
            or p.position == "CAM"
        )
    elif zone_upper == "WING":
         return lambda p: p.position in ["LW", "RW", "LM", "RM"]
    elif zone_upper.startswith("FWD"):
        return lambda p: p.position == "Center Forward"
    else: # 'ANY' или неизвестная зона
        return lambda p: True

def mirrored_zone(zone: str, *, flip_side: bool = False) -> str:
    """Return the zone on the pitch where an opponent would most likely intercept.

    If ``flip_side`` is True the opposite flank is used when creating the mapped
    zone.
    """
    prefix = zone_prefix(zone)
    side = mirror_side(zone_side(zone)) if flip_side else zone_side(zone)
    mirror_map = {
        "GK": make_zone("FWD", "C"),
        "DEF": make_zone("FWD", side),
        "DM": make_zone("AM", side),
        "MID": make_zone("MID", side),
        "AM": make_zone("DM", side),
        "FWD": make_zone("DEF", side),
    }
    if prefix in mirror_map:
        return mirror_map[prefix]
    if prefix == "WING" or zone.upper() == "WING":
        return "WING"
    return zone

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

    # Получаем id игроков из состава (поддерживаем и строковый, и словарный формат)
    lineup_player_ids = []
    
    # Проверяем формат lineup и обрабатываем соответственно
    if isinstance(lineup, str):
        # Строковый формат: "15,23,7,2,19,14,25,1,13,21,22"
        try:
            for player_id_str in lineup.split(','):
                player_id_str = player_id_str.strip()
                if player_id_str and player_id_str.isdigit():
                    lineup_player_ids.append(int(player_id_str))
        except Exception as e:
            logger.error(f"Error parsing string lineup for team {team.name}: {e}")
    elif isinstance(lineup, dict):
        # Словарный формат: {"0": "15", "1": "23", ...}
        for slot, player_val in lineup.items():
            player_id = extract_player_id(player_val)
            if player_id:
                try:
                    lineup_player_ids.append(int(player_id))
                except Exception:
                    continue
    else:
        logger.error(f"Unsupported lineup format for team {team.name}: {type(lineup)}")
        return None
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
            # If no one fits a specific defensive side/centre zone,
            # fall back to any defender.
            if not candidates and (zone_upper := zone.upper()):
                if zone_upper in {"DEF-L", "DEF-C", "DEF-R"}:
                    def_condition = zone_conditions("DEF")
                    candidates = [p for p in available_players if def_condition(p)]

        if candidates:
            # Weighted choice by positioning for most zones. Previously this
            # only applied to defenders when the goalkeeper was passing.
            if zone_prefix(zone) in ["DEF", "DM", "MID", "AM", "FWD"]:
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

def choose_player_from_zones(team: Club, zones: list[str], *, exclude_ids: set | None = None, match: Match | None = None) -> tuple[Player | None, str | None]:
    """Iterate over ``zones`` and return the first available player and the zone used."""
    if exclude_ids is None:
        exclude_ids = set()
    for zone in zones:
        player = choose_player(team, zone, exclude_ids=exclude_ids, match=match)
        if player:
            return player, zone
    return None, None

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

# === СИСТЕМА МОРАЛИ ===

# Базовые изменения морали от событий
BASE_MORALE_EVENTS = {
    'goal_scored': +12,        # Забил гол
    'goal_conceded': -6,       # Пропустил гол (вся команда)
    'goal_conceded_gk': -10,   # Пропустил гол (вратарь)
    'assist': +8,              # Голевая передача
    'successful_pass': +1,     # Успешный пас (при цепочке 3+)
    'pass_intercepted': -3,    # Пас перехвачен
    'dribble_success': +3,     # Удачный дриблинг
    'dribble_failed': -2,      # Неудачный дриблинг
    'foul_committed': -2,      # Совершил фол
    'foul_suffered': +1,       # Пострадал от фола
    'shot_saved_gk': +5,       # Вратарь отразил удар
    'shot_miss': -4,           # Промах по воротам
    'clean_sheet': +8,         # Чистый лист (защитники + вратарь)
}

# Контекстные множители по времени матча
TIME_MULTIPLIERS = {
    (1, 30): 1.0,     # 1-30 минута: обычное влияние
    (31, 60): 1.1,    # 31-60 минута: чуть больше
    (61, 75): 1.3,    # 61-75 минута: важное время
    (76, 90): 1.6,    # 76-90 минута: решающие моменты
}

# Множители в зависимости от разности счета
SCORE_DIFFERENCE_MULTIPLIERS = {
    'equal': 1.2,           # Равный счет
    'leading_1': 0.9,       # Ведем на 1
    'leading_2+': 0.8,      # Ведем на 2+
    'trailing_1': 1.3,      # Отстаем на 1
    'trailing_2+': 1.5,     # Отстаем на 2+
}

# Множители по зонам поля
ZONE_MULTIPLIERS = {
    'GK': 0.8,          # Вратарская зона
    'DEF': 0.9,         # Защитная зона
    'DM': 1.0,          # Оборонительная средняя зона
    'MID': 1.0,         # Центр поля
    'AM': 1.1,          # Атакующая средняя зона
    'FWD': 1.2,         # Атакующая зона
}

# Позиционные модификаторы реакций на события
POSITION_MODIFIERS = {
    'Goalkeeper': {
        'goal_conceded': 2.0,        # Вратари сильнее страдают от голов
        'goal_conceded_gk': 1.0,     # Базовый множитель для своих голов
        'shot_saved_gk': 1.5,        # Больше радуются сейвам
        'clean_sheet': 2.0,          # Очень ценят чистые листы
        'default': 0.5,              # Слабо реагируют на общие события
    },
    'Center Back': {
        'goal_conceded': 1.5,        # Защитники тоже страдают от голов
        'successful_pass': 0.8,      # Меньше радуются пасам
        'clean_sheet': 1.8,          # Ценят чистые листы
        'default': 1.0,
    },
    'Right Back': {
        'goal_conceded': 1.3,
        'successful_pass': 0.9,
        'clean_sheet': 1.5,
        'default': 1.0,
    },
    'Left Back': {
        'goal_conceded': 1.3,
        'successful_pass': 0.9,
        'clean_sheet': 1.5,
        'default': 1.0,
    },
    'Defensive Midfielder': {
        'successful_pass': 1.2,      # Полузащитники любят пасы
        'pass_intercepted': 1.2,     # И расстраиваются от потерь
        'assist': 1.1,
        'default': 1.0,
    },
    'Central Midfielder': {
        'successful_pass': 1.3,      # Полузащитники любят пасы
        'pass_intercepted': 1.2,     # И расстраиваются от потерь
        'assist': 1.2,               # Ценят голевые передачи
        'default': 1.0,
    },
    'Right Midfielder': {
        'successful_pass': 1.2,
        'assist': 1.3,
        'default': 1.0,
    },
    'Left Midfielder': {
        'successful_pass': 1.2,
        'assist': 1.3,
        'default': 1.0,
    },
    'Attacking Midfielder': {
        'goal_scored': 1.3,
        'assist': 1.4,
        'successful_pass': 1.2,
        'default': 1.0,
    },
    'Center Forward': {
        'goal_scored': 1.5,          # Нападающие живут голами
        'assist': 1.3,               # И передачами
        'shot_miss': 1.3,            # Сильно расстраиваются от промахов
        'default': 1.0,
    },
}

# Настройки восстановления морали
RECOVERY_SETTINGS = {
    'recovery_rate': 0.8,             # Восстановление за минуту
    'max_deviation': 25,              # Максимальное отклонение от базы
    'critical_threshold': 20,         # Порог для критически низкой морали
    'excellent_threshold': 80,        # Порог для отличной морали
}

def get_time_multiplier(minute: int) -> float:
    """Возвращает множитель в зависимости от времени матча."""
    for (start, end), multiplier in TIME_MULTIPLIERS.items():
        if start <= minute <= end:
            return multiplier
    return 1.0

def get_score_multiplier(match: Match, team: Club) -> float:
    """Возвращает множитель в зависимости от разности счета."""
    home_score = match.home_score
    away_score = match.away_score
    
    if team.id == match.home_team_id:
        score_diff = home_score - away_score
    else:
        score_diff = away_score - home_score
    
    if score_diff == 0:
        return SCORE_DIFFERENCE_MULTIPLIERS['equal']
    elif score_diff == 1:
        return SCORE_DIFFERENCE_MULTIPLIERS['leading_1']
    elif score_diff >= 2:
        return SCORE_DIFFERENCE_MULTIPLIERS['leading_2+']
    elif score_diff == -1:
        return SCORE_DIFFERENCE_MULTIPLIERS['trailing_1']
    else:  # score_diff <= -2
        return SCORE_DIFFERENCE_MULTIPLIERS['trailing_2+']

def get_zone_multiplier(zone: str) -> float:
    """Возвращает множитель в зависимости от зоны поля."""
    zone_prefix_str = zone_prefix(zone)
    return ZONE_MULTIPLIERS.get(zone_prefix_str, 1.0)

def get_position_modifier(position: str, event_type: str) -> float:
    """Возвращает позиционный модификатор для события."""
    position_mods = POSITION_MODIFIERS.get(position, {})
    return position_mods.get(event_type, position_mods.get('default', 1.0))

def calculate_morale_change(player: Player, event_type: str, match: Match, zone: str = None) -> int:
    """Рассчитывает изменение морали игрока от события."""
    # Базовое изменение
    base_change = BASE_MORALE_EVENTS.get(event_type, 0)
    if base_change == 0:
        return 0
    
    # Определяем команду игрока
    if player.club_id == match.home_team_id:
        team = match.home_team
    elif player.club_id == match.away_team_id:
        team = match.away_team
    else:
        return 0
    
    # Контекстные множители
    time_mult = get_time_multiplier(match.current_minute)
    score_mult = get_score_multiplier(match, team)
    zone_mult = get_zone_multiplier(zone or match.current_zone)
    
    # Позиционный модификатор
    position_mult = get_position_modifier(player.position, event_type)
    
    # Итоговое изменение
    total_change = base_change * time_mult * score_mult * zone_mult * position_mult
    
    # Ограничение максимального изменения за событие
    return clamp_int(int(total_change), -15, +15)

def apply_morale_change(player: Player, change: int) -> None:
    """Применяет изменение морали к игроку с ограничениями."""
    if change == 0:
        return
    
    new_morale = clamp_int(player.morale + change, 0, 100)
    
    # Логирование значительных изменений
    if abs(change) >= 5:
        logger.info(f"Morale change for {player.first_name} {player.last_name}: {player.morale} -> {new_morale} ({change:+d})")
    
    player.morale = new_morale
    player.save(update_fields=['morale'])

def process_morale_event(player: Player, event_type: str, match: Match, zone: str = None) -> None:
    """Обрабатывает событие морали для игрока."""
    change = calculate_morale_change(player, event_type, match, zone)
    if change != 0:
        apply_morale_change(player, change)

def apply_team_morale_effect(team: Club, event_type: str, match: Match, exclude_player: Player = None) -> None:
    """Применяет эффект морали ко всей команде (например, при голе)."""
    try:
        # Получаем состав команды
        if team.id == match.home_team_id:
            lineup = match.home_lineup
        else:
            lineup = match.away_lineup
        
        if not lineup:
            return
        
        # Извлекаем ID игроков из состава (поддерживаем и строковый, и словарный формат)
        player_ids = []
        
        if isinstance(lineup, str):
            # Строковый формат: "15,23,7,2,19,14,25,1,13,21,22"
            try:
                for player_id_str in lineup.split(','):
                    player_id_str = player_id_str.strip()
                    if player_id_str and player_id_str.isdigit():
                        player_ids.append(int(player_id_str))
            except Exception as e:
                logger.error(f"Error parsing string lineup in apply_team_morale_effect: {e}")
        elif isinstance(lineup, dict):
            # Словарный формат: {"0": "15", "1": "23", ...}
            for slot, player_val in lineup.items():
                player_id = extract_player_id(player_val)
                if player_id:
                    try:
                        player_ids.append(int(player_id))
                    except Exception:
                        continue
        else:
            logger.error(f"Unsupported lineup format in apply_team_morale_effect: {type(lineup)}")
            return
        
        # Применяем эффект ко всем игрокам команды
        team_players = team.player_set.filter(id__in=player_ids)
        for player in team_players:
            if exclude_player and player.id == exclude_player.id:
                continue
            process_morale_event(player, event_type, match)
            
    except Exception as e:
        logger.error(f"Error applying team morale effect for team {team.id}: {e}")

def recover_morale_gradually(player: Player) -> None:
    """Постепенно восстанавливает мораль игрока к базовому уровню."""
    base_morale = player.base_morale
    current_morale = player.morale
    
    if current_morale == base_morale:
        return
    
    # Направление восстановления
    if current_morale > base_morale:
        recovery = -RECOVERY_SETTINGS['recovery_rate']
    else:
        recovery = RECOVERY_SETTINGS['recovery_rate']
    
    # Применяем восстановление
    new_morale = current_morale + recovery
    
    # Не позволяем "перескочить" базовое значение
    if (recovery > 0 and new_morale > base_morale) or (recovery < 0 and new_morale < base_morale):
        new_morale = base_morale
    
    new_morale = clamp_int(int(new_morale), 0, 100)
    
    if new_morale != current_morale:
        player.morale = new_morale
        player.save(update_fields=['morale'])

# Обновленные функции морали
def decrease_morale(team: Club, player: Player, val: int, match: Match = None):
    """Уменьшает мораль игрока (используется для совместимости)."""
    if match:
        change = -abs(val)
        apply_morale_change(player, change)

def increase_morale(team: Club, player: Player, val: int, match: Match = None):
    """Увеличивает мораль игрока (используется для совместимости)."""
    if match:
        change = abs(val)
        apply_morale_change(player, change)

# Функции-заглушки
def process_injury(match): logger.warning(f"Injury processing not implemented for match {match.id}")

def decrease_stamina(team, player, val):
    pass

def increase_stamina(team, player, val):
    pass

# --- Probability helper functions ---
def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def clamp_int(value: int, min_value: int = -100, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def update_momentum(match: Match, team: Club, delta: int) -> None:
    if team.id == match.home_team_id:
        match.home_momentum = clamp_int(match.home_momentum + delta)
    elif team.id == match.away_team_id:
        match.away_momentum = clamp_int(match.away_momentum + delta)


def get_team_momentum(match: Match, team: Club) -> int:
    if team.id == match.home_team_id:
        return match.home_momentum
    elif team.id == match.away_team_id:
        return match.away_momentum
    return 0


# --- Expanded 16 zone grid ---
ZONE_GRID = [
    "GK",
    "DEF-L", "DEF-C", "DEF-R",
    "DM-L", "DM-C", "DM-R",
    "MID-L", "MID-C", "MID-R",
    "AM-L", "AM-C", "AM-R",
    "FWD-L", "FWD-C", "FWD-R",
]

# Helper mappings to work with the grid
ROW_PREFIX = ["GK", "DEF", "DM", "MID", "AM", "FWD"]
ROW_INDEX = {p: i for i, p in enumerate(ROW_PREFIX)}
SIDES = ["L", "C", "R"]

def zone_prefix(zone: str) -> str:
    return zone.split("-")[0]

def zone_side(zone: str) -> str:
    parts = zone.split("-")
    return parts[1] if len(parts) > 1 else "C"

def mirror_side(side: str) -> str:
    """Return the opposite side (L<->R) leaving centre unchanged."""
    return {"L": "R", "R": "L", "C": "C"}.get(side, "C")

def make_zone(prefix: str, side: str) -> str:
    if prefix == "GK":
        return "GK"
    return f"{prefix}-{side}"

def random_adjacent_zone(zone: str) -> str:
    """Return a random neighbouring zone."""
    prefix = zone_prefix(zone)
    side = zone_side(zone)
    row_idx = ROW_INDEX.get(prefix, 0)
    side_idx = SIDES.index(side) if side in SIDES else 1
    adjacent: list[str] = []
    for dr in (-1, 0, 1):
        for ds in (-1, 0, 1):
            if dr == 0 and ds == 0:
                continue
            r = row_idx + dr
            if r < 0 or r >= len(ROW_PREFIX):
                continue
            if ROW_PREFIX[r] == "GK":
                candidate = "GK"
            else:
                s_idx = side_idx + ds
                if s_idx < 0 or s_idx >= len(SIDES):
                    continue
                candidate = make_zone(ROW_PREFIX[r], SIDES[s_idx])
            if candidate != zone and candidate in ZONE_GRID:
                adjacent.append(candidate)
    return random.choice(adjacent) if adjacent else zone

def forward_dribble_zone(zone: str, diag_prob: float = 0.1) -> str:
    """Return a forward zone for dribbling.

    The dribbler keeps the same side 90% of the time. With ``diag_prob``
    chance they move diagonally forward one column left or right, staying
    within bounds.
    """

    prefix = zone_prefix(zone)
    side = zone_side(zone)
    row_idx = ROW_INDEX.get(prefix, 0)
    next_idx = min(row_idx + 1, len(ROW_PREFIX) - 1)
    next_prefix = ROW_PREFIX[next_idx]

    target_side = side
    if random.random() < diag_prob:
        side_idx = SIDES.index(side) if side in SIDES else 1
        direction = random.choice([-1, 1])
        new_idx = min(max(side_idx + direction, 0), len(SIDES) - 1)
        target_side = SIDES[new_idx]

    return make_zone(next_prefix, target_side)

def next_zone(zone: str) -> str:
    """Return the next zone for a pass.

    The ball always moves forward in the same column. There is no
    sideways or backward option.
    """

    prefix = zone_prefix(zone)
    side = zone_side(zone)
    next_map = {
        "GK": "DEF",
        "DEF": "DM",
        "DM": "MID",
        "MID": "AM",
        "AM": "FWD",
        "FWD": "FWD",
    }
    return make_zone(next_map.get(prefix, prefix), side)


def pass_success_probability(
    passer: Player,
    recipient: Player,
    opponent: Player | None,
    *,
    from_zone: str,
    to_zone: str,
    high: bool = False,
    momentum: int = 0,
) -> float:
    """Return probability that a pass succeeds for a given zone transition."""
    f_prefix = zone_prefix(from_zone)
    t_prefix = zone_prefix(to_zone)
    def_base = 0.6
    # Реалистичные базовые вероятности с высокой точностью для безопасных зон
    if f_prefix == "GK" and t_prefix == "DEF":
        def_base = 0.998  # 99.8% - первый пас почти всегда успешен
    elif f_prefix == "DEF" and t_prefix == "DM":
        def_base = 0.92   # 92% - высокая надежность в своей зоне
    elif f_prefix == "DM" and t_prefix == "MID":
        def_base = 0.85   # 85% - средняя зона поля
    elif f_prefix == "MID" and t_prefix == "AM":
        def_base = 0.75   # 75% - приближение к опасной зоне
    elif f_prefix == "AM" and t_prefix == "FWD":
        def_base = 0.65   # 65% - финальная передача под давлением
    base = def_base

    if high:
        try:
            distance = ROW_INDEX[t_prefix] - ROW_INDEX[f_prefix]
        except Exception:
            distance = 1
        base -= 0.05 * max(distance - 1, 0)


    # Passing and vision continue to provide the main boost.  Values are in the
    # range 0-100 so the maximum bonus is around +1.0 when both stats are high.
    # Special handling for goalkeepers: use distribution and command instead
    if passer.position == "Goalkeeper":
        bonus = (passer.distribution + passer.command) / 200
    else:
        # Увеличиваем влияние навыков в атакующих зонах
        if f_prefix in ["AM", "FWD"]:
            # В атакующих зонах навыки имеют большее значение
            bonus = (passer.passing + passer.vision) / 150  # Увеличено с /200
        else:
            bonus = (passer.passing + passer.vision) / 200

    # Receiver positioning also helps.  Unpositioned passes still have a chance
    # but we favour well‑positioned targets.
    rec_bonus = recipient.positioning / 200 if recipient else 0
    heading_bonus = recipient.heading / 200 if high and recipient else 0

    penalty = 0
    if opponent:
        # Специальное условие для первого паса вратарь→защитник
        if f_prefix == "GK" and t_prefix == "DEF":
            # Минимальный штраф для первого паса - перехваты очень редки
            penalty = (opponent.marking + opponent.tackling) / 1200
        # Градация штрафов по зонам: меньше давления в безопасных зонах
        elif f_prefix in ["GK", "DEF"]:
            # Минимальное давление в своей половине поля
            penalty = (opponent.marking + opponent.tackling) / 800
        elif f_prefix in ["DM", "MID"]:
            # Среднее давление в центре поля
            penalty = (opponent.marking + opponent.tackling) / 500
        elif f_prefix in ["AM", "FWD"]:
            # Максимальное давление в атакующей зоне
            penalty = (opponent.marking + opponent.tackling) / 300
        else:
            # Базовое значение для других случаев
            penalty = (opponent.marking + opponent.tackling) / 400
    # Более сбалансированное влияние выносливости и морали
    stamina_factor = 0.7 + (passer.stamina / 100) * 0.3  # от 0.7 до 1.0
    
    # Специальная обработка морали для первого паса вратаря
    if f_prefix == "GK" and t_prefix == "DEF" and passer.position == "Goalkeeper":
        morale_factor = 0.95  # Высокая уверенность для первого паса
    else:
        morale_factor = 0.7 + passer.morale / 200  # от 0.7 до 1.2
    
    momentum_factor = 1 + momentum / 200
    
    # Personality modifier integration
    # Определяем тип паса для контекста
    pass_type = 'short'  # по умолчанию
    if high:
        pass_type = 'long'
    elif f_prefix in ["AM", "FWD"] and t_prefix == "FWD":
        pass_type = 'through'  # прострел в штрафную
    
    # Определяем уровень давления для контекста
    pressure_level = 0.0
    if opponent:
        if f_prefix in ["AM", "FWD"]:
            pressure_level = 0.8  # высокое давление в атаке
        elif f_prefix in ["DM", "MID"]:
            pressure_level = 0.5  # среднее давление в центре
        else:
            pressure_level = 0.2  # низкое давление в обороне
    
    # Получаем personality модификатор
    personality_context = {
        'pass_type': pass_type,
        'pressure': pressure_level,
        'zone': f_prefix
    }
    
    personality_bonus = PersonalityModifier.get_pass_modifier(passer, personality_context)
    personality_accuracy_bonus = personality_bonus.get('accuracy', 0.0)
    
    # Применяем personality модификатор к базовой вероятности
    base_probability = (base + bonus + rec_bonus + heading_bonus - penalty) * stamina_factor * morale_factor * momentum_factor
    final_probability = base_probability + personality_accuracy_bonus
    
    return clamp(final_probability)


def shot_success_probability(shooter: Player, goalkeeper: Player | None, *, momentum: int = 0, match_minute: int = 45, pressure: float = 0.0) -> float:
    base = 0.1
    bonus = (shooter.finishing + shooter.long_range + shooter.accuracy) / 300
    penalty = 0
    if goalkeeper:
        penalty = (goalkeeper.reflexes + goalkeeper.handling + goalkeeper.positioning) / 300
    
    # Создаем контекст для personality модификатора
    shot_context = {
        'shot_type': 'close',
        'pressure': pressure,
        'match_minute': match_minute
    }
    
    # Получаем personality модификатор
    personality_bonus = PersonalityModifier.get_shot_modifier(shooter, shot_context)
    personality_accuracy_bonus = personality_bonus.get('accuracy', 0.0)
    
    stamina_factor = 0.7 + (shooter.stamina / 100) * 0.3
    morale_factor = 0.7 + shooter.morale / 200
    momentum_factor = 1 + momentum / 200
    
    # Применяем personality модификатор к финальной вероятности
    base_probability = (base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor
    final_probability = base_probability + personality_accuracy_bonus
    
    return clamp(final_probability)


def long_shot_success_probability(shooter: Player, goalkeeper: Player | None, *, momentum: int = 0, match_minute: int = 45, pressure: float = 0.0) -> float:
    """Probability of scoring with a long range shot."""
    base = 0.05
    bonus = (shooter.long_range * 2 + shooter.finishing + shooter.accuracy) / 400
    penalty = 0
    if goalkeeper:
        penalty = (goalkeeper.reflexes + goalkeeper.handling + goalkeeper.positioning) / 300
    
    # Создаем контекст для personality модификатора
    shot_context = {
        'shot_type': 'long',
        'pressure': pressure,
        'match_minute': match_minute
    }
    
    # Получаем personality модификатор
    personality_bonus = PersonalityModifier.get_shot_modifier(shooter, shot_context)
    personality_accuracy_bonus = personality_bonus.get('accuracy', 0.0)
    
    stamina_factor = 0.7 + (shooter.stamina / 100) * 0.3
    morale_factor = 0.7 + shooter.morale / 200
    momentum_factor = 1 + momentum / 200
    
    # Применяем personality модификатор к финальной вероятности
    base_probability = (base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor
    final_probability = base_probability + personality_accuracy_bonus
    
    return clamp(final_probability)


def foul_probability(tackler: Player, dribbler: Player, zone: str | None = None) -> float:
    """Return probability that ``tackler`` fouls ``dribbler`` in ``zone``."""
    base = 0.05
    diff = tackler.tackling - dribbler.dribbling

    # Players with a high work rate tend to press harder, committing more fouls
    work_rate_bonus = tackler.work_rate / 300

    # Tired players are more prone to commit fouls
    stamina_penalty = (100 - tackler.stamina) / 200

    zone_bonus = 0.0
    if zone and zone_prefix(zone) in {"DEF", "DM"}:
        # Defensive areas see slightly rougher challenges
        zone_bonus = 0.1

    # Существующий расчет базовой вероятности
    base_probability = base + diff / 200 + work_rate_bonus + stamina_penalty + zone_bonus
    
    # Добавляем personality модификатор
    personality_bonus = PersonalityModifier.get_foul_modifier(tackler)
    
    # Применяем к базовой вероятности
    final_probability = base_probability + personality_bonus
    return clamp(final_probability)


def dribble_success_probability(dribbler: Player, defender: Player | None, *, momentum: int = 0) -> float:
    """Probability that a dribble attempt succeeds."""
    base = 0.55
    bonus = (dribbler.dribbling + dribbler.pace + dribbler.flair) / 300
    penalty = 0
    if defender:
        penalty = (defender.tackling + defender.marking + defender.strength) / 300
    stamina_factor = 0.8 + (dribbler.stamina / 100) * 0.2
    morale_factor = 0.85 + dribbler.morale / 200
    momentum_factor = 1 + momentum / 200
    return clamp((base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor)

def process_narrative_event(match, minute, event_type, player, related_player=None):
    """
    Обрабатывает нарративные события в матче
    """
    USE_PERSONALITY_ENGINE = getattr(settings, 'USE_PERSONALITY_ENGINE', False)
    if not USE_PERSONALITY_ENGINE:
        return None
        
    try:
        return NarrativeAIEngine.process_match_event(
            match, minute, event_type, player, related_player
        )
    except Exception as e:
        logger.error(f"Error processing narrative event: {e}")
        return None


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
    
    # Проверяем включен ли PersonalityDecisionEngine
    USE_PERSONALITY_ENGINE = getattr(settings, 'USE_PERSONALITY_ENGINE', False)
    
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

    opponent_team = get_opponent_team(match, possessing_team)
    update_momentum(match, possessing_team, 1)
    update_momentum(match, opponent_team, -1)
    
    # === ИНТЕГРАЦИЯ PersonalityDecisionEngine ===
    
    # Подсчитываем контекстную информацию для personality engine
    def count_nearby_players(team, zone):
        """Подсчитывает количество игроков команды рядом с зоной"""
        adjacent_zones = []
        prefix = zone_prefix(zone)
        side = zone_side(zone)
        
        # Добавляем соседние зоны
        for direction in ['L', 'C', 'R']:
            if direction != side:
                adjacent_zones.append(make_zone(prefix, direction))
        
        # Добавляем зоны спереди и сзади
        row_idx = ROW_INDEX.get(prefix, 0)
        if row_idx > 0:
            adjacent_zones.append(make_zone(ROW_PREFIX[row_idx - 1], side))
        if row_idx < len(ROW_PREFIX) - 1:
            adjacent_zones.append(make_zone(ROW_PREFIX[row_idx + 1], side))
        
        return min(len(adjacent_zones), 3)  # Ограничиваем для реалистичности
    
    def estimate_distance_to_goal(zone):
        """Оценивает расстояние до ворот на основе зоны"""
        prefix = zone_prefix(zone)
        distances = {
            'FWD': 10,
            'AM': 25,
            'MID': 45,
            'DM': 65,
            'DEF': 85,
            'GK': 100
        }
        return distances.get(prefix, 50)
    
    def calculate_pressure_level(opponents_nearby, zone):
        """Рассчитывает уровень давления"""
        base_pressure = 0.3
        zone_pressure = {
            'FWD': 0.4,
            'AM': 0.3,
            'MID': 0.2,
            'DM': 0.15,
            'DEF': 0.1,
            'GK': 0.05
        }
        
        prefix = zone_prefix(zone)
        pressure = base_pressure + zone_pressure.get(prefix, 0.2)
        pressure += opponents_nearby * 0.15
        return min(pressure, 1.0)
    
    # Создаем контекст для PersonalityDecisionEngine
    teammates_nearby = count_nearby_players(possessing_team, current_zone)
    opponents_nearby = count_nearby_players(opponent_team, current_zone)
    goal_distance = estimate_distance_to_goal(current_zone)
    pressure_level = calculate_pressure_level(opponents_nearby, current_zone)
    
    # Определяем тип владения мячом
    possession_type = 'defense'
    prefix = zone_prefix(current_zone)
    if prefix in ['AM', 'FWD']:
        possession_type = 'attack'
    elif prefix in ['MID', 'DM']:
        possession_type = 'midfield'
    
    personality_context = {
        'possession_type': possession_type,
        'goal_distance': goal_distance,
        'teammates_nearby': teammates_nearby,
        'opponents_nearby': opponents_nearby,
        'match_minute': match.current_minute,
        'pressure_level': pressure_level,
        'score_difference': (match.home_score - match.away_score) if possessing_team.id == match.home_team_id else (match.away_score - match.home_score),
        'team_situation': 'drawing'  # По умолчанию
    }
    
    # Обновляем team_situation на основе счета
    score_diff = personality_context['score_difference']
    if score_diff > 0:
        personality_context['team_situation'] = 'winning'
    elif score_diff < 0:
        personality_context['team_situation'] = 'losing'
    
    # Основная логика действия в зависимости от зоны
    if zone_prefix(current_zone) == "FWD":
        # === ЗОНА АТАКИ - РЕШЕНИЕ О УДАРЕ ===
        
        # Используем PersonalityDecisionEngine для принятия решения
        should_shoot = True  # По умолчанию стреляем в зоне атаки
        
        if USE_PERSONALITY_ENGINE:
            # Получаем решение от personality engine
            action_type = PersonalityDecisionEngine.choose_action_type(current_player, personality_context)
            
            # Проверяем склонность к рискованным действиям
            risk_level = 0.6  # Удар по воротам - средний риск
            should_attempt_risky = PersonalityDecisionEngine.should_attempt_risky_action(
                current_player, risk_level, personality_context
            )
            
            # Модифицируем решение на основе personality
            if action_type == 'pass' and not should_attempt_risky:
                # Игрок предпочитает передачу, пробуем найти получателя
                target_zone = next_zone(current_zone)  # Обычно будет FWD, но может быть полезно для кроссов
                potential_recipient = choose_player(possessing_team, target_zone, exclude_ids={current_player.id}, match=match)
                
                if potential_recipient and random.random() < 0.7:  # 70% шанс на пас вместо удара
                    should_shoot = False
        
        if should_shoot:
            # Зона атаки - удар по воротам
            match.st_shoots += 1
            shooter = current_player
            opponent_team = get_opponent_team(match, possessing_team)
            goalkeeper = choose_player(opponent_team, "GK", match=match)
            is_goal = random.random() < shot_success_probability(
                shooter,
                goalkeeper,
                momentum=get_team_momentum(match, possessing_team),
                match_minute=match.current_minute,
                pressure=0.3,  # Средний уровень давления в зоне атаки
            )
            
            # Получаем информацию о влияющей черте характера
            personality_reason = None
            if USE_PERSONALITY_ENGINE:
                trait_name, trait_description = PersonalityDecisionEngine.get_influencing_trait(
                    shooter, 'shoot', personality_context
                )
                if trait_description:
                    personality_reason = f"Повлияла черта: {trait_description}"
            
            if is_goal:
                if possessing_team.id == match.home_team_id:
                    match.home_score += 1
                else:
                    match.away_score += 1
                update_momentum(match, possessing_team, 25)
                update_momentum(match, opponent_team, -25)
                
                # === СИСТЕМА МОРАЛИ: ГОЛ ===
                # Бонус стрелку
                process_morale_event(shooter, 'goal_scored', match, current_zone)
                # Штраф команде соперника
                apply_team_morale_effect(opponent_team, 'goal_conceded', match)
                # Особый штраф вратарю соперника
                if goalkeeper:
                    process_morale_event(goalkeeper, 'goal_conceded_gk', match, current_zone)
                
                # === НАРРАТИВНАЯ СИСТЕМА: ГОЛ ===
                process_narrative_event(match, match.current_minute, 'goal_scored', shooter, goalkeeper)
                
                event_data = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'goal',
                    'player': shooter,
                    'description': render_comment(
                        'goal',
                        shooter=f"{shooter.first_name} {shooter.last_name}",
                        team=possessing_team.name,
                        home=match.home_score,
                        away=match.away_score,
                    ),
                    'personality_reason': personality_reason
                }
            else:
                # === СИСТЕМА МОРАЛИ: ПРОМАХ ===
                process_morale_event(shooter, 'shot_miss', match, current_zone)
                # Бонус вратарю за отражение (если есть)
                if goalkeeper:
                    process_morale_event(goalkeeper, 'shot_saved_gk', match, current_zone)
                
                event_data = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'shot_miss',
                    'player': shooter,
                    'description': render_comment(
                        'shot_miss',
                        shooter=f"{shooter.first_name} {shooter.last_name}",
                    ),
                    'personality_reason': personality_reason
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
        # Если should_shoot == False, переходим к логике паса
    
    # === ЛОГИКА ПЕРЕДАЧ И ДРИБЛИНГА ===
    
    # Если мы не в зоне атаки ИЛИ в зоне атаки, но не стреляем, то делаем пас
    should_pass = True
    if zone_prefix(current_zone) == "FWD" and 'should_shoot' in locals() and should_shoot:
        should_pass = False
    
    if should_pass:
        # Attempt a pass to the next zone keeping the same side
        target_zone = next_zone(current_zone)
        is_long = False
        current_row = ROW_INDEX.get(zone_prefix(current_zone), 0)
        available_rows = len(ROW_PREFIX) - 1 - current_row
        
        # Apply personality influence to long pass decision
        long_pass_chance = 0.2  # Базовый шанс длинного паса
        if available_rows > 1:
            if USE_PERSONALITY_ENGINE:
                # Длинный пас - рискованное действие
                risk_level = 0.8
                should_attempt_risky = PersonalityDecisionEngine.should_attempt_risky_action(
                    current_player, risk_level, personality_context
                )
                
                action_type = PersonalityDecisionEngine.choose_action_type(current_player, personality_context)
                
                # Модифицируем шанс длинного паса
                if action_type == 'long_pass' and should_attempt_risky:
                    long_pass_chance *= 2.5  # Увеличиваем для игроков, склонных к длинным пасам
                elif not should_attempt_risky:
                    long_pass_chance *= 0.3  # Снижаем для осторожных игроков
                
                long_pass_chance = clamp(long_pass_chance, 0.05, 0.6)
            
            if random.random() < long_pass_chance:
                steps = random.randint(2, min(3, available_rows))
                next_row = current_row + steps
                target_zone = make_zone(ROW_PREFIX[next_row], zone_side(current_zone))
                is_long = True

        match.st_possessions += 1

        # --- New dribbling logic with personality integration ---
        attempt_dribble = False
        if current_player.position != "Goalkeeper" and current_player.dribbling > 50:
            dribble_chance = clamp((current_player.dribbling + current_player.pace) / 200, 0, 0.8)
            
            # Apply personality influence to dribbling decision
            if USE_PERSONALITY_ENGINE:
                action_type = PersonalityDecisionEngine.choose_action_type(current_player, personality_context)
                risk_level = 0.7  # Дриблинг - довольно рискованное действие
                should_attempt_risky = PersonalityDecisionEngine.should_attempt_risky_action(
                    current_player, risk_level, personality_context
                )
                
                # Модифицируем шанс дриблинга на основе personality
                if action_type == 'dribble' and should_attempt_risky:
                    dribble_chance *= 1.5  # Увеличиваем шанс для игроков склонных к дриблингу
                elif action_type == 'pass' or not should_attempt_risky:
                    dribble_chance *= 0.4  # Снижаем шанс для осторожных игроков
                
                dribble_chance = clamp(dribble_chance, 0, 0.9)
            
            if random.random() < dribble_chance:
                attempt_dribble = True

        opponent_team = get_opponent_team(match, possessing_team)

        if attempt_dribble:
            # Move forward keeping the same side most of the time,
            # occasionally shifting diagonally left/right.
            target_zone = forward_dribble_zone(current_zone)
            intercept_zone = mirrored_zone(target_zone, flip_side=True)
            zones = [
                intercept_zone,
                make_zone("FWD", mirror_side(zone_side(target_zone))),
                make_zone("MID", mirror_side(zone_side(target_zone))),
                make_zone("MID", "C"),
            ]
            defender, def_zone = choose_player_from_zones(opponent_team, zones, match=match)
            success_prob = dribble_success_probability(
                current_player,
                defender,
                momentum=get_team_momentum(match, possessing_team),
            )
            
            # Получаем информацию о влияющей черте характера для дриблинга
            dribble_personality_reason = None
            if USE_PERSONALITY_ENGINE:
                trait_name, trait_description = PersonalityDecisionEngine.get_influencing_trait(
                    current_player, 'dribble', personality_context
                )
                if trait_description:
                    dribble_personality_reason = f"Повлияла черта: {trait_description}"
            
            dribble_event = {
                'match': match,
                'minute': match.current_minute,
                'event_type': 'dribble',
                'player': current_player,
                'related_player': defender,
                'description': render_comment(
                    'dribble',
                    player=current_player.last_name,
                    zone=target_zone,
                ),
                'personality_reason': dribble_personality_reason
            }

            if random.random() < success_prob:
                match.current_zone = target_zone
                # ball remains with current_player
                
                # === СИСТЕМА МОРАЛИ: УДАЧНЫЙ ДРИБЛИНГ ===
                process_morale_event(current_player, 'dribble_success', match, target_zone)
                
                if defender:
                    foul_chance = foul_probability(defender, current_player, target_zone)
                    if random.random() < foul_chance:
                        match.st_fouls += 1
                        
                        # === СИСТЕМА МОРАЛИ: ФОЛ ===
                        process_morale_event(defender, 'foul_committed', match, target_zone)
                        process_morale_event(current_player, 'foul_suffered', match, target_zone)
                        
                        foul_event = {
                            'match': match,
                            'minute': match.current_minute,
                            'event_type': 'foul',
                            'player': defender,
                            'related_player': current_player,
                            'description': render_comment(
                                'foul',
                                player=defender.last_name,
                                target=current_player.last_name,
                                zone=target_zone,
                            ),
                        }
                        process_injury(match)
                        return {
                            'event': dribble_event,
                            'additional_event': foul_event,
                            'action_type': 'dribble',
                            'continue': False,
                        }

                return {
                    'event': dribble_event,
                    'action_type': 'dribble',
                    'continue': True,
                }
            else:
                # === СИСТЕМА МОРАЛИ: НЕУДАЧНЫЙ ДРИБЛИНГ ===
                process_morale_event(current_player, 'dribble_failed', match, target_zone)
                
                # === НАРРАТИВНАЯ СИСТЕМА: ПЕРЕХВАТ ===
                if defender:
                    process_narrative_event(match, match.current_minute, 'interception', defender, current_player)
                
                if defender:
                    interception_event = {
                        'match': match,
                        'minute': match.current_minute,
                        'event_type': 'interception',
                        'player': defender,
                        'related_player': current_player,
                        'description': render_comment(
                            'interception',
                            interceptor=defender.last_name,
                            player=current_player.last_name,
                            zone=target_zone,
                        ),
                    }
                    # Trigger a counterattack if the ball is stolen during a
                    # dribble in the defending or defensive midfield zone
                    counterattack_on_dribble = zone_prefix(target_zone) in {"DEF", "DM"}
                    # Counterattack even on failed dribbles in DEF/DM zones
                    special_counter_dribble = zone_prefix(target_zone) in {"DEF", "DM"}
                    
                    # Apply personality influence to counterattack decision
                    if USE_PERSONALITY_ENGINE and defender and counterattack_on_dribble:
                        # Создаем контекст для защитника, который перехватил мяч
                        defender_context = {
                            'possession_type': 'transition',  # Переходная фаза
                            'goal_distance': 100 - goal_distance,  # Расстояние до ворот соперника
                            'teammates_nearby': count_nearby_players(opponent_team, target_zone),
                            'opponents_nearby': count_nearby_players(possessing_team, target_zone),
                            'match_minute': match.current_minute,
                            'pressure_level': 0.2,  # Низкое давление после перехвата
                            'score_difference': -personality_context['score_difference'],  # Инвертируем для другой команды
                            'team_situation': personality_context['team_situation']
                        }
                        
                        # Обновляем team_situation для защитника
                        if defender_context['score_difference'] > 0:
                            defender_context['team_situation'] = 'winning'
                        elif defender_context['score_difference'] < 0:
                            defender_context['team_situation'] = 'losing'
                        else:
                            defender_context['team_situation'] = 'drawing'
                        
                        # Решение о контратаке
                        action_type = PersonalityDecisionEngine.choose_action_type(defender, defender_context)
                        risk_level = 0.6  # Контратака - средний риск
                        should_attempt_risky = PersonalityDecisionEngine.should_attempt_risky_action(
                            defender, risk_level, defender_context
                        )
                        
                        # Модифицируем вероятность контратаки
                        if action_type == 'attack' and should_attempt_risky:
                            special_counter_dribble = True  # Принудительная контратака
                        elif not should_attempt_risky:
                            # Осторожные игроки могут выбрать более безопасный вариант
                            if random.random() < 0.3:
                                special_counter_dribble = False

                    new_defender, new_zone = choose_player_from_zones(opponent_team, zones, match=match)
                    if new_defender:
                        match.current_player_with_ball = new_defender
                        match.current_zone = new_zone
                    else:
                        match.current_player_with_ball = defender
                        match.current_zone = def_zone

                    counterattack_event = {
                        'match': match,
                        'minute': match.current_minute,
                        'event_type': 'counterattack',
                        'player': defender,
                        'related_player': current_player,
                        'description': render_comment(
                            'counterattack',
                            interceptor=defender.last_name,
                        ),
                    }

                    if counterattack_on_dribble:
                        if special_counter_dribble:
                            return {
                                'event': dribble_event,
                                'additional_event': interception_event,
                                'second_additional_event': counterattack_event,
                                'action_type': 'counterattack',
                                'continue': True,
                            }
                    else:
                        return {
                            'event': dribble_event,
                            'additional_event': interception_event,
                            'action_type': 'interception',
                            'continue': False,
                        }
                else:
                    return {
                        'event': dribble_event,
                        'action_type': 'failed_interception',
                        'continue': False,
                    }

        recipient = choose_player(possessing_team, target_zone, exclude_ids={current_player.id}, match=match)

        opponent = choose_player(opponent_team, target_zone, match=match)
        pass_prob = pass_success_probability(
            current_player,
            recipient,
            opponent,
            from_zone=current_zone,
            to_zone=target_zone,
            high=is_long,
            momentum=get_team_momentum(match, possessing_team),
        ) if recipient else 0
        
        # Получаем информацию о влияющей черте характера для паса
        pass_personality_reason = None
        if USE_PERSONALITY_ENGINE:
            pass_type = 'long_pass' if is_long else 'pass'
            trait_name, trait_description = PersonalityDecisionEngine.get_influencing_trait(
                current_player, pass_type, personality_context
            )
            if trait_description:
                pass_personality_reason = f"Повлияла черта: {trait_description}"

        if recipient:
            if random.random() < pass_prob:
                match.st_passes += 1

                event_data = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'pass',
                    'player': current_player,
                    'related_player': recipient,
                    'description': render_comment(
                        'pass',
                        player=current_player.last_name,
                        recipient=recipient.last_name,
                        from_zone=current_zone,
                        to_zone=target_zone,
                    ),
                    'personality_reason': pass_personality_reason
                }

                match.current_player_with_ball = recipient
                match.current_zone = target_zone

                # === СИСТЕМА МОРАЛИ: УСПЕШНЫЙ ПАС ===
                process_morale_event(current_player, 'successful_pass', match, target_zone)
                
                # === НАРРАТИВНАЯ СИСТЕМА: УСПЕШНЫЙ ПАС ===
                process_narrative_event(match, match.current_minute, 'pass', current_player, recipient)

                # После паса возможен фол
                fouler = choose_player(opponent_team, "ANY", match=match)
                if fouler:
                    foul_chance = foul_probability(fouler, recipient, target_zone)
                    if random.random() < foul_chance:
                        match.st_fouls += 1
                        
                        # === СИСТЕМА МОРАЛИ: ФОЛ ===
                        process_morale_event(fouler, 'foul_committed', match, target_zone)
                        process_morale_event(recipient, 'foul_suffered', match, target_zone)
                        
                        # === НАРРАТИВНАЯ СИСТЕМА: ФОЛ ===
                        process_narrative_event(match, match.current_minute, 'foul', fouler, recipient)
                        
                        foul_event = {
                            'match': match,
                            'minute': match.current_minute,
                            'event_type': 'foul',
                            'player': fouler,
                            'related_player': recipient,
                            'description': render_comment(
                                'foul',
                                player=fouler.last_name,
                                target=recipient.last_name,
                                zone=target_zone,
                            ),
                        }
                        process_injury(match)
                        return {
                            'event': event_data,
                            'additional_event': foul_event,
                            'action_type': 'pass',
                            'continue': False,
                        }

                return {
                    'event': event_data,
                    'action_type': 'pass',
                    'continue': True,
                }
            else:
                # Неудачный пас и возможный перехват
                opponent_team = get_opponent_team(match, possessing_team)
                # Determine where the ball would likely be intercepted.
                intercept_zone = mirrored_zone(target_zone, flip_side=True)
                zones = [
                    intercept_zone,
                    make_zone("FWD", mirror_side(zone_side(target_zone))),
                    make_zone("MID", mirror_side(zone_side(target_zone))),
                    make_zone("MID", "C"),
                ]
                interceptor, used_zone = choose_player_from_zones(
                    opponent_team, zones, match=match
                )

                # Событие попытки паса
                pass_event = {
                    'match': match,
                    'minute': match.current_minute,
                    'event_type': 'pass',
                    'player': current_player,
                    'related_player': recipient,
                    'description': render_comment(
                        'pass',
                        player=current_player.last_name,
                        recipient=recipient.last_name,
                        from_zone=current_zone,
                        to_zone=target_zone,
                    ),
                    'personality_reason': pass_personality_reason
                }

                if interceptor:
                    # === СИСТЕМА МОРАЛИ: ПЕРЕХВАТ ПАСА ===
                    process_morale_event(current_player, 'pass_intercepted', match, target_zone)
                    
                    special_counter = (
                        (zone_prefix(current_zone) == "GK" and zone_prefix(target_zone) == "DEF") or
                        (zone_prefix(current_zone) == "DEF" and zone_prefix(target_zone) == "DM") or
                        (zone_prefix(current_zone) == "GK" and zone_prefix(target_zone) == "DM")
                    )

                    interception_event = {
                        'match': match,
                        'minute': match.current_minute,
                        'event_type': 'interception',
                        'player': interceptor,
                        'related_player': current_player,
                        'description': render_comment(
                            'interception',
                            interceptor=interceptor.last_name,
                            player=current_player.last_name,
                            zone=target_zone,
                        ),
                    }

                    counterattack_event = {
                        'match': match,
                        'minute': match.current_minute,
                        'event_type': 'counterattack',
                        'player': interceptor,
                        'related_player': current_player,
                        'description': render_comment(
                            'counterattack',
                            interceptor=interceptor.last_name,
                        ),
                    }

                    if special_counter:
                        match.current_player_with_ball = interceptor
                        if zone_prefix(current_zone) == "GK" and zone_prefix(target_zone) == "DEF":
                            # Перехват в зоне защиты соперника – мгновенный пас вперёд
                            match.current_zone = make_zone("FWD", zone_side(target_zone))
                            return {
                                'event': pass_event,
                                'additional_event': interception_event,
                                'second_additional_event': counterattack_event,
                                'action_type': 'counterattack',
                                'continue': True
                            }
                        else:
                            # Перехват в центре поля: шанс на дальний удар
                            long_shot = random.random() < 0.5
                            if long_shot:
                                match.st_shoots += 1
                                goalkeeper = choose_player(possessing_team, "GK", match=match)
                                is_goal = random.random() < long_shot_success_probability(
                                    interceptor,
                                    goalkeeper,
                                    momentum=get_team_momentum(match, opponent_team),
                                    match_minute=match.current_minute,
                                    pressure=0.5,  # Повышенное давление при дальнем ударе после перехвата
                                )
                                if is_goal:
                                    if opponent_team.id == match.home_team_id:
                                        match.home_score += 1
                                    else:
                                        match.away_score += 1
                                    shot_event = {
                                        'match': match,
                                        'minute': match.current_minute,
                                        'event_type': 'goal',
                                        'player': interceptor,
                                        'description': render_comment(
                                            'goal',
                                            shooter=interceptor.last_name,
                                            team=opponent_team.name,
                                            home=match.home_score,
                                            away=match.away_score,
                                        ),
                                    }
                                else:
                                    shot_event = {
                                        'match': match,
                                        'minute': match.current_minute,
                                        'event_type': 'shot_miss',
                                        'player': interceptor,
                                        'description': render_comment(
                                            'shot_miss',
                                            shooter=interceptor.last_name,
                                        ),
                                    }

                                new_keeper = choose_player(possessing_team, "GK", match=match)
                                if new_keeper:
                                    match.current_player_with_ball = new_keeper
                                    match.current_zone = "GK"
                                return {
                                    'event': pass_event,
                                    'additional_event': interception_event,
                                    'second_additional_event': counterattack_event,
                                    'third_additional_event': shot_event,
                                    'action_type': 'counterattack',
                                    'continue': False
                                }
                            else:
                                # Быстрый пас после перехвата вместо мгновенного
                                # перемещения в атаку
                                recipient = choose_player(
                                    opponent_team,
                                    make_zone("FWD", zone_side(target_zone)),
                                    exclude_ids={interceptor.id},
                                    match=match,
                                )
                                opponent_def = choose_player(
                                    possessing_team,
                                    make_zone("DEF", zone_side(target_zone)),
                                    match=match,
                                )
                                pass_prob2 = pass_success_probability(
                                    interceptor,
                                    recipient,
                                    opponent_def,
                                    from_zone=make_zone("DM", zone_side(target_zone)),
                                    to_zone=make_zone("FWD", zone_side(target_zone)),
                                    high=True,
                                    momentum=get_team_momentum(match, opponent_team),
                                ) if recipient else 0

                                if recipient and random.random() < pass_prob2:
                                    match.st_passes += 1
                                    counter_pass_event = {
                                        'match': match,
                                        'minute': match.current_minute,
                                        'event_type': 'pass',
                                        'player': interceptor,
                                        'related_player': recipient,
                                        'description': render_comment(
                                            'pass',
                                            player=interceptor.last_name,
                                            recipient=recipient.last_name,
                                            from_zone=f"DM-{zone_side(target_zone)}",
                                            to_zone=f"FWD-{zone_side(target_zone)}",
                                        ),
                                    }
                                    match.current_player_with_ball = recipient
                                    match.current_zone = make_zone("FWD", zone_side(target_zone))
                                    return {
                                        'event': pass_event,
                                        'additional_event': interception_event,
                                        'second_additional_event': counterattack_event,
                                        'third_additional_event': counter_pass_event,
                                        'action_type': 'counterattack',
                                        'continue': True
                                    }
                                else:
                                    fail_interceptor = choose_player(
                                        possessing_team,
                                        make_zone("DEF", zone_side(target_zone)),
                                        match=match,
                                    )
                                    if fail_interceptor:
                                        interception2_event = {
                                            'match': match,
                                            'minute': match.current_minute,
                                            'event_type': 'interception',
                                            'player': fail_interceptor,
                                            'related_player': interceptor,
                                            'description': render_comment(
                                                'interception',
                                                interceptor=fail_interceptor.last_name,
                                                player=interceptor.last_name,
                                                zone=f"DM-{zone_side(target_zone)}",
                                            ),
                                        }
                                        new_defender2 = choose_player(
                                            possessing_team,
                                            make_zone("DEF", zone_side(target_zone)),
                                            match=match,
                                        )
                                        if new_defender2:
                                            match.current_player_with_ball = new_defender2
                                            match.current_zone = make_zone(
                                                "DEF",
                                                zone_side(target_zone),
                                            )
                                        else:
                                            match.current_player_with_ball = fail_interceptor
                                            match.current_zone = make_zone(
                                                "DEF", zone_side(target_zone)
                                            )
                                        return {
                                            'event': pass_event,
                                            'additional_event': interception_event,
                                            'second_additional_event': counterattack_event,
                                            'third_additional_event': interception2_event,
                                            'action_type': 'counterattack',
                                            'continue': False
                                        }
                                    else:
                                        match.current_player_with_ball = interceptor
                                        match.current_zone = make_zone("DM", zone_side(target_zone))
                                        return {
                                            'event': pass_event,
                                            'additional_event': interception_event,
                                            'second_additional_event': counterattack_event,
                                            'action_type': 'counterattack',
                                            'continue': True
                                        }

                    # Мяч переходит к защитнику перехватившей команды
                    new_defender = choose_player(
                        opponent_team,
                        make_zone("DEF", zone_side(intercept_zone)),
                        match=match,
                    )
                    if new_defender:
                        match.current_player_with_ball = new_defender
                        match.current_zone = make_zone(
                            "DEF", zone_side(intercept_zone)
                        )
                    else:
                        match.current_player_with_ball = interceptor
                        match.current_zone = make_zone("DEF", zone_side(intercept_zone))

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