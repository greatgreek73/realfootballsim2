from django.core.management.base import BaseCommand
from django.db import transaction
from django_countries import countries
from faker import Faker
from tournaments.models import League, Championship, Season
from clubs.models import Club
from tqdm import tqdm
import sys
import random  # Добавляем импорт random

class Command(BaseCommand):
    help = 'Generates championships for all countries with bot teams'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.team_adjectives = [
            'Red', 'Blue', 'Golden', 'Silver', 'Black', 'White', 'Royal',
            'Imperial', 'Northern', 'United', 'Real', 'Crystal', 'Athletic',
            'Sporting', 'Racing', 'Phoenix', 'Elite', 'Supreme', 'Ancient',
            'Mighty', 'Green', 'Purple', 'Bronze', 'Iron', 'Steel', 
            'Eastern', 'Western', 'Southern', 'Central', 'Inter',
            'Dynamic', 'Olympic', 'Spartak', 'Victoria', 'Glory',
            'Freedom', 'Unity', 'Progressive', 'Classic', 'Modern'
        ]
        self.team_nouns = [
            'Lions', 'Eagles', 'Dragons', 'Warriors', 'Knights', 'Rovers',
            'Rangers', 'Wanderers', 'Stars', 'Kings', 'Legends', 'Phoenix',
            'Tigers', 'Panthers', 'Wolves', 'Falcons', 'Titans', 'Giants',
            'Heroes', 'Guardians', 'Hawks', 'Bears', 'Sharks', 'Vipers',
            'Scorpions', 'Pythons', 'Cobras', 'Stallions', 'Bulls', 'Raiders',
            'Hunters', 'Hornets', 'Ravens', 'Demons', 'Angels', 'Thunder',
            'Lightning', 'Storm', 'United', 'City'
        ]
        self.team_suffixes = ['FC', 'United', 'City', 'Athletic', 'Sporting']
        self.stats = {
            'leagues_created': 0,
            'championships_created': 0,
            'teams_created': 0,
            'countries_processed': 0
        }

    def generate_team_name(self):
        """Generates a unique random team name with more variations"""
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            # 70% chance of standard name (Adjective + Noun)
            # 30% chance of name with suffix (Adjective + Noun + Suffix)
            if random.random() < 0.7:
                adj = self.fake.random_element(self.team_adjectives)
                noun = self.fake.random_element(self.team_nouns)
                name = f"{adj} {noun}"
            else:
                adj = self.fake.random_element(self.team_adjectives)
                noun = self.fake.random_element(self.team_nouns)
                suffix = self.fake.random_element(self.team_suffixes)
                name = f"{adj} {noun} {suffix}"

            if not Club.objects.filter(name=name).exists():
                return name
            attempts += 1
        raise Exception(f"Could not generate unique team name after {max_attempts} attempts")

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
        self.stdout.write('Starting championship generation process...')
        
        # Безопасная обработка start_from
        start_from = (options.get('start_from') or '').upper()
        force = options.get('force', False)

        # Предварительная проверка
        existing_leagues = League.objects.count()
        existing_championships = Championship.objects.count()
        existing_clubs = Club.objects.count()

        self.stdout.write(f'Current state:')
        self.stdout.write(f'- Existing leagues: {existing_leagues}')
        self.stdout.write(f'- Existing championships: {existing_championships}')
        self.stdout.write(f'- Existing clubs: {existing_clubs}')
        
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

                # Get list of countries and filter if needed
                country_list = list(countries)
                if start_from:
                    try:
                        start_index = next(i for i, (code, _) in enumerate(country_list) 
                                         if code == start_from)
                        country_list = country_list[start_index:]
                        self.stdout.write(f'Starting from country: {start_from}')
                    except StopIteration:
                        self.stdout.write(
                            self.style.WARNING(f'Country code {start_from} not found, starting from beginning')
                        )

                self.stdout.write(f'Processing {len(country_list)} countries...')

                with tqdm(total=len(country_list), desc="Processing countries") as pbar:
                    for country_code, country_name in country_list:
                        try:
                            # Check if league exists
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

                            # Check if championship exists
                            championship = Championship.objects.filter(
                                season=season,
                                league=league
                            ).first()

                            if not championship or force:
                                if force and championship:
                                    championship.delete()
                                
                                championship = Championship.objects.create(
                                    season=season,
                                    league=league,
                                    status='pending',
                                    start_date=season.start_date,
                                    end_date=season.end_date
                                )
                                self.stats['championships_created'] += 1

                                # Create teams
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

                            self.stats['countries_processed'] += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error processing {country_name}: {str(e)}')
                            )
                            continue
                        finally:
                            pbar.update(1)

                # Print final statistics
                self.stdout.write(self.style.SUCCESS('\nGeneration completed successfully!'))
                self.stdout.write(f"Countries processed: {self.stats['countries_processed']}")
                self.stdout.write(f"Leagues created: {self.stats['leagues_created']}")
                self.stdout.write(f"Championships created: {self.stats['championships_created']}")
                self.stdout.write(f"Teams created: {self.stats['teams_created']}")
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nProcess interrupted by user'))
            self.stdout.write(f"Countries processed: {self.stats['countries_processed']}")
            self.stdout.write(f"Leagues created: {self.stats['leagues_created']}")
            self.stdout.write(f"Championships created: {self.stats['championships_created']}")
            self.stdout.write(f"Teams created: {self.stats['teams_created']}")
            sys.exit(1)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\nError during championship generation: {str(e)}')
            )
            raise e