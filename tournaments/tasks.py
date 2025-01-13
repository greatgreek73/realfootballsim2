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
    """Дополняет неполный состав, используя более гибкие правила позиций."""
    # Создаем множество уже использованных ID
    used_ids = set()
    
    # Получаем всех доступных игроков и их позиции
    available_players = {}
    all_players = list(club.player_set.all())
    for player in all_players:
        if player.position not in available_players:
            available_players[player.position] = []
        available_players[player.position].append({
            'id': player.id,
            'position': player.position
        })

    new_lineup = {}
    next_slot = 0

    # 1. Сначала вратарь
    if 'Goalkeeper' in available_players and available_players['Goalkeeper']:
        keeper = available_players['Goalkeeper'][0]
        new_lineup['0'] = {
            "playerId": str(keeper['id']),
            "slotType": "goalkeeper",
            "slotLabel": "GK",
            "playerPosition": "Goalkeeper"
        }
        used_ids.add(keeper['id'])
        next_slot = 1

    # 2. Далее защитники
    defenders = []
    for pos in ['Center Back', 'Left Back', 'Right Back']:
        if pos in available_players:
            defenders.extend(available_players[pos])
    
    needed_defenders = min(4, len(defenders))
    selected_defenders = random.sample(defenders, needed_defenders)
    for defender in selected_defenders:
        if defender['id'] not in used_ids:
            new_lineup[str(next_slot)] = {
                "playerId": str(defender['id']),
                "slotType": "auto",
                "slotLabel": f"AUTO{next_slot}",
                "playerPosition": defender['position']
            }
            used_ids.add(defender['id'])
            next_slot += 1

    # 3. Полузащитники
    midfielders = []
    for pos in ['Central Midfielder', 'Defensive Midfielder', 'Attacking Midfielder', 'Left Midfielder', 'Right Midfielder']:
        if pos in available_players:
            midfielders.extend([m for m in available_players[pos] if m['id'] not in used_ids])
    
    needed_midfielders = min(4, len(midfielders))
    selected_midfielders = random.sample(midfielders, needed_midfielders)
    for midfielder in selected_midfielders:
        if midfielder['id'] not in used_ids:
            new_lineup[str(next_slot)] = {
                "playerId": str(midfielder['id']),
                "slotType": "auto",
                "slotLabel": f"AUTO{next_slot}",
                "playerPosition": midfielder['position']
            }
            used_ids.add(midfielder['id'])
            next_slot += 1

    # 4. Нападающие
    forwards = []
    for pos in ['Center Forward']:
        if pos in available_players:
            forwards.extend([f for f in available_players[pos] if f['id'] not in used_ids])
    
    needed_forwards = min(2, len(forwards))
    selected_forwards = random.sample(forwards, needed_forwards) if forwards else []
    for forward in selected_forwards:
        if forward['id'] not in used_ids:
            new_lineup[str(next_slot)] = {
                "playerId": str(forward['id']),
                "slotType": "auto",
                "slotLabel": f"AUTO{next_slot}",
                "playerPosition": forward['position']
            }
            used_ids.add(forward['id'])
            next_slot += 1

    # Если не хватает игроков, добавляем любых доступных
    while next_slot < 11:
        available = [p for p in all_players if p.id not in used_ids]
        if not available:
            return None
        
        player = random.choice(available)
        new_lineup[str(next_slot)] = {
            "playerId": str(player.id),
            "slotType": "auto",
            "slotLabel": f"AUTO{next_slot}",
            "playerPosition": player.position
        }
        used_ids.add(player.id)
        next_slot += 1

    return new_lineup

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