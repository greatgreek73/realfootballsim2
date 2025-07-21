from django.core.management.base import BaseCommand
from clubs.models import Club
from players.models import Player
from django.db import transaction
from faker import Faker
from players.utils import generate_player_stats
from clubs.views import get_locale_from_country_code
from tqdm import tqdm
import random

class Command(BaseCommand):
    help = 'Generates 5 random players for each club'

    def handle(self, *args, **options):
        clubs = Club.objects.all()
        total_clubs = clubs.count()
        
        self.stdout.write(f"Found {total_clubs} clubs. Starting player generation...")
        
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

        with transaction.atomic():
            for club in tqdm(clubs, desc="Generating players"):
                # Создаем Faker с локалью, соответствующей стране клуба
                locale = get_locale_from_country_code(club.country.code)
                fake = Faker(locale)

                # Обязательно создаем вратаря
                self.create_player_for_club(
                    club=club,
                    fake=fake,
                    position="Goalkeeper",
                    player_class=random.randint(1, 4)
                )
                
                # Создаем еще 4 случайных полевых игрока
                for _ in range(4):
                    # Исключаем вратаря из случайного выбора позиций
                    position = random.choice([pos for pos in positions if pos != "Goalkeeper"])
                    self.create_player_for_club(
                        club=club,
                        fake=fake,
                        position=position,
                        player_class=random.randint(1, 4)
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully generated {total_clubs * 5} players for {total_clubs} clubs'
        ))

    def create_player_for_club(self, club, fake, position, player_class):
        """Создает одного игрока для клуба"""
        # Генерируем уникальное имя
        while True:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male() if hasattr(fake, 'last_name_male') else fake.last_name()
            if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                break

        # Генерируем характеристики в зависимости от позиции
        stats = generate_player_stats(position, player_class)

        if position == 'Goalkeeper':
            player = Player.objects.create(
                club=club,
                first_name=first_name,
                last_name=last_name,
                nationality=club.country,
                age=17,
                position=position,
                player_class=player_class,
                strength=stats['strength'],
                stamina=stats['stamina'],
                morale=stats['morale'],
                base_morale=stats['base_morale'],
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
            player = Player.objects.create(
                club=club,
                first_name=first_name,
                last_name=last_name,
                nationality=club.country,
                age=17,
                position=position,
                player_class=player_class,
                strength=stats['strength'],
                stamina=stats['stamina'],
                morale=stats['morale'],
                base_morale=stats['base_morale'],
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

        return player