from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import League

class Command(BaseCommand):
    help = 'Initialize leagues for top 10 football countries'

    def handle(self, *args, **options):
        # Топ-10 футбольных стран
        TOP_LEAGUES = [
            {
                'country': 'GB',
                'div1_name': 'Premier League',
                'div2_name': 'Championship'
            },
            {
                'country': 'ES',
                'div1_name': 'La Liga',
                'div2_name': 'La Liga 2'
            },
            {
                'country': 'IT',
                'div1_name': 'Serie A',
                'div2_name': 'Serie B'
            },
            {
                'country': 'DE',
                'div1_name': 'Bundesliga',
                'div2_name': '2. Bundesliga'
            },
            {
                'country': 'FR',
                'div1_name': 'Ligue 1',
                'div2_name': 'Ligue 2'
            },
            {
                'country': 'PT',
                'div1_name': 'Primeira Liga',
                'div2_name': 'Liga Portugal 2'
            },
            {
                'country': 'GR',
                'div1_name': 'Super League',
                'div2_name': 'Super League 2'
            },
            {
                'country': 'RU',
                'div1_name': 'Premier League',
                'div2_name': 'First League'
            },
            {
                'country': 'AR',
                'div1_name': 'Primera División',
                'div2_name': 'Primera Nacional'
            },
            {
                'country': 'BR',
                'div1_name': 'Série A',
                'div2_name': 'Série B'
            },
        ]

        try:
            with transaction.atomic():
                # Удаляем все существующие лиги
                League.objects.all().delete()
                
                for league_info in TOP_LEAGUES:
                    # Создаем первый дивизион
                    League.objects.create(
                        name=f"{league_info['country']} {league_info['div1_name']}", # добавляем страну в название
                        country=league_info['country'],
                        level=1,
                        max_teams=16,
                        foreign_players_limit=5
                    )
                    self.stdout.write(
                        f"Created {league_info['div1_name']} for {league_info['country']}"
                    )
                    
                    # Создаем второй дивизион
                    League.objects.create(
                        name=f"{league_info['country']} {league_info['div2_name']}", # добавляем страну в название
                        country=league_info['country'],
                        level=2,
                        max_teams=16,
                        foreign_players_limit=5
                    )
                    self.stdout.write(
                        f"Created {league_info['div2_name']} for {league_info['country']}"
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created leagues for {len(TOP_LEAGUES)} countries'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating leagues: {str(e)}')
            )