from django.core.management.base import BaseCommand
from django.db import transaction
from django_countries import countries
from faker import Faker
from tournaments.models import League, Championship, Season
from clubs.models import Club
from tqdm import tqdm  # для прогресс-бара
import sys

class Command(BaseCommand):
    help = 'Generates championships for all countries with bot teams'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
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
        self.stats = {
            'leagues_created': 0,
            'championships_created': 0,
            'teams_created': 0
        }

    def generate_team_name(self):
        """Generates a unique random team name"""
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            adj = self.fake.random_element(self.team_adjectives)
            noun = self.fake.random_element(self.team_nouns)
            name = f"{adj} {noun}"
            if not Club.objects.filter(name=name).exists():
                return name
            attempts += 1
        raise Exception("Could not generate unique team name after 100 attempts")

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-from',
            type=str,
            help='Start from specific country code (e.g., "FR" for France)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of championships even if they exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting championship generation...')
        start_from = options.get('start_from', '').upper()
        
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

                # Get list of countries and create progress bar
                country_list = list(countries)
                if start_from:
                    start_index = next((i for i, (code, _) in enumerate(country_list) 
                                      if code == start_from), 0)
                    country_list = country_list[start_index:]

                with tqdm(total=len(country_list), desc="Processing countries") as pbar:
                    # Process each country
                    for country_code, country_name in country_list:
                        try:
                            # Check if league already exists
                            league = League.objects.filter(
                                country=country_code,
                                level=1
                            ).first()

                            if not league:
                                league = League.objects.create(
                                    country=country_code,
                                    level=1,
                                    name=f"{country_name} Premier League",
                                    max_teams=16,
                                    foreign_players_limit=5
                                )
                                self.stats['leagues_created'] += 1
                                self.stdout.write(f'Created league for {country_name}')

                            # Check if championship exists
                            championship = Championship.objects.filter(
                                season=season,
                                league=league
                            ).first()

                            if not championship:
                                championship = Championship.objects.create(
                                    season=season,
                                    league=league,
                                    status='pending',
                                    start_date=season.start_date,
                                    end_date=season.end_date
                                )
                                self.stats['championships_created'] += 1
                                self.stdout.write(f'Created championship for {league.name}')

                                # Create teams only for new championships
                                for i in range(16):
                                    team_name = self.generate_team_name()
                                    team = Club.objects.create(
                                        name=team_name,
                                        country=country_code,
                                        is_bot=True,
                                        owner=None
                                    )
                                    championship.teams.add(team)
                                    self.stats['teams_created'] += 1
                                    self.stdout.write(f'Created bot team: {team_name}')

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error processing {country_name}: {str(e)}')
                            )
                            continue
                        finally:
                            pbar.update(1)

                # Print final statistics
                self.stdout.write(self.style.SUCCESS('\nGeneration completed!'))
                self.stdout.write(f"Leagues created: {self.stats['leagues_created']}")
                self.stdout.write(f"Championships created: {self.stats['championships_created']}")
                self.stdout.write(f"Teams created: {self.stats['teams_created']}")
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nProcess interrupted by user'))
            self.stdout.write(f"Leagues created: {self.stats['leagues_created']}")
            self.stdout.write(f"Championships created: {self.stats['championships_created']}")
            self.stdout.write(f"Teams created: {self.stats['teams_created']}")
            sys.exit(1)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\nError during championship generation: {str(e)}')
            )
            raise e