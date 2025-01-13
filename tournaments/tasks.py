from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.core.management import call_command
from matches.models import Match
from players.models import Player
from clubs.models import Club
from .models import Season, Championship, League
import logging
import time
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
import random

logger = logging.getLogger(__name__)


def retry_on_db_lock(func, max_attempts=3, delay=1):
    """
    Декоратор для повторных попыток в случае Database is locked (SQLite).
    """
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "database is locked" in str(e) and attempts < max_attempts - 1:
                    attempts += 1
                    time.sleep(delay)
                    continue
                raise
    return wrapper


@shared_task(name='tournaments.simulate_active_matches', bind=True)
def simulate_active_matches(self):
    """
    Пошаговая симуляция матчей (каждая «минута»).
    """
    now = timezone.now()
    logger.info(f"Starting active matches simulation at {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("No matches in progress at the moment.")
        return "No matches in progress"

    from matches.match_simulation import simulate_one_minute

    for match in matches:
        simulate_one_minute(match.id)
        logger.info(
            f"Simulated one minute for match {match.id} "
            f"({match.home_team} vs {match.away_team}, current_minute={match.current_minute})"
        )

    return f"Simulated one minute for {matches.count()} matches"


@shared_task(name='tournaments.check_season_end', bind=True)
def check_season_end(self):
    """
    Проверяет окончание сезона и создаёт новый при необходимости.
    """
    try:
        with transaction.atomic():
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()

            logger.info(
                f"Checking season {current_season.number} (end date: {current_season.end_date})"
            )

            is_end_date_passed = today > current_season.end_date
            finished_matches_count = Match.objects.filter(
                championshipmatch__championship__season=current_season,
                status='finished'
            ).count()

            required_matches = (
                len(Championship.objects.filter(season=current_season)) * (16 * 15)
            )
            all_matches_played = finished_matches_count >= required_matches

            if is_end_date_passed and all_matches_played:
                logger.info(f"Season {current_season.number} has ended. Starting end-season process...")

                unfinished_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress']
                ).count()
                
                if unfinished_matches > 0:
                    return f"Season {current_season.number} has {unfinished_matches} unfinished matches"

                logger.info("Processing teams transitions between divisions...")
                call_command('handle_season_transitions')

                current_season.is_active = False
                current_season.save()

                logger.info("Creating new season...")
                call_command('create_new_season')

                new_season = Season.objects.get(is_active=True)
                championships = Championship.objects.filter(season=new_season)
                total_teams = sum(c.teams.count() for c in championships)

                return (
                    f"Season {current_season.number} ended successfully. "
                    f"Created new season {new_season.number} with "
                    f"{championships.count()} championships and {total_teams} teams"
                )

            return f"Season {current_season.number} is still active"

    except Season.DoesNotExist:
        logger.warning("No active season found")
        return "No active season found"
    except Exception as e:
        logger.error(f"Error in season end check: {str(e)}")
        raise

def extract_player_ids_from_lineup(current_lineup):
    """
    Извлекает ID игроков из состава любого формата.
    
    Поддерживает оба формата:
    Старый: {"0": "8012", ...}
    Новый: {"0": {"playerId": "8012", ...}, ...}
    """
    player_ids = set()
    if not current_lineup:
        return player_ids
        
    for slot_val in current_lineup.values():
        if isinstance(slot_val, dict):
            # Новый формат
            pid_str = slot_val.get('playerId')
            if pid_str:
                try:
                    player_ids.add(int(pid_str))
                except ValueError:
                    logger.warning(f"Invalid playerId format: {pid_str}")
        else:
            # Старый формат
            try:
                player_ids.add(int(slot_val))
            except ValueError:
                logger.warning(f"Invalid player id in old format: {slot_val}")
    
    return player_ids


def complete_lineup(club, current_lineup):
    """Дополняет состав, гарантированно избегая дублирования игроков"""
    # Получаем всех доступных игроков
    available_players = list(club.player_set.all())
    if len(available_players) < 11:
        return None

    new_lineup = {}
    used_players = []  # Будем хранить использованных игроков здесь

    # 1. Сначала ставим вратаря
    goalkeepers = [p for p in available_players if p.position == 'Goalkeeper']
    if not goalkeepers:
        return None

    keeper = goalkeepers[0]
    new_lineup['0'] = {
        "playerId": str(keeper.id),
        "slotType": "goalkeeper",
        "slotLabel": "GK",
        "playerPosition": "Goalkeeper"
    }
    available_players.remove(keeper)
    used_players.append(keeper)

    # 2. Теперь остальные позиции
    current_slot = 1
    positions_needed = [
        (2, ['Center Back']),  # 2 центральных защитника
        (2, ['Left Back', 'Right Back']),  # 2 крайних защитника
        (3, ['Central Midfielder', 'Defensive Midfielder', 'Attacking Midfielder']),  # 3 полузащитника
        (2, ['Left Midfielder', 'Right Midfielder']),  # 2 крайних полузащитника
        (1, ['Center Forward'])  # 1 нападающий
    ]

    for count, possible_positions in positions_needed:
        # Находим игроков на нужных позициях
        candidates = [p for p in available_players if p.position in possible_positions]
        # Берем столько игроков, сколько нужно (или сколько есть)
        selected = candidates[:count] if len(candidates) <= count else random.sample(candidates, count)
        
        for player in selected:
            if player in available_players:  # Дополнительная проверка
                new_lineup[str(current_slot)] = {
                    "playerId": str(player.id),
                    "slotType": "auto",
                    "slotLabel": f"AUTO{current_slot}",
                    "playerPosition": player.position
                }
                available_players.remove(player)
                used_players.append(player)
                current_slot += 1

    # Проверяем, что у нас полный состав
    if len(new_lineup) == 11:
        # Дополнительная проверка на дубликаты
        player_ids = [int(data['playerId']) for data in new_lineup.values()]
        if len(set(player_ids)) == 11:
            return new_lineup

    return None


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи из scheduled в in_progress и копирует составы команд.
    Автоматически дополняет неполные составы случайными игроками из клуба.
    """
    now = timezone.now()
    logger.info("===== STARTING start_scheduled_matches TASK =====")

    with transaction.atomic():
        matches = Match.objects.select_for_update().filter(
            status='scheduled',
            datetime__lte=now
        )
        count = matches.count()

        if count == 0:
            logger.info("No scheduled matches ready to start.")
            return "0 matches started."

        logger.info(f"Found {count} scheduled matches ready to start.")

        for match in matches:
            logger.info(f"Processing match ID={match.id}: {match.home_team} vs {match.away_team}")

            # Получаем lineup домашней команды
            home_data = match.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
            if not isinstance(home_data, dict):
                home_data = {"lineup": {}, "tactic": "balanced"}
            home_lineup = home_data.get('lineup', {})

            if len(home_lineup) < 11:
                new_home_lineup = complete_lineup(match.home_team, home_lineup)
                if new_home_lineup is None:
                    logger.warning(f"Not enough players in home team {match.home_team.name}. Cannot start match={match.id}.")
                    continue
                home_lineup = new_home_lineup

            match.home_lineup = home_lineup
            match.home_tactic = home_data.get('tactic', 'balanced')

            # Получаем lineup гостевой команды
            away_data = match.away_team.lineup or {"lineup": {}, "tactic": "balanced"}
            if not isinstance(away_data, dict):
                away_data = {"lineup": {}, "tactic": "balanced"}
            away_lineup = away_data.get('lineup', {})

            if len(away_lineup) < 11:
                new_away_lineup = complete_lineup(match.away_team, away_lineup)
                if new_away_lineup is None:
                    logger.warning(f"Not enough players in away team {match.away_team.name}. Cannot start match={match.id}.")
                    continue
                away_lineup = new_away_lineup

            match.away_lineup = away_lineup
            match.away_tactic = away_data.get('tactic', 'balanced')

            # Переводим статус матча в in_progress
            match.status = 'in_progress'
            match.save()

            logger.info(
                f"Match {match.id} is now in_progress. "
                f"home_lineup={match.home_lineup}, away_lineup={match.away_lineup} "
                f"home_tactic={match.home_tactic}, away_tactic={match.away_tactic}"
            )

    return f"{count} matches started."