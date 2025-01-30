import random
import logging
from django.db import transaction
from django.utils import timezone
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player

logger = logging.getLogger(__name__)

def auto_select_lineup(club: Club) -> dict:
    """
    Простейшая автогенерация состава (4-4-2).
    Возвращает словарь формата:
      {
        "lineup": {
          "0": {"playerId": "123", "slotType": "goalkeeper", "slotLabel": "GK"},
          "1": {"playerId": "124", "slotType": "defender",   "slotLabel": "RB"},
          ...
        },
        "tactic": "balanced"  # например
      }

    В упрощённом виде: находим GK, берем 4 защитника, 4 полузащитника, 2 форварда.
    Если игроков в club < 11, возвращаем пустой lineup.
    """
    players = list(club.player_set.all())
    if len(players) < 11:
        return {
            "lineup": {},
            "tactic": "balanced"
        }

    # 1) Ищем вратаря
    gk = next((p for p in players if p.position == "Goalkeeper"), None)
    if not gk:
        # Если нет вообще вратаря, выберем первого
        gk = players[0]

    # Убираем его из пула
    used_ids = {gk.id}

    # (Просто для примера) соберем всех защитников
    defenders = [p for p in players if ("Back" in p.position or "Defender" in p.position) and p.id not in used_ids]
    defenders = defenders[:4]  # берём 4

    # полузащитники
    midfielders = [p for p in players if "Midfielder" in p.position and p.id not in used_ids]
    midfielders = midfielders[:4]

    # форварды
    forwards = [p for p in players if "Forward" in p.position and p.id not in used_ids]
    forwards = forwards[:2]

    # Формируем словарь
    lineup_dict = {}

    # Слот 0 = GK
    lineup_dict["0"] = {
        "playerId": str(gk.id),
        "slotType": "goalkeeper",
        "slotLabel": "GK"
    }

    slot_index = 1
    # DEF
    for d in defenders:
        lineup_dict[str(slot_index)] = {
            "playerId": str(d.id),
            "slotType": "defender",
            "slotLabel": f"DEF{slot_index}"
        }
        slot_index += 1

    # MID
    for m in midfielders:
        lineup_dict[str(slot_index)] = {
            "playerId": str(m.id),
            "slotType": "midfielder",
            "slotLabel": f"MID{slot_index}"
        }
        slot_index += 1

    # FWD
    for f in forwards:
        lineup_dict[str(slot_index)] = {
            "playerId": str(f.id),
            "slotType": "forward",
            "slotLabel": f"FWD{slot_index}"
        }
        slot_index += 1

    return {
        "lineup": lineup_dict,
        "tactic": "balanced"
    }

def ensure_match_lineup_set(match: Match, for_home: bool) -> None:
    """
    Проверяет состав команды для матча.
    1) Пытается взять состав из club.lineup
    2) Если там пусто или состав неполный - генерирует auto_select_lineup()
    
    :param for_home: True => работаем с home_lineup, иначе away_lineup
    """
    team = match.home_team if for_home else match.away_team
    
    # Берем состав из club.lineup
    club_lineup = team.lineup
    
    # Проверяем валидность состава из club.lineup
    if (not club_lineup or 
        not isinstance(club_lineup, dict) or 
        not club_lineup.get("lineup") or 
        len(club_lineup.get("lineup", {})) < 11):
        # Если состав отсутствует или неполный - генерируем автоматически
        new_lineup = auto_select_lineup(team)
        if for_home:
            match.home_lineup = new_lineup
        else:
            match.away_lineup = new_lineup
    else:
        # Используем существующий состав из club.lineup
        if for_home:
            match.home_lineup = club_lineup
        else:
            match.away_lineup = club_lineup

def simulate_one_minute(match: Match, minute: int):
    """
    Упрощённая логика "1 минута матча".
    Пример: 30% шанс на "MOMENT", 10% шанс гола, и рандом выбраем HOME / AWAY.
    """
    # 30% шанс
    if random.random() < 0.3:
        side = random.choice(["HOME", "AWAY"])
        desc = f"MOMENT at minute {minute}: {side} tries to attack!"
        MatchEvent.objects.create(
            match=match,
            minute=minute,
            event_type='info',
            description=desc
        )
        logger.info(desc)

        # 10% шанс гола
        if random.random() < 0.10:
            if side == "HOME":
                match.home_score += 1
                desc_g = f"GOAL by HOME at minute {minute}!"
            else:
                match.away_score += 1
                desc_g = f"GOAL by AWAY at minute {minute}!"

            MatchEvent.objects.create(
                match=match,
                minute=minute,
                event_type='goal',
                description=desc_g
            )
            logger.info(desc_g)

def simulate_match(match_id: int):
    """
    Главная функция симуляции матча.
    1) Находим match (status='scheduled')
    2) Заполняем home_lineup/away_lineup из club.lineup или auto_select_lineup
    3) Ставим match.status='in_progress', счёт=0:0, current_minute=0
    4) 90 минут => simulate_one_minute()
    5) Ставим match.status='finished', current_minute=90, сохраняем счёт
    """
    try:
        with transaction.atomic():
            match = Match.objects.select_for_update().get(id=match_id)
            if match.status != 'scheduled':
                logger.warning(f"Match {match.id} is not scheduled => skip simulation")
                return

            # 1) ensure lineups
            ensure_match_lineup_set(match, True)   # home
            ensure_match_lineup_set(match, False)  # away
            
            # 2) Инициализация матча
            match.home_score = 0
            match.away_score = 0
            match.current_minute = 0
            match.status = 'in_progress'
            match.save()

            # 3) Симуляция 90 минут
            for minute in range(1, 91):
                simulate_one_minute(match, minute)

            # 4) Завершение матча
            match.status = 'finished'
            match.current_minute = 90
            match.save()

            logger.info(f"Match {match.id} ended: {match.home_score}-{match.away_score}")

    except Match.DoesNotExist:
        logger.error(f"Match {match_id} not found")
    except Exception as e:
        logger.error(f"Error in simulate_match({match_id}): {str(e)}")
        raise
