# tournaments/management/commands/check_matches.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from matches.models import Match
from matches.match_simulation import simulate_match
import logging
from datetime import datetime

logger = logging.getLogger('matches')

class Command(BaseCommand):
    help = 'Checks and simulates matches that should start now'

    def add_arguments(self, parser):
        # Добавляем опциональный аргумент для тестирования
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print additional debug information',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        debug = options['debug']

        if debug:
            self.stdout.write(f'Current time: {now}')
            logger.info(f'Starting match check at {now}')

        # Находим матчи, которые должны были начаться
        matches = Match.objects.filter(
            status='scheduled',
            datetime__lte=now
        ).select_related('home_team', 'away_team')

        if debug:
            self.stdout.write(f'Found {matches.count()} matches to simulate')
            for match in matches:
                self.stdout.write(
                    f'- {match.datetime}: {match.home_team} vs {match.away_team}'
                )

        if matches.exists():
            logger.info(f'Found {matches.count()} matches to simulate')
            
            for match in matches:
                try:
                    msg = f'Simulating match: {match.home_team} vs {match.away_team} (scheduled for {match.datetime})'
                    self.stdout.write(msg)
                    logger.info(msg)
                    
                    simulate_match(match.id)
                    
                    logger.info(
                        f'Match completed: {match.home_team} {match.home_score} - {match.away_score} {match.away_team}'
                    )
                except Exception as e:
                    error_msg = f'Error simulating match {match.id}: {str(e)}'
                    self.stdout.write(self.style.ERROR(error_msg))
                    logger.error(error_msg)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully simulated {matches.count()} matches')
            )
        else:
            if debug:
                self.stdout.write('No matches to simulate')