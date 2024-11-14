from celery import shared_task
from django.utils import timezone
from matches.models import Match
from matches.match_simulation import simulate_match
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
    Проверяет и симулирует матчи, время которых наступило
    """
    try:
        now = timezone.now()
        logger.info(f"Checking matches at {now}")
        
        matches = Match.objects.filter(
            status='scheduled',
            date__lte=now
        ).select_related('home_team', 'away_team')
        
        simulated_count = 0
        for match in matches:
            try:
                logger.info(f"Simulating match: {match.home_team} vs {match.away_team}")
                simulate_match(match.id)
                simulated_count += 1
            except Exception as e:
                logger.error(f"Error simulating match {match.id}: {str(e)}")
                raise
        
        logger.info(f"Simulated {simulated_count} matches")
        return f"Successfully simulated {simulated_count} matches"
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise