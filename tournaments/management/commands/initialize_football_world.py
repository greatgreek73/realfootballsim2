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
            }
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

        # В каждой команде может быть максимум 30 игроков
        self.max_players_per_club = 30

    def generate_team_name(self, fake):
        """
        Генерирует уникальное название команды.
        """
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
        """
        Создает 2 дивизиона на каждую из TOP_LEAGUES.
        """
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
            self.stdout.write(self.style.SUCCESS(
                f"Created {len(self.TOP_LEAGUES) * 2} leagues"
            ))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating leagues: {str(e)}"))
            return False

    def create_teams(self):
        """
        Создаёт 16 команд (is_bot=True) в каждой лиге, генерируя уникальные названия.
        """
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

    def create_player(self, club, position, fake, player_class):
        """
        Создает одного игрока (с уникальным ФИО) нужного класса и позиции.
        """
        # Генерируем уникальное ФИО
        while True:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
            if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                break

        stats = generate_player_stats(position, player_class)

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
            # Доп. характеристики вратаря
            gk_stats = {
                'reflexes': stats['reflexes'],
                'handling': stats['handling'],
                'aerial': stats['aerial'],
                'command': stats['command'],
                'distribution': stats['distribution'],
                'one_on_one': stats['one_on_one'],
                'rebound_control': stats['rebound_control'],
                'shot_reading': stats['shot_reading']
            }
            player_stats = {**base_stats, **gk_stats}
        else:
            # Полевые игроки
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
        """
        Создаёт игроков для ботов-команд не больше 30 в каждом клубе.
        """
        self.stdout.write("Creating players...")
        try:
            for club in Club.objects.all():
                fake = Faker(['en_GB'])
                players_created = 0
                existing_count = Player.objects.filter(club=club).count()

                # Если уже 30 или больше игроков, пропускаем
                if existing_count >= self.max_players_per_club:
                    self.stdout.write(
                        f"Skipping {club.name} - already has {existing_count} players"
                    )
                    continue

                # Создаем игроков согласно team_structure
                for position, details in self.team_structure.items():
                    if existing_count >= self.max_players_per_club:
                        break

                    count = min(details["count"], self.max_players_per_club - existing_count)
                    class_distribution = details["class_distribution"]

                    for i in range(count):
                        player_class = class_distribution[i % len(class_distribution)]
                        self.create_player(club, position, fake, player_class)
                        players_created += 1
                        existing_count += 1

                        if existing_count >= self.max_players_per_club:
                            break

                self.stdout.write(f"Created {players_created} players for {club.name}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating players: {str(e)}"))
            return False

    def create_season_and_championships(self):
        """
        Создает 1 сезон (Season 1) и чемпионаты для каждой лиги, 
        устанавливая статус in_progress.
        """
        self.stdout.write("Creating season and championships...")
        try:
            # Чтобы end_date > start_date, поменяем год end_date на 2025
            season = Season.objects.create(
                name="Season 1",
                number=1,
                start_date=datetime(2025, 2, 1).date(),
                end_date=datetime(2025, 2, 28).date(),
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
                # Добавляем все клубы этой лиги в teams
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

        # 1) Создание лиг
        if not self.create_league_structure():
            return

        # 2) Создание команд
        if not self.create_teams():
            return

        # 3) Создание игроков
        if not self.create_players():
            return

        # 4) Сезон + чемпионаты
        if not self.create_season_and_championships():
            return

        # 5) Генерация матчей
        try:
            from django.core.management import call_command
            call_command('generate_all_matches')
            self.stdout.write(self.style.SUCCESS("Football world initialization completed!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating matches: {str(e)}'))
