from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from tournaments.models import League, Championship, Season
from clubs.models import Club
from players.models import Player
from players.utils import generate_player_stats
from faker import Faker
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize complete football world with leagues, teams, and players'

    def __init__(self):
        super().__init__()
        self.TOP_LEAGUES = [
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
        self.team_names = [
            'United', 'City', 'Athletic', 'Rovers', 'Wanderers', 
            'Rangers', 'Dynamo', 'Sporting', 'Real', 'Inter',
            'Academy', 'Warriors', 'Legion', 'Phoenix', 'Union'
        ]
        self.team_suffixes = ['FC', 'CF', 'SC', 'AF']
        
        # Определяем структуру команды
        self.team_structure = {
            "Goalkeeper": {"count": 3, "class_distribution": [1, 2, 3]},
            "Right Back": {"count": 2, "class_distribution": [2, 3]},
            "Center Back": {"count": 4, "class_distribution": [1, 2, 3, 4]},
            "Left Back": {"count": 2, "class_distribution": [2, 3]},
            "Defensive Midfielder": {"count": 2, "class_distribution": [2, 3]},
            "Central Midfielder": {"count": 3, "class_distribution": [1, 2, 3]},
            "Attacking Midfielder": {"count": 2, "class_distribution": [2, 3]},
            "Right Midfielder": {"count": 2, "class_distribution": [2, 3]},
            "Left Midfielder": {"count": 2, "class_distribution": [2, 3]},
            "Center Forward": {"count": 3, "class_distribution": [1, 2, 3]}
        }
    def create_league_structure(self):
        """Создает структуру лиг"""
        self.stdout.write("Creating league structure...")
        try:
            for league_info in self.TOP_LEAGUES:
                League.objects.create(
                    name=f"{league_info['country']} {league_info['div1_name']}",
                    country=league_info['country'],
                    level=1,
                    max_teams=16,
                    foreign_players_limit=5
                )
                League.objects.create(
                    name=f"{league_info['country']} {league_info['div2_name']}",
                    country=league_info['country'],
                    level=2,
                    max_teams=16,
                    foreign_players_limit=5
                )
            self.stdout.write(self.style.SUCCESS(f"Created {len(self.TOP_LEAGUES) * 2} leagues"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating leagues: {str(e)}"))
            return False

    def create_teams(self):
        """Создает команды для всех лиг"""
        self.stdout.write("Creating teams...")
        try:
            for league in League.objects.all():
                fake = Faker(['en_GB'])
                for _ in range(16):
                    team_name = self.generate_team_name(fake)
                    Club.objects.create(
                        name=team_name,
                        country=league.country,
                        league=league,
                        is_bot=True
                    )
                self.stdout.write(f"Created 16 teams for {league.name}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating teams: {str(e)}"))
            return False

    def create_players(self):
        """Создает игроков для всех команд"""
        self.stdout.write("Creating players...")
        try:
            for club in Club.objects.all():
                fake = Faker(['en_GB'])
                players_created = 0
                
                # Проверяем текущее количество игроков
                existing_count = Player.objects.filter(club=club).count()
                if existing_count >= 30:
                    self.stdout.write(f"Skipping {club.name} - already has {existing_count} players")
                    continue

                # Создаем игроков согласно структуре команды
                for position, details in self.team_structure.items():
                    # Если достигли лимита - прекращаем
                    if existing_count >= 30:
                        break
                        
                    count = min(details["count"], 30 - existing_count)
                    class_distribution = details["class_distribution"]
                    
                    for i in range(count):
                        player_class = class_distribution[i % len(class_distribution)]
                        self.create_player(club, position, fake, player_class)
                        players_created += 1
                        existing_count += 1
                        
                        # Проверяем после каждого созданного игрока
                        if existing_count >= 30:
                            break
                
                self.stdout.write(f"Created {players_created} players for {club.name}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating players: {str(e)}"))
            return False

        def create_season_and_championships(self):
        """Создает сезон и чемпионаты"""
        self.stdout.write("Creating season and championships...")
        try:
            season = Season.objects.create(
                name="Season 1",
                number=1,
                start_date=datetime(2025, 1, 1).date(),
                end_date=datetime(2024, 1, 31).date(),
                is_active=True
            )

            for league in League.objects.all():
                championship = Championship.objects.create(
                    season=season,
                    league=league,
                    status='in_progress',
                    start_date=season.start_date,
                    end_date=season.end_date,
                    match_time=timezone.now().time().replace(hour=18, minute=0)
                )
                
                teams = Club.objects.filter(league=league)
                for team in teams:
                    championship.teams.add(team)

                self.stdout.write(f"Created championship for {league.name}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating season and championships: {str(e)}"))
            return False

    def handle(self, *args, **options):
        self.stdout.write("Starting football world initialization...")
        
        if not self.create_league_structure():
            return
        if not self.create_teams():
            return
        if not self.create_players():
            return
        if not self.create_season_and_championships():
            return
            
        try:
            from django.core.management import call_command
            call_command('generate_all_matches')
            self.stdout.write(self.style.SUCCESS("Football world initialization completed!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating matches: {str(e)}'))