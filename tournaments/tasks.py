from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.core.management import call_command
from matches.models import Match
from matches.match_simulation import simulate_match
from django.db import models
from .models import Season, Championship, League
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

@shared_task(
    name='tournaments.check_and_simulate_matches',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 60},
    default_retry_delay=300  # 5 минут между повторами
)
def check_and_simulate_matches(self):
    """
    Проверяет и симулирует матчи для обоих дивизионов
    """
    try:
        now = timezone.now()
        logger.info(f"Starting match check at {now}")
        
        # Проверяем наличие активного сезона
        if not Season.objects.filter(is_active=True).exists():
            logger.warning("No active season found, skipping match simulation")
            return "No active season found"
        
        # Получаем все матчи, время которых наступило
        matches = (Match.objects.filter(
            status='scheduled',
            date__lte=now
        ).select_related(
            'home_team', 
            'away_team',
            'championshipmatch',
            'championshipmatch__championship',
            'championshipmatch__championship__league'
        ).order_by('date'))  # Сортируем по дате для последовательной симуляции
        
        if not matches.exists():
            logger.info("No matches to simulate")
            return "No matches to simulate"
        
        logger.info(f"Found {matches.count()} matches to simulate")
        
        simulated_count = {'div1': 0, 'div2': 0}
        errors_count = 0
        
        for match in matches:
            try:
                championship_match = match.championshipmatch
                division = championship_match.championship.league.level
                
                # Дополнительные проверки
                if not championship_match.championship.season.is_active:
                    logger.warning(f"Match {match.id} belongs to inactive season, skipping")
                    continue
                
                logger.info(
                    f"Simulating Division {division} match: "
                    f"{match.home_team} vs {match.away_team} "
                    f"(ID: {match.id})"
                )
                
                with transaction.atomic():
                    simulate_match(match.id)
                    
                    if division == 1:
                        simulated_count['div1'] += 1
                    else:
                        simulated_count['div2'] += 1
                
            except Exception as e:
                errors_count += 1
                logger.error(f"Error simulating match {match.id}: {str(e)}")
                if errors_count >= 3:  # Если слишком много ошибок
                    raise Exception("Too many simulation errors")
                continue
        
        result_message = (
            f"Simulated {sum(simulated_count.values())} matches "
            f"({simulated_count['div1']} in Div1, {simulated_count['div2']} in Div2)"
        )
        if errors_count > 0:
            result_message += f" with {errors_count} errors"
            
        logger.info(result_message)
        return result_message
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise

@shared_task(
    name='tournaments.check_season_end',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def check_season_end(self):
    """Проверяет окончание сезона и запускает необходимые процессы"""
    try:
        with transaction.atomic():
            # Блокируем текущий сезон для изменений
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()
            
            logger.info(f"Checking season {current_season.number} (end date: {current_season.end_date})")
            
            # Проверяем, закончился ли сезон
            if today > current_season.end_date:
                logger.info(f"Season {current_season.number} has ended. Starting end-season process...")
                
                # 1. Проверяем незавершенные матчи
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
                    return (f"Season {current_season.number} has "
                           f"{unfinished_count} unfinished matches")
                
                # 2. Обрабатываем переходы между дивизионами
                logger.info("Processing teams transitions between divisions...")
                call_command('handle_season_transitions')
                
                # 3. Деактивируем текущий сезон
                current_season.is_active = False
                current_season.save()
                logger.info(f"Deactivated season {current_season.number}")
                
                # 4. Создаём новый сезон через команду
                logger.info("Creating new season...")
                call_command('create_new_season')
                
                # 5. Проверяем успешность создания нового сезона
                try:
                    new_season = Season.objects.get(is_active=True)
                    logger.info(f"Successfully created new season {new_season.number}")
                    
                    # Подсчитываем количество чемпионатов и команд
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
            
            return f"Season {current_season.number} is still active until {current_season.end_date}"
            
    except Season.DoesNotExist:
        logger.warning("No active season found")
        return "No active season found"
    except Exception as e:
        logger.error(f"Error in season end check: {str(e)}")
        raise