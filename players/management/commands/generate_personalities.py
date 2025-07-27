from django.core.management.base import BaseCommand
from django.db import transaction
from players.models import Player
from players.personality import PersonalityGenerator


class Command(BaseCommand):
    help = 'Generate personality traits for players without personality data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of players to update in each batch (default: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        try:
            # Находим игроков с пустым personality_traits (пустой словарь {})
            players_to_update = Player.objects.filter(personality_traits={})
            
            total_count = players_to_update.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Найдено {total_count} игроков с пустыми профилями личности'
                )
            )
            
            if total_count == 0:
                self.stdout.write(
                    self.style.WARNING('Нет игроков для обновления')
                )
                return
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('Режим dry-run: изменения не будут сохранены')
                )
                
                # Показываем примеры того, что будет сгенерировано
                sample_players = players_to_update[:5]
                for player in sample_players:
                    sample_personality = PersonalityGenerator.generate()
                    self.stdout.write(
                        f'Игрок {player.full_name}: {sample_personality}'
                    )
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Было бы обновлено {total_count} игроков'
                    )
                )
                return
            
            # Обновляем игроков партиями для лучшей производительности
            updated_count = 0
            players_to_bulk_update = []
            
            self.stdout.write('Генерация профилей личности...')
            
            for player in players_to_update:
                # Генерируем новый профиль личности
                new_personality = PersonalityGenerator.generate()
                player.personality_traits = new_personality
                players_to_bulk_update.append(player)
                
                # Обновляем batch_size игроков за раз
                if len(players_to_bulk_update) >= batch_size:
                    with transaction.atomic():
                        Player.objects.bulk_update(
                            players_to_bulk_update, 
                            ['personality_traits'],
                            batch_size=batch_size
                        )
                    updated_count += len(players_to_bulk_update)
                    
                    # Показываем прогресс
                    self.stdout.write(
                        f'Обновлено {updated_count}/{total_count} игроков...'
                    )
                    
                    players_to_bulk_update = []
            
            # Обновляем оставшихся игроков
            if players_to_bulk_update:
                with transaction.atomic():
                    Player.objects.bulk_update(
                        players_to_bulk_update, 
                        ['personality_traits'],
                        batch_size=len(players_to_bulk_update)
                    )
                updated_count += len(players_to_bulk_update)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно сгенерированы профили личности для {updated_count} игроков'
                )
            )
            
            # Показываем примеры обновленных игроков
            sample_updated = Player.objects.filter(
                personality_traits__isnull=False
            ).exclude(personality_traits={})[:3]
            
            self.stdout.write('\nПримеры сгенерированных профилей:')
            for player in sample_updated:
                traits_summary = []
                for trait, value in list(player.personality_traits.items())[:3]:
                    traits_summary.append(f'{trait}: {value}')
                
                self.stdout.write(
                    f'  {player.full_name}: {", ".join(traits_summary)}...'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при генерации профилей личности: {str(e)}'
                )
            )
            raise