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
    Запускается периодически (например, каждые 5 секунд).
    """
    now = timezone.now()
    logger.info(f"Starting active matches simulation at {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("No matches in progress at the moment.")
        return "No matches in progress"

    from matches.match_simulation import simulate_one_minute

    for match in matches:
        umatch = simulate_one_minute(match)
        umatch.save()
        logger.info(
            f"Simulated one minute for match {match.id} "
            f"({umatch.home_team} vs {umatch.away_team}, current_minute={umatch.current_minute})"
        )

    return f"Simulated one minute for {matches.count()} matches"


@shared_task(name='tournaments.check_season_end', bind=True)
def check_season_end(self):
    """
    Проверяет окончание сезона и создаёт новый при необходимости.
    Запускается, к примеру, раз в день или раз в час (согласно настройкам Celery Beat).
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

            # Примерный расчёт: 16 команд * (15 туров), если двойной круг - 16*15=240, плюс количество чемпионатов
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
    Извлекает ID игроков из состава любого формата (старый/новый).
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
            # Старый формат: "8012"
            try:
                player_ids.add(int(slot_val))
            except ValueError:
                logger.warning(f"Invalid player id in old format: {slot_val}")

    return player_ids


def complete_lineup(club, current_lineup):
    """
    Дополняет состав без дублирования игроков, используя простую логику:
    1) Ищет вратаря (обязательно).
    2) Заполняет остальные 10 слотов случайными игроками из клуба.
    3) Не учитывает точные позиции (кроме GK).
    """

    # Получаем всех игроков клуба
    all_players = list(club.player_set.all())
    if len(all_players) < 11:
        # Если игроков меньше 11, невозможно сформировать состав
        return None

    new_lineup = {}
    used_ids = set()

    # --- 1) Ставим вратаря (если есть) ---
    goalkeepers = [p for p in all_players if p.position == 'Goalkeeper']
    if not goalkeepers:
        logger.warning(f"No Goalkeeper in club {club.name}")
        return None

    keeper = goalkeepers[0]  # Берём первого попавшегося GK
    new_lineup['0'] = {
        "playerId": str(keeper.id),
        "slotType": "goalkeeper",
        "slotLabel": "GK",
        "playerPosition": keeper.position
    }
    used_ids.add(keeper.id)
    all_players.remove(keeper)  # исключаем из пула

    # --- 2) Заполняем остальные 10 слотов любыми игроками ---
    if len(all_players) < 10:
        logger.warning(f"Club {club.name} doesn't have enough players after removing GK")
        return None

    chosen_others = random.sample(all_players, 10)
    slot_index = 1
    for player in chosen_others:
        new_lineup[str(slot_index)] = {
            "playerId": str(player.id),
            "slotType": "auto",
            "slotLabel": f"AUTO{slot_index}",
            "playerPosition": player.position
        }
        used_ids.add(player.id)
        slot_index += 1

    # Проверяем, что в итоге у нас 11 уникальных игроков
    if len(new_lineup) == 11 and len(used_ids) == 11:
        return new_lineup
    else:
        logger.warning(f"Could not form a unique 11-player lineup for {club.name}")
        return None


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи из scheduled в in_progress и копирует составы команд.
    Автоматически дополняет неполные составы (до 11 игроков), если они меньше 11.
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

            # Обрабатываем домашнюю команду
            home_data = match.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
            if not isinstance(home_data, dict):
                home_data = {"lineup": {}, "tactic": "balanced"}
            home_lineup = home_data.get('lineup', {})

            if len(home_lineup) < 11:
                completed_home = complete_lineup(match.home_team, home_lineup)
                if completed_home is None:
                    logger.warning(
                        f"Home team {match.home_team.name} cannot form 11 players. "
                        f"Skipping match {match.id}."
                    )
                    continue
                home_lineup = completed_home

            match.home_lineup = home_lineup
            match.home_tactic = home_data.get('tactic', 'balanced')

            # Обрабатываем гостевую команду
            away_data = match.away_team.lineup or {"lineup": {}, "tactic": "balanced"}
            if not isinstance(away_data, dict):
                away_data = {"lineup": {}, "tactic": "balanced"}
            away_lineup = away_data.get('lineup', {})

            if len(away_lineup) < 11:
                completed_away = complete_lineup(match.away_team, away_lineup)
                if completed_away is None:
                    logger.warning(
                        f"Away team {match.away_team.name} cannot form 11 players. "
                        f"Skipping match {match.id}."
                    )
                    continue
                away_lineup = completed_away

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
