from celery import shared_task
from django.utils import timezone
from .models import Match
from .match_simulation import simulate_one_minute
import logging

logger = logging.getLogger(__name__)

@shared_task(name='matches.simulate_match_minute')
def simulate_match_minute(match_id: int):
    """
    Симулирует одну минуту матча
    """
    try:
        simulate_one_minute(match_id)
        logger.info(f"Successfully simulated minute for match {match_id}")
    except Exception as e:
        logger.error(f"Error simulating minute for match {match_id}: {str(e)}")
        raise