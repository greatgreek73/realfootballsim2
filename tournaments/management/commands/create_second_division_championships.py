from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import League, Championship, Season
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates championships for second divisions in current season'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Получаем текущий активный сезон
                current_season = Season.objects.get(is_active=True)
                
                # Получаем все вторые дивизионы
                second_divisions = League.objects.filter(level=2)
                
                championships_created = 0
                for league in second_divisions:
                    # Проверяем, нет ли уже чемпионата для этой лиги в текущем сезоне
                    exists = Championship.objects.filter(
                        season=current_season,
                        league=league
                    ).exists()
                    
                    if not exists:
                        # Создаем чемпионат
                        championship = Championship.objects.create(
                            season=current_season,
                            league=league,
                            status='in_progress',
                            start_date=current_season.start_date,
                            end_date=current_season.end_date,
                            match_time=timezone.now().time().replace(hour=18, minute=0)
                        )
                        
                        # Добавляем все команды лиги в чемпионат
                        for club in league.clubs.all():
                            championship.teams.add(club)
                            
                        championships_created += 1
                        self.stdout.write(f"Created championship for {league.name}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {championships_created} championships'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating championships: {str(e)}')
            )