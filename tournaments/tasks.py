from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.core.management import call_command
from matches.models import Match
from matches.match_simulation import simulate_match
from django.db import models
from .models import Season, Championship
import logging

logger = logging.getLogger(__name__)

@shared_task(
    name='tournaments.check_and_simulate_matches',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 60}
)
def check_and_simulate_matches(self):
    """
    Проверяет и симулирует матчи для обоих дивизионов
    """
    try:
        now = timezone.now()
        logger.info(f"Checking matches at {now}")
        
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
        ))
        
        logger.info(f"Found {matches.count()} matches to simulate")
        
        simulated_count = {'div1': 0, 'div2': 0}
        for match in matches:
            try:
                championship_match = match.championshipmatch
                division = championship_match.championship.league.level
                logger.info(f"Simulating Division {division} match: {match.home_team} vs {match.away_team}")
                
                simulate_match(match.id)
                
                # Учитываем статистику по дивизионам
                if division == 1:
                    simulated_count['div1'] += 1
                else:
                    simulated_count['div2'] += 1
                    
            except Exception as e:
                logger.error(f"Error simulating match {match.id}: {str(e)}")
                raise  # Для автоматических повторных попыток
        
        logger.info(
            f"Simulated {simulated_count['div1']} matches in Division 1, "
            f"{simulated_count['div2']} matches in Division 2"
        )
        return (f"Successfully simulated {sum(simulated_count.values())} matches "
                f"({simulated_count['div1']} in Div1, {simulated_count['div2']} in Div2)")
        
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
            # Блокируем текущий сезон
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()
            
            logger.info(f"Checking season {current_season.number} end date: {current_season.end_date}")
            
            # Если сезон закончился
            if today > current_season.end_date:
                # 1. Проверяем, что все матчи завершены
                active_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress']
                ).count()
                
                if active_matches > 0:
                    logger.warning(f"Found {active_matches} unfinished matches")
                    return f"Season {current_season.number} has {active_matches} unfinished matches"
                
                # 2. Обрабатываем переходы между дивизионами
                logger.info("Starting season transitions")
                call_command('handle_season_transitions')
                
                # 3. Делаем текущий сезон неактивным
                current_season.is_active = False
                current_season.save()
                logger.info(f"Deactivated season {current_season.number}")
                
                # 4. Создаем новый сезон
                new_season_number = current_season.number + 1
                new_season = Season.objects.create(
                    number=new_season_number,
                    name=f"Season {new_season_number}",
                    start_date=today,  # или рассчитать нужную дату
                    end_date=today + timezone.timedelta(days=30),  # или рассчитать нужную дату
                    is_active=True
                )
                logger.info(f"Created new season {new_season.number}")
                
                # 5. Создаем чемпионаты для нового сезона
                logger.info("Creating championships for new season")
                call_command('create_new_season')
                
                return (f"Season {current_season.number} ended. "
                       f"Created new season {new_season.number}")
            
            return f"Season {current_season.number} is still active"
            
    except Season.DoesNotExist:
        logger.warning("No active season found")
        return "No active season found"
    except Exception as e:
        logger.error(f"Error checking season end: {str(e)}")
        raise  # Для автоматических повторных попыток