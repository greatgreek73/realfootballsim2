from django.core.management.base import BaseCommand
from django.db import transaction
from clubs.models import Club
from players.models import Player
from faker import Faker
from players.utils import generate_player_stats
import random

class Command(BaseCommand):
    help = 'Generates players for all teams'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                clubs = Club.objects.all()
                
                for club in clubs:
                    self.stdout.write(f"Generating players for {club.name}...")
                    
                    # Создаем Faker для соответствующей страны
                    fake = Faker(['en_GB'])
                    
                    # Позиции игроков
                    positions = [
                        "Goalkeeper",
                        "Right Back",
                        "Center Back",
                        "Left Back",
                        "Defensive Midfielder",
                        "Central Midfielder",
                        "Attacking Midfielder",
                        "Right Midfielder",
                        "Left Midfielder",
                        "Center Forward"
                    ]
                    
                    # Создаем минимум 25 игроков для каждой команды
                    # Обязательно создаем вратаря
                    self.create_player(club, "Goalkeeper", fake)
                    
                    # Создаем остальных игроков
                    for _ in range(24):
                        position = random.choice(positions)
                        self.create_player(club, position, fake)
                    
                    self.stdout.write(f"Created 25 players for {club.name}")
                
                self.stdout.write(self.style.SUCCESS("All teams populated with players!"))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error generating players: {str(e)}")
            )
    
    def create_player(self, club, position, fake):
        """Создает одного игрока"""
        # Генерируем уникальное имя
        while True:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
            if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                break
        
        # Генерируем характеристики
        stats = generate_player_stats(position, random.randint(1, 4))
        
        if position == 'Goalkeeper':
            Player.objects.create(
                club=club,
                first_name=first_name,
                last_name=last_name,
                nationality=club.country,
                # Игроки классов 1-4 должны быть 17 лет
                age=17,
                position=position,
                player_class=random.randint(1, 4),
                strength=stats['strength'],
                stamina=stats['stamina'],
                pace=stats['pace'],
                positioning=stats['positioning'],
                reflexes=stats['reflexes'],
                handling=stats['handling'],
                aerial=stats['aerial'],
                jumping=stats['jumping'],
                command=stats['command'],
                throwing=stats['throwing'],
                kicking=stats['kicking']
            )
        else:
            Player.objects.create(
                club=club,
                first_name=first_name,
                last_name=last_name,
                nationality=club.country,
                # Игроки классов 1-4 должны быть 17 лет
                age=17,
                position=position,
                player_class=random.randint(1, 4),
                strength=stats['strength'],
                stamina=stats['stamina'],
                pace=stats['pace'],
                marking=stats['marking'],
                tackling=stats['tackling'],
                work_rate=stats['work_rate'],
                positioning=stats['positioning'],
                passing=stats['passing'],
                crossing=stats['crossing'],
                dribbling=stats['dribbling'],
                ball_control=stats['ball_control'],
                heading=stats['heading'],
                finishing=stats['finishing'],
                long_range=stats['long_range'],
                vision=stats['vision']
            )