from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import League
from clubs.models import Club
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Populates first divisions with bot teams'

    def __init__(self):
        super().__init__()
        self.team_adjectives = [
            'United', 'City', 'Athletic', 'Rovers', 'Wanderers', 
            'Rangers', 'Dynamo', 'Sporting', 'Real', 'Inter',
            'Academy', 'Warriors', 'Legion', 'Phoenix', 'Union'
        ]
        self.team_suffixes = ['FC', 'CF', 'SC', 'AF']

    def generate_team_name(self, fake):
        """Генерирует уникальное название команды"""
        attempts = 0
        while attempts < 100:
            city = fake.city()
            variant = random.choice([
                f"{city} {random.choice(self.team_adjectives)}",
                f"{random.choice(self.team_adjectives)} {city}",
                f"{city} {random.choice(self.team_suffixes)}"
            ])
            if not Club.objects.filter(name=variant).exists():
                return variant
            attempts += 1
        raise Exception("Не удалось создать уникальное имя команды")

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Получаем все первые дивизионы
                first_divisions = League.objects.filter(level=1)
                
                for league in first_divisions:
                    self.stdout.write(f"Populating {league.name}...")
                    
                    # Проверяем, сколько команд уже есть
                    existing_teams = Club.objects.filter(league=league).count()
                    if existing_teams >= 16:
                        self.stdout.write(f"League {league.name} already has {existing_teams} teams")
                        continue
                    
                    # Создаем Faker для соответствующей страны
                    fake = Faker(['en_GB'])  # Можно добавить больше локалей
                    
                    # Добавляем команды до 16
                    teams_to_create = 16 - existing_teams
                    for _ in range(teams_to_create):
                        team_name = self.generate_team_name(fake)
                        Club.objects.create(
                            name=team_name,
                            country=league.country,
                            league=league,
                            is_bot=True
                        )
                        self.stdout.write(f"Created team: {team_name}")
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully populated {league.name} with {teams_to_create} teams"
                        )
                    )
                
                self.stdout.write(self.style.SUCCESS("All first divisions populated!"))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error populating first divisions: {str(e)}")
            )