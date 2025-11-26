from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date
from tournaments.models import Season, Championship, ChampionshipMatch
from tournaments.utils import create_championship_matches
from matches.match_simulation import simulate_match
from matches.models import Match
from clubs.models import Club

class Command(BaseCommand):
    help = 'Resets and creates new first season starting from November 2024'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 1. Удаляем все существующие сезоны и связанные данные
                self.stdout.write("Deleting existing seasons and matches...")
                Season.objects.all().delete()  # Это также удалит связанные чемпионаты и матчи

                # 2. Создаем новый первый сезон
                season = Season.objects.create(
                    name="November 2024",
                    number=1,  # Первый сезон
                    start_date=date(2024, 11, 1),
                    end_date=date(2025, 5, 31),
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f"Created new season: {season.name}"))

                # 3. Создаем чемпионаты для всех лиг
                from tournaments.models import League
                leagues = League.objects.all()
                championships_created = 0

                for league in leagues:
                    # Получаем команды для этой лиги
                    bot_teams = Club.objects.filter(league=league, is_bot=True)
                    human_teams = Club.objects.filter(league=league, is_bot=False)
                    total_teams = bot_teams.count() + human_teams.count()
                    
                    # Проверяем, что в лиге ровно 16 команд (боты + человеческие)
                    if total_teams != 16:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping {league.name} - has {total_teams} teams "
                            f"({bot_teams.count()} bots, {human_teams.count()} human)"
                        ))
                        continue

                    championship = Championship.objects.create(
                        season=season,
                        league=league,
                        status='in_progress',  # Так как сезон уже идёт
                        start_date=season.start_date,
                        end_date=season.end_date
                    )
                    
                    # Добавляем все команды в чемпионат
                    for team in list(bot_teams) + list(human_teams):
                        championship.teams.add(team)

                    # Генерируем расписание
                    create_championship_matches(championship)
                    championships_created += 1

                self.stdout.write(self.style.SUCCESS(
                    f"Created {championships_created} championships"
                ))

                # 4. Симулируем матчи с 1 по 7 ноября
                # Используем timezone.make_aware для создания datetime с часовым поясом
                current_date = timezone.make_aware(
                    datetime(2024, 11, 8, 0, 0, 0)
                )
                
                past_matches = Match.objects.filter(
                    date__lt=current_date,
                    status='scheduled'
                )

                matches_simulated = 0
                for match in past_matches:
                    simulate_match(match.id)
                    matches_simulated += 1

                self.stdout.write(self.style.SUCCESS(
                    f"Simulated {matches_simulated} past matches"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error occurred: {str(e)}"))
            raise e

        self.stdout.write(self.style.SUCCESS("Season reset completed successfully!"))