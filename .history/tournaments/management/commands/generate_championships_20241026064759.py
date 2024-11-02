from django.core.management.base import BaseCommand
from django.db import transaction
from django_countries import countries
from faker import Faker
from tournaments.models import League, Championship, Season, ChampionshipTeam
from clubs.models import Club

class Command(BaseCommand):
    help = 'Generates championships for all countries with bot teams'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.team_adjectives = ['Red', 'Blue', 'Golden', 'Silver', 'Black', 
                              'White', 'Royal', 'Imperial', 'Northern', 'United',
                              'Real', 'Crystal', 'Athletic', 'Sporting', 'Racing']
        self.team_nouns = ['Lions', 'Eagles', 'Dragons', 'Warriors', 'Knights',
                          'Rovers', 'Rangers', 'Wanderers', 'Stars', 'Kings',
                          'Legends', 'Phoenix', 'Tigers', 'Panthers', 'Wolves']

    def generate_team_name(self):
        """Generates a random team name from adjectives and nouns"""
        adj = self.fake.random_element(self.team_adjectives)
        noun = self.fake.random_element(self.team_nouns)
        return f"{adj} {noun}"

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Create current season if not exists
                season, created = Season.objects.get_or_create(
                    name="2024/2025",
                    defaults={
                        'start_date': '2024-08-01',
                        'end_date': '2025-05-31',
                        'is_active': True
                    }
                )

                # Create leagues and championships for each country
                for country_code, country_name in list(countries):
                    # Create top division league
                    league, created = League.objects.get_or_create(
                        country=country_code,
                        level=1,
                        defaults={
                            'name': f"{country_name} Premier League",
                            'max_teams': 16,
                            'foreign_players_limit': 5
                        }
                    )

                    # Create championship
                    championship, created = Championship.objects.get_or_create(
                        season=season,
                        league=league,
                        defaults={
                            'status': 'pending',
                            'start_date': season.start_date,
                            'end_date': season.end_date
                        }
                    )

                    # Generate bot teams if needed
                    existing_teams = ChampionshipTeam.objects.filter(
                        championship=championship
                    ).count()

                    teams_needed = 16 - existing_teams
                    
                    for _ in range(teams_needed):
                        # Create bot team
                        team_name = self.generate_team_name()
                        team = Club.objects.create(
                            name=team_name,
                            country=country_code,
                            is_bot=True  # Нужно добавить это поле в модель Club
                        )
                        
                        # Add team to championship
                        ChampionshipTeam.objects.create(
                            championship=championship,
                            team=team
                        )

                self.stdout.write(self.style.SUCCESS('Successfully generated championships'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))