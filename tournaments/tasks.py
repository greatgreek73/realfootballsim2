from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.core.management import call_command
from matches.models import Match
from django.db import models
from .models import Season, Championship, League
import logging
from datetime import timedelta
import time
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

def retry_on_db_lock(func, max_attempts=3, delay=1):
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

@shared_task(
    name='tournaments.simulate_active_matches',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def simulate_active_matches(self):
    """
    Пошаговая симуляция матчей.
    Каждые 5 секунд (или другой интервал) задача проверяет матчи, находящиеся в статусе 'in_progress',
    и симулирует одну игровую минуту для каждого такого матча.
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
        logger.info(f"Simulated one minute for match {match.id} "
                    f"({match.home_team} vs {match.away_team}, current_minute={match.current_minute})")

    return f"Simulated one minute for {matches.count()} matches"


@shared_task(
    name='tournaments.check_season_end',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def check_season_end(self):
    """
    Проверяет окончание сезона и при необходимости завершает его,
    затем создаёт новый сезон.
    """
    try:
        with transaction.atomic():
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()
            
            logger.info(f"Checking season {current_season.number} (end date: {current_season.end_date})")
            
            is_end_date_passed = today > current_season.end_date
            
            finished_matches_count = Match.objects.filter(
                championshipmatch__championship__season=current_season,
                status='finished'
            ).count()

            required_matches = len(Championship.objects.filter(season=current_season)) * (16 * 15)
            
            all_matches_played = finished_matches_count >= required_matches

            if is_end_date_passed and all_matches_played:
                logger.info(f"Season {current_season.number} has ended. Starting end-season process...")
                
                unfinished_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress']
                )
                
                unfinished_count = unfinished_matches.count()
                if unfinished_count > 0:
                    logger.warning(
                        f"Found {unfinished_count} unfinished matches. "
                        "Season cannot end with unfinished matches."
                    )
                    return (f"Season {current_season.number} has {unfinished_count} unfinished matches")
                
                logger.info("Processing teams transitions between divisions...")
                call_command('handle_season_transitions')
                
                current_season.is_active = False
                current_season.save()
                logger.info(f"Deactivated season {current_season.number}")
                
                logger.info("Creating new season...")
                call_command('create_new_season')
                
                try:
                    new_season = Season.objects.get(is_active=True)
                    logger.info(f"Successfully created new season {new_season.number}")
                    
                    championships = Championship.objects.filter(season=new_season)
                    total_teams = sum(c.teams.count() for c in championships)
                    
                    return (
                        f"Season {current_season.number} ended successfully. "
                        f"Created new season {new_season.number} with "
                        f"{championships.count()} championships and {total_teams} teams"
                    )
                except Season.DoesNotExist:
                    error_msg = "Failed to create new season"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                except Season.MultipleObjectsReturned:
                    error_msg = "Multiple active seasons found after creation"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            if not all_matches_played:
                return f"Season {current_season.number} is waiting for matches completion ({finished_matches_count}/{required_matches})"
            if not is_end_date_passed:
                return f"Season {current_season.number} is still active until {current_season.end_date}"
            return f"Season {current_season.number} needs both end date and all matches to end"
            
    except Season.DoesNotExist:
        logger.warning("No active season found")
        return "No active season found"
    except Exception as e:
        logger.error(f"Error in season end check: {str(e)}")
        raise


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи, для которых время уже наступило, из scheduled в in_progress.
    Таким образом, если есть прошлые или текущие матчи, которые не начались (хотя должны были),
    они теперь начнутся, и simulate_active_matches сможет их симулировать.
    """
    now = timezone.now()
    with transaction.atomic():
        matches = Match.objects.select_for_update().filter(
            status='scheduled',
            datetime__lte=now
        )
        count = matches.count()
        if count > 0:
            logger.info(f"Found {count} scheduled matches ready to start.")
            matches.update(status='in_progress')
        else:
            logger.info("No scheduled matches ready to start.")
    return f"{count} matches started."
