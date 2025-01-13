# C:\realfootballsim\tournaments\tasks.py

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

            # Допустим у нас 16 команд, каждая играет 15 туров * 2 круга = 30, итого 16 * 15 (т.к. каждая пара считает лишь один раз)
            required_matches = (
                len(Championship.objects.filter(season=current_season)) * (16 * 15)
            )
            all_matches_played = finished_matches_count >= required_matches

            if is_end_date_passed and all_matches_played:
                logger.info(f"Season {current_season.number} has ended. Starting end-season process...")

                # Проверяем, не остались ли незавершенные матчи
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


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи из scheduled в in_progress и копирует составы команд.
    Автоматически дополняет неполные составы случайными игроками из клуба.
    """

    def complete_lineup(club, current_lineup):
        """
        Дополняет неполный состав случайными игроками из клуба.
        
        current_lineup может содержать либо строки (старый формат),
        либо словари вида:
            {
                "playerId": "8012",
                "slotType": "...",
                ...
            }
        Нужно извлекать из этого словаря именно playerId и приводить к int.
        """
        # 1) Определяем, используется ли формат "dict" (playerId) или старый
        #    Сделаем проверку по первому элементу, если он есть.
        is_new_format = False
        if current_lineup:
            any_val = next(iter(current_lineup.values()))
            if isinstance(any_val, dict):
                is_new_format = True

        # 2) Собираем ID уже занятых игроков
        used_ids = set()
        for slot_key, slot_val in current_lineup.items():
            if isinstance(slot_val, dict):
                # Новый формат
                pid_str = slot_val.get('playerId')
                if pid_str is not None:
                    used_ids.add(int(pid_str))
            else:
                # Старый формат
                used_ids.add(int(slot_val))

        # 3) Получаем всех доступных игроков клуба
        available_players = list(
            Player.objects.filter(club=club)
            .exclude(id__in=used_ids)
            .values_list('id', flat=True)
        )

        # 4) Сколько недостает игроков?
        slots_needed = 11 - len(current_lineup)
        if len(available_players) < slots_needed:
            return None  # Недостаточно игроков

        # 5) Рандомно добавляем нужное число
        random_players = random.sample(available_players, slots_needed)
        next_pos = len(current_lineup)

        for player_id in random_players:
            if is_new_format:
                # Создаем запись в виде dict
                current_lineup[str(next_pos)] = {
                    "playerId": str(player_id),
                    # Остальные поля можно заполнить пустыми или как угодно
                    "slotType": "auto_filled",
                    "slotLabel": f"AUTO{next_pos}",
                    "playerPosition": ""  # Можно попытаться вычислить из Player, если нужно
                }
            else:
                # Старый формат: просто строка
                current_lineup[str(next_pos)] = str(player_id)

            next_pos += 1

        return current_lineup

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

            # Обработка состава домашней команды
            home_data = match.home_team.lineup
            if not home_data or not isinstance(home_data, dict):
                home_data = {"lineup": {}}

            home_lineup = home_data.get('lineup', {})
            if len(home_lineup) < 11:
                new_home_lineup = complete_lineup(match.home_team, home_lineup)
                if new_home_lineup is None:
                    return '0 matches started: not enough players in home team'
                home_lineup = new_home_lineup

            match.home_lineup = home_lineup
            match.home_tactic = home_data.get('tactic', 'balanced')

            # Обработка состава гостевой команды
            away_data = match.away_team.lineup
            if not away_data or not isinstance(away_data, dict):
                away_data = {"lineup": {}}

            away_lineup = away_data.get('lineup', {})
            if len(away_lineup) < 11:
                new_away_lineup = complete_lineup(match.away_team, away_lineup)
                if new_away_lineup is None:
                    return '0 matches started: not enough players in away team'
                away_lineup = new_away_lineup

            match.away_lineup = away_lineup
            match.away_tactic = away_data.get('tactic', 'balanced')

            # Обновляем статус и сохраняем
            match.status = 'in_progress'
            match.save()

            logger.info(
                f"Match {match.id} is now in_progress. "
                f"home_lineup={match.home_lineup}, away_lineup={match.away_lineup} "
                f"home_tactic={match.home_tactic}, away_tactic={match.away_tactic}"
            )

    return f"{count} matches started."
