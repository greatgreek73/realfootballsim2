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
from matches.commentary import render_comment

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


def update_possession(match: Match, player: Player | None, zone: str | None = None) -> None:
    """Update match possession details.

    Sets the current player with the ball and zone (if provided) and updates
    ``match.possession_indicator`` based on the player's club.
    """
    match.current_player_with_ball = player
    if zone is not None:
        match.current_zone = zone

    if not player:
        match.possession_indicator = 0
    elif player.club_id == match.home_team_id:
        match.possession_indicator = 1
    elif player.club_id == match.away_team_id:
        match.possession_indicator = 2
    else:
        match.possession_indicator = 0


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
    if f_prefix == "GK" and t_prefix == "DEF":
        def_base = 0.9
    elif f_prefix == "DEF" and t_prefix == "DM":
        def_base = 0.8
    elif f_prefix == "DM" and t_prefix == "MID":
        def_base = 0.75
    elif f_prefix == "MID" and t_prefix == "AM":
        def_base = 0.7
    elif f_prefix == "AM" and t_prefix == "FWD":
        def_base = 0.65
    base = def_base

    if high:
        try:
            distance = ROW_INDEX[t_prefix] - ROW_INDEX[f_prefix]
        except Exception:
            distance = 1
        base -= 0.05 * max(distance - 1, 0)


    # Passing and vision continue to provide the main boost.  Values are in the
    # range 0-100 so the maximum bonus is around +1.0 when both stats are high.
    bonus = (passer.passing + passer.vision) / 200

    # Receiver positioning also helps.  Unpositioned passes still have a chance
    # but we favour well‑positioned targets.
    rec_bonus = recipient.positioning / 200 if recipient else 0
    heading_bonus = recipient.heading / 200 if high and recipient else 0

    penalty = 0
    if opponent:
        # Reduce the weight of defensive skills so a single opponent does not
        # negate a reasonable passing attempt quite as often.
        penalty = (opponent.marking + opponent.tackling) / 400
    stamina_factor = passer.stamina / 100
    morale_factor = 0.5 + passer.morale / 200
    momentum_factor = 1 + momentum / 200
    return clamp((base + bonus + rec_bonus + heading_bonus - penalty) * stamina_factor * morale_factor * momentum_factor)


def shot_success_probability(shooter: Player, goalkeeper: Player | None, *, momentum: int = 0) -> float:
    base = 0.1
    bonus = (shooter.finishing + shooter.long_range + shooter.accuracy) / 300
    penalty = 0
    if goalkeeper:
        penalty = (goalkeeper.reflexes + goalkeeper.handling + goalkeeper.positioning) / 300
    stamina_factor = shooter.stamina / 100
    morale_factor = 0.5 + shooter.morale / 200
    momentum_factor = 1 + momentum / 200
    return clamp((base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor)


def long_shot_success_probability(shooter: Player, goalkeeper: Player | None, *, momentum: int = 0) -> float:
    """Probability of scoring with a long range shot."""
    base = 0.05
    bonus = (shooter.long_range * 2 + shooter.finishing + shooter.accuracy) / 400
    penalty = 0
    if goalkeeper:
        penalty = (goalkeeper.reflexes + goalkeeper.handling + goalkeeper.positioning) / 300
    stamina_factor = shooter.stamina / 100
    morale_factor = 0.5 + shooter.morale / 200
    momentum_factor = 1 + momentum / 200
    return clamp((base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor)


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

    probability = base + diff / 200 + work_rate_bonus + stamina_penalty + zone_bonus
    return clamp(probability)


def dribble_success_probability(dribbler: Player, defender: Player | None, *, momentum: int = 0) -> float:
    """Probability that a dribble attempt succeeds."""
    base = 0.55
    bonus = (dribbler.dribbling + dribbler.pace + dribbler.flair) / 300
    penalty = 0
    if defender:
        penalty = (defender.tackling + defender.marking + defender.strength) / 300
    stamina_factor = dribbler.stamina / 100
    morale_factor = 0.5 + dribbler.morale / 200
    momentum_factor = 1 + momentum / 200
    return clamp((base + bonus - penalty) * stamina_factor * morale_factor * momentum_factor)

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
        update_possession(match, current_player, "GK")

    # Индикатор владения обновляется через update_possession

    opponent_team = get_opponent_team(match, possessing_team)
    update_momentum(match, possessing_team, 1)
    update_momentum(match, opponent_team, -1)
    
    
    # Основная логика действия в зависимости от зоны
    if zone_prefix(current_zone) == "FWD":
        # Зона атаки - удар по воротам
        match.st_shoots += 1
        shooter = current_player
        opponent_team = get_opponent_team(match, possessing_team)
        goalkeeper = choose_player(opponent_team, "GK", match=match)
        is_goal = random.random() < shot_success_probability(
            shooter,
            goalkeeper,
            momentum=get_team_momentum(match, possessing_team),
        )
        
        if is_goal:
            if possessing_team.id == match.home_team_id:
                match.home_score += 1
            else:
                match.away_score += 1
            update_momentum(match, possessing_team, 25)
            update_momentum(match, opponent_team, -25)
            
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
                )
            }
        else:
            event_data = {
                'match': match,
                'minute': match.current_minute,
                'event_type': 'shot_miss',
                'player': shooter,
                'description': render_comment(
                    'shot_miss',
                    shooter=f"{shooter.first_name} {shooter.last_name}",
                )
            }
        
        # После удара мяч переходит к вратарю соперника
        opponent_team = get_opponent_team(match, possessing_team)
        new_keeper = choose_player(opponent_team, "GK", match=match)
        if new_keeper:
            update_possession(match, new_keeper, "GK")
        
        return {
            'event': event_data,
            'action_type': 'shot',
            'continue': False  # Конец атаки
        }
    
    else:
        # Attempt a pass to the next zone keeping the same side
        target_zone = next_zone(current_zone)
        is_long = False
        current_row = ROW_INDEX.get(zone_prefix(current_zone), 0)
        available_rows = len(ROW_PREFIX) - 1 - current_row
        if available_rows > 1 and random.random() < 0.2:
            steps = random.randint(2, min(3, available_rows))
            next_row = current_row + steps
            target_zone = make_zone(ROW_PREFIX[next_row], zone_side(current_zone))
            is_long = True

        match.st_possessions += 1

        # --- New dribbling logic ---
        attempt_dribble = False
        if current_player.position != "Goalkeeper" and current_player.dribbling > 50:
            dribble_chance = clamp((current_player.dribbling + current_player.pace) / 200, 0, 0.8)
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
            }

            if random.random() < success_prob:
                update_possession(match, current_player, target_zone)
                # ball remains with current_player
                if defender:
                    foul_chance = foul_probability(defender, current_player, target_zone)
                    if random.random() < foul_chance:
                        match.st_fouls += 1
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

                    new_defender, new_zone = choose_player_from_zones(opponent_team, zones, match=match)
                    if new_defender:
                        update_possession(match, new_defender, new_zone)
                    else:
                        update_possession(match, defender, def_zone)

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
                    )
                }

                update_possession(match, recipient, target_zone)

                # После паса возможен фол
                fouler = choose_player(opponent_team, "ANY", match=match)
                if fouler:
                    foul_chance = foul_probability(fouler, recipient, target_zone)
                    if random.random() < foul_chance:
                        match.st_fouls += 1
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
                }

                if interceptor:
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
                        update_possession(match, interceptor)
                        if zone_prefix(current_zone) == "GK" and zone_prefix(target_zone) == "DEF":
                            # Перехват в зоне защиты соперника – мгновенный пас вперёд
                            update_possession(match, interceptor, make_zone("FWD", zone_side(target_zone)))
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
                                    update_possession(match, new_keeper, "GK")
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
                                    update_possession(match, recipient, make_zone("FWD", zone_side(target_zone)))
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
                                            update_possession(
                                                match,
                                                new_defender2,
                                                make_zone("DEF", zone_side(target_zone)),
                                            )
                                        else:
                                            update_possession(
                                                match,
                                                fail_interceptor,
                                                make_zone("DEF", zone_side(target_zone)),
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
                                        update_possession(
                                            match,
                                            interceptor,
                                            make_zone("DM", zone_side(target_zone)),
                                        )
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
                        update_possession(
                            match,
                            new_defender,
                            make_zone("DEF", zone_side(intercept_zone)),
                        )
                    else:
                        update_possession(
                            match,
                            interceptor,
                            make_zone("DEF", zone_side(intercept_zone)),
                        )

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