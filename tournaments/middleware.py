# tournaments/middleware.py
from django.utils import timezone
from datetime import timedelta
from matches.models import Match
from matches.match_simulation import simulate_match
import logging

logger = logging.getLogger('matches')

class MatchSimulationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_check = timezone.now()
        self.check_interval = timedelta(seconds=10)  # Уменьшим интервал для тестирования
        logger.info("Match simulation middleware initialized")

    def __call__(self, request):
        now = timezone.now()
        
        # Добавим подробное логирование
        logger.info(f"Checking matches at {now}")
        logger.info(f"Last check was at {self.last_check}")
        
        if now - self.last_check >= self.check_interval:
            logger.info("Starting match check...")
            self.check_matches()
            self.last_check = now
            
        return self.get_response(request)

    def check_matches(self):
        now = timezone.now()
        matches = Match.objects.filter(
            status='scheduled',
            datetime__lte=now
        ).select_related('home_team', 'away_team')

        logger.info(f"Found {matches.count()} matches to check")
        
        for match in matches:
            try:
                logger.info(f"Simulating match: {match.home_team} vs {match.away_team}")
                simulate_match(match.id)
                
                # Перезагружаем матч для получения результата
                match.refresh_from_db()
                logger.info(
                    f"Match simulated: {match.home_team} {match.home_score} - {match.away_score} {match.away_team}"
                )
            except Exception as e:
                logger.error(f"Error simulating match {match.id}: {str(e)}")