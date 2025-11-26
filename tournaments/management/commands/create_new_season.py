from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from tournaments.models import Championship, Season, League
from tournaments.utils import create_championship_matches
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates new season with championships based on current league assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Duration of the season in days'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Находим последний сезон для определения номера нового
                last_season = Season.objects.order_by('-number').first()
                new_season_number = 1 if not last_season else last_season.number + 1
                
                # Определяем даты сезона
                start_date = timezone.now().date()
                duration = timedelta(days=options['days'])
                end_date = start_date + duration

                # Создаем новый сезон
                new_season = Season.objects.create(
                    number=new_season_number,
                    name=f"Season {new_season_number}",
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                
                self.stdout.write(f"Created new season: {new_season}")

                # Получаем все лиги
                leagues = League.objects.all().order_by('country', 'level')
                
                championships_created = 0
                matches_created = 0

                # Создаем чемпионаты для каждой лиги
                for league in leagues:
                    # Проверяем количество команд в лиге
                    teams_in_league = league.clubs.count()
                    if teams_in_league != 16:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping {league}: has {teams_in_league} teams instead of 16"
                            )
                        )
                        continue

                    # Создаем чемпионат
                    championship = Championship.objects.create(
                        season=new_season,
                        league=league,
                        status='pending',
                        start_date=start_date,
                        end_date=end_date
                    )

                    # Добавляем команды в чемпионат
                    for team in league.clubs.all():
                        championship.teams.add(team)

                    # Генерируем расписание матчей
                    create_championship_matches(championship)
                    
                    championships_created += 1
                    matches_created += championship.championshipmatch_set.count()

                    self.stdout.write(
                        f"Created championship for {league.name} with "
                        f"{championship.teams.count()} teams"
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created new season {new_season_number} with "
                        f"{championships_created} championships and "
                        f"{matches_created} matches"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error creating new season: {str(e)}")
            )
            raise