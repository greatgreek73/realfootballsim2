from django.core.management.base import BaseCommand
from django.utils import timezone
import time
from matches.models import Match
from matches.match_simulation import simulate_match
import logging

logger = logging.getLogger('matches')

class Command(BaseCommand):
    help = 'Continuously checks and simulates matches'

    def handle(self, *args, **options):
        self.stdout.write('Starting match checker...')
        
        while True:
            try:
                now = timezone.now()
                self.stdout.write(f'Checking matches at {now}')
                
                # Находим матчи для симуляции
                matches = Match.objects.filter(
                    status='scheduled',
                    datetime__lte=now
                ).select_related('home_team', 'away_team')
                
                if matches.exists():
                    self.stdout.write(f'Found {matches.count()} matches to simulate')
                    
                    for match in matches:
                        try:
                            self.stdout.write(f'Simulating: {match.home_team} vs {match.away_team}')
                            simulate_match(match.id)
                            match.refresh_from_db()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Simulated: {match.home_team} {match.home_score} - {match.away_score} {match.away_team}'
                                )
                            )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error simulating match {match.id}: {str(e)}')
                            )
                
                # Ждем 10 секунд перед следующей проверкой
                time.sleep(10)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error in match checker: {str(e)}')
                )
                time.sleep(10)