from django.core.management.base import BaseCommand
from django.utils import timezone
from matches.models import Match
from clubs.models import Club
from tournaments.tasks import start_scheduled_matches, simulate_active_matches
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates and simulates a test match'

    def handle(self, *args, **kwargs):
        # 1. Создаем тестовый матч
        clubs = Club.objects.all()[:2]
        if len(clubs) < 2:
            self.stdout.write(self.style.ERROR('Need at least 2 clubs in database'))
            return

        home_team, away_team = clubs[0], clubs[1]
        match = Match.objects.create(
            home_team=home_team,
            away_team=away_team,
            datetime=timezone.now(),
            status='scheduled'
        )

        self.stdout.write(f"\nCreated test match #{match.id}:")
        self.stdout.write(f"Home team: {home_team.name}")
        self.stdout.write(f"Away team: {away_team.name}")
        self.stdout.write(f"Initial status: {match.status}")

        # 2. Запускаем start_scheduled_matches для перевода в in_progress
        self.stdout.write("\nStarting the match...")
        result = start_scheduled_matches()
        self.stdout.write(f"start_scheduled_matches result: {result}")

        # Перечитываем матч из базы
        match.refresh_from_db()
        self.stdout.write(f"\nMatch status after start: {match.status}")
        self.stdout.write(f"Home lineup: {match.home_lineup}")
        self.stdout.write(f"Away lineup: {match.away_lineup}")

        # 3. Симулируем несколько минут
        if match.status == 'in_progress':
            self.stdout.write("\nSimulating first 5 minutes...")
            for _ in range(5):
                result = simulate_active_matches()
                self.stdout.write(f"Simulated minute, result: {result}")
                time.sleep(1)  # Пауза в 1 секунду между минутами

            # Финальный статус
            match.refresh_from_db()
            self.stdout.write(f"\nFinal match status:")
            self.stdout.write(f"Status: {match.status}")
            self.stdout.write(f"Score: {match.home_score} - {match.away_score}")
            self.stdout.write(f"Current minute: {match.current_minute}")
