from django.core.management.base import BaseCommand
from django.db import transaction
from players.models import Player
from players.utils import generate_player_stats
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Updates existing players with new attributes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='How many players to update in one batch'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        try:
            # Получаем общее количество игроков
            total_players = Player.objects.count()
            self.stdout.write(f"Found {total_players} players to update")

            # Используем tqdm для отображения прогресса
            with tqdm(total=total_players) as pbar:
                # Обрабатываем игроков батчами для экономии памяти
                for i in range(0, total_players, batch_size):
                    with transaction.atomic():
                        players = Player.objects.all()[i:i+batch_size]
                        
                        for player in players:
                            # Генерируем новые характеристики
                            stats = generate_player_stats(
                                player.position,
                                player.player_class
                            )
                            
                            # Обновляем характеристики игрока
                            for attr, value in stats.items():
                                setattr(player, attr, value)
                            
                            player.save()
                            pbar.update(1)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated {total_players} players'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating players: {str(e)}'
                )
            )
            raise e