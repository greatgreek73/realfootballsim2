from django.core.management.base import BaseCommand
from players.models import Player
from players.utils import generate_bloom_data


class Command(BaseCommand):
    help = 'Updates existing players with bloom data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Находим игроков без данных расцвета (у них bloom_type пустой или None)
        players_to_update = Player.objects.filter(
            bloom_type='middle',  # Значение по умолчанию из модели
            bloom_start_age=18,   # Значение по умолчанию из модели
            bloom_seasons_left=0  # Значение по умолчанию из модели
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Найдено {players_to_update.count()} игроков для обновления'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Режим dry-run: изменения не будут сохранены')
            )
        
        updated_count = 0
        
        for player in players_to_update:
            # Генерируем новые данные расцвета
            bloom_data = generate_bloom_data()
            
            old_data = f"Type: {player.bloom_type}, Start: {player.bloom_start_age}"
            new_data = f"Type: {bloom_data['bloom_type']}, Start: {bloom_data['bloom_start_age']}"
            
            if not dry_run:
                # Обновляем игрока
                player.bloom_type = bloom_data['bloom_type']
                player.bloom_start_age = bloom_data['bloom_start_age']
                player.bloom_seasons_left = bloom_data['bloom_seasons_left']
                player.save()
            
            updated_count += 1
            
            if updated_count <= 10:  # Показываем первые 10 примеров
                self.stdout.write(
                    f'Игрок {player.full_name} (возраст {player.age}): '
                    f'{old_data} -> {new_data}'
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно обновлено {updated_count} игроков'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Было бы обновлено {updated_count} игроков'
                )
            )