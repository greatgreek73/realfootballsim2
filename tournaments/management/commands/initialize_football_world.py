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

    def generate_team_name(self, fake):
        """Генерирует уникальное название команды"""
        attempts = 0
        while attempts < 100:
            city = fake.city()
            variant = random.choice([
                f"{city} {random.choice(self.team_names)}",
                f"{random.choice(self.team_names)} {city}",
                f"{city} {random.choice(self.team_suffixes)}"
            ])
            if not Club.objects.filter(name=variant).exists():
                return variant
            attempts += 1
        raise Exception("Не удалось создать уникальное имя команды")

    def create_league_structure(self):
        """Создает структуру лиг"""
        self.stdout.write("Creating league structure...")
        try:
            for league_info in self.TOP_LEAGUES:
                # Первый дивизион
                League.objects.create(
                    name=f"{league_info['country']} {league_info['div1_name']}",
                    country=league_info['country'],
                    level=1,
                    max_teams=16,
                    foreign_players_limit=5
                )
                
                # Второй дивизион
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
                for _ in range(16):  # 16 команд в каждой лиге
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

    def create_player(self, club, position, fake, player_class):
        """Создает одного игрока"""
        while True:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
            if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                break

        stats = generate_player_stats(position, player_class)

        # Базовые характеристики для всех игроков
        base_stats = {
            'club': club,
            'first_name': first_name,
            'last_name': last_name,
            'nationality': club.country,
            'age': random.randint(17, 35),
            'position': position,
            'player_class': player_class,
            'strength': stats['strength'],
            'stamina': stats['stamina'],
            'pace': stats['pace'],
            'positioning': stats['positioning'],
        }

        if position == 'Goalkeeper':
            # Добавляем характеристики вратаря
            goalkeeper_stats = {
                'reflexes': stats['reflexes'],
                'handling': stats['handling'],
                'aerial': stats['aerial'],
                'command': stats['command'],
                'distribution': stats['distribution'],
                'one_on_one': stats['one_on_one'],
                'rebound_control': stats['rebound_control'],
                'shot_reading': stats['shot_reading']
            }
            player_stats = {**base_stats, **goalkeeper_stats}
        else:
            # Добавляем характеристики полевого игрока
            field_stats = {
                'marking': stats['marking'],
                'tackling': stats['tackling'],
                'work_rate': stats['work_rate'],
                'passing': stats['passing'],
                'crossing': stats['crossing'],
                'dribbling': stats['dribbling'],
                'flair': stats['flair'],
                'heading': stats['heading'],
                'finishing': stats['finishing'],
                'long_range': stats['long_range'],
                'vision': stats['vision'],
                'accuracy': stats['accuracy']
            }
            player_stats = {**base_stats, **field_stats}

        return Player.objects.create(**player_stats)

    def create_players(self):
        """Создает игроков для всех команд"""
        self.stdout.write("Creating players...")
        try:
            for club in Club.objects.all():
                fake = Faker(['en_GB'])
                players_created = 0
                
                # Создаем игроков согласно структуре команды
                for position, details in self.team_structure.items():
                    count = details["count"]
                    class_distribution = details["class_distribution"]
                    
                    # Создаем указанное количество игроков на позицию
                    for i in range(count):
                        # Выбираем класс игрока из распределения
                        player_class = class_distribution[i % len(class_distribution)]
                        self.create_player(club, position, fake, player_class)
                        players_created += 1
                
                self.stdout.write(f"Created {players_created} players for {club.name}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating players: {str(e)}"))
            return False

    def create_season_and_championships(self):
        """Создает сезон и чемпионаты"""
        self.stdout.write("Creating season and championships...")
        try:
            # Создаем сезон (изменено начало на 1 декабря)
            season = Season.objects.create(
                name="2024/2025",
                number=1,
                start_date=datetime(2024, 12, 1).date(),  # Изменено с 11, 1 на 12, 1
                end_date=datetime(2025, 5, 31).date(),
                is_active=True
            )

            # Создаем чемпионаты для всех лиг
            for league in League.objects.all():
                championship = Championship.objects.create(
                    season=season,
                    league=league,
                    status='in_progress',
                    start_date=season.start_date,  # Используется новая дата начала
                    end_date=season.end_date,
                    match_time=timezone.now().time().replace(hour=18, minute=0)
                )
                
                # Добавляем команды в чемпионат
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
        
        # Пошаговое выполнение с проверками
        if not self.create_league_structure():
            return
            
        if not self.create_teams():
            return
            
        if not self.create_players():
            return
            
        if not self.create_season_and_championships():
            return
            
        # Генерируем матчи через существующую команду
        try:
            from django.core.management import call_command
            call_command('generate_all_matches')
            self.stdout.write(self.style.SUCCESS("Football world initialization completed!"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating matches: {str(e)}')
            )
