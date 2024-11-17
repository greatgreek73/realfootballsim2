from celery import shared_task
from django.utils import timezone
from matches.models import Match
from matches.match_simulation import simulate_match
from django.db import models
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
        
        simulated_count = {'div1': 0, 'div2': 0}
        for match in matches:
            try:
                championship_match = match.championshipmatch
                division = championship_match.championship.league.level
                logger.info(
                    f"Simulating Division {division} match: "
                    f"{match.home_team} vs {match.away_team}"
                )
                simulate_match(match.id)
                
                # Учитываем статистику по дивизионам
                if division == 1:
                    simulated_count['div1'] += 1
                else:
                    simulated_count['div2'] += 1
                    
            except Exception as e:
                logger.error(f"Error simulating match {match.id}: {str(e)}")
                raise  # Позволяем механизму повторных попыток обработать ошибку
        
        logger.info(
            f"Simulated {simulated_count['div1']} matches in Division 1, "
            f"{simulated_count['div2']} matches in Division 2"
        )
        return (f"Successfully simulated {sum(simulated_count.values())} matches "
                f"({simulated_count['div1']} in Div1, {simulated_count['div2']} in Div2)")
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise

@shared_task
def check_season_end():
    """Проверяет, не закончился ли текущий сезон"""
    from .models import Season
    from django.core.management import call_command
    
    try:
        current_season = Season.objects.get(is_active=True)
        today = timezone.now().date()
        
        # Если сезон закончился
        if today > current_season.end_date:
            logger.info(f"Season {current_season} has ended. Starting end season process...")
            # Запускаем команду окончания сезона
            call_command('end_season')
            logger.info("End season process completed")
            
    except Season.DoesNotExist:
        logger.warning("No active season found")
    except Exception as e:
        logger.error(f"Error checking season end: {str(e)}")