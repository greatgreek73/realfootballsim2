from django.core.management.base import BaseCommand
from django.db import transaction
from django_countries import countries
from faker import Faker
from tournaments.models import League, Championship, Season
from clubs.models import Club

class Command(BaseCommand):
    help = 'Generates championships for all countries with bot teams'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        # Расширенные списки для большего разнообразия
        self.team_adjectives = [
            'Red', 'Blue', 'Golden', 'Silver', 'Black', 'White', 'Royal',
            'Imperial', 'Northern', 'United', 'Real', 'Crystal', 'Athletic',
            'Sporting', 'Racing', 'Phoenix', 'Elite', 'Supreme', 'Ancient',
            'Mighty'
        ]
        self.team_nouns = [
            'Lions', 'Eagles', 'Dragons', 'Warriors', 'Knights', 'Rovers',
            'Rangers', 'Wanderers', 'Stars', 'Kings', 'Legends', 'Phoenix',
            'Tigers', 'Panthers', 'Wolves', 'Falcons', 'Titans', 'Giants',
            'Heroes', 'Guardians'
        ]

    def generate_team_name(self):
        """Generates a unique random team name"""
        while True:
            adj = self.fake.random_element(self.team_adjectives)
            noun = self.fake.random_element(self.team_nouns)
            name = f"{adj} {noun}"
            # Проверяем, что такое название еще не существует
            if not Club.objects.filter(name=name).exists():
                return name

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of championships even if they exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting championship generation...')
        
        try:
            with transaction.atomic():
                # Create active season if not exists
                season, created = Season.objects.get_or_create(
                    name="2024/2025",
                    defaults={
                        'start_date': '2024-08-01',
                        'end_date': '2025-05-31',
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new season: {season.name}'))
                else:
                    self.stdout.write(f'Using existing season: {season.name}')

                # Process each country
                for country_code, country_name in list(countries):
                    self.stdout.write(f'Processing {country_name}...')
                    
                    # Create league
                    league, created = League.objects.get_or_create(
                        country=country_code,
                        level=1,  # Top division
                        defaults={
                            'name': f"{country_name} Premier League",
                            'max_teams': 16,
                            'foreign_players_limit': 5
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'Created league for {country_name}')

                    # Create or get championship
                    championship, created = Championship.objects.get_or_create(
                        season=season,
                        league=league,
                        defaults={
                            'status': 'pending',
                            'start_date': season.start_date,
                            'end_date': season.end_date
                        }
                    )

                    if created:
                        self.stdout.write(f'Created championship for {league.name}')
                        
                        # Create 16 bot teams for new championship
                        for i in range(16):
                            team_name = self.generate_team_name()
                            team = Club.objects.create(
                                name=team_name,
                                country=country_code,
                                is_bot=True,
                                owner=None
                            )
                            championship.teams.add(team)
                            self.stdout.write(f'Created bot team: {team_name}')

                self.stdout.write(self.style.SUCCESS('Successfully generated all championships'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during championship generation: {str(e)}')
            )
            raise e