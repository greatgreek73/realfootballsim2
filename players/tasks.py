import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import datetime
import pytz

from .training_logic import conduct_all_teams_training

logger = logging.getLogger("player_training")


@shared_task(name='players.conduct_scheduled_training', bind=True)
def conduct_scheduled_training(self):
    """
    Проводит автоматические тренировки для всех команд.
    Запускается по расписанию: понедельник, среда, пятница в 12:00 CET.
    """
    now = timezone.now()
    logger.info(f"🏋️ [conduct_scheduled_training] Запуск тренировок в {now}")

    try:
        with transaction.atomic():
            # Проводим тренировки для всех команд
            stats = conduct_all_teams_training()
            
            logger.info(
                f"✅ Тренировки завершены. Статистика: "
                f"Команд: {stats['teams_trained']}, "
                f"Игроков: {stats['players_trained']}, "
                f"Улучшений: {stats['total_improvements']}, "
                f"В расцвете: {stats['players_in_bloom']}, "
                f"Ошибок: {stats['errors']}"
            )
            
            return {
                'status': 'success',
                'timestamp': now.isoformat(),
                'stats': stats
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проведении тренировок: {e}")
        return {
            'status': 'error',
            'timestamp': now.isoformat(),
            'error': str(e)
        }


@shared_task(name='players.advance_player_seasons', bind=True)
def advance_player_seasons(self):
    """
    Продвигает сезоны расцвета игроков.
    Запускается в начале каждого нового сезона.
    """
    from .models import Player
    
    now = timezone.now()
    logger.info(f"📅 [advance_player_seasons] Продвижение сезонов игроков в {now}")
    
    stats = {
        'players_processed': 0,
        'blooms_started': 0,
        'blooms_ended': 0,
        'errors': 0
    }
    
    try:
        with transaction.atomic():
            players = Player.objects.all()
            
            for player in players:
                try:
                    stats['players_processed'] += 1
                    
                    # Проверяем, нужно ли запустить расцвет
                    if player.should_start_bloom():
                        player.start_bloom()
                        stats['blooms_started'] += 1
                        logger.info(
                            f"🌟 Начат расцвет игрока {player.full_name} "
                            f"({player.bloom_type}, возраст {player.age})"
                        )
                    
                    # Продвигаем существующий расцвет
                    if player.is_in_bloom:
                        old_seasons = player.bloom_seasons_left
                        player.advance_bloom_season()
                        
                        if player.bloom_seasons_left == 0:
                            stats['blooms_ended'] += 1
                            logger.info(
                                f"🏁 Завершен расцвет игрока {player.full_name} "
                                f"({player.bloom_type})"
                            )
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка при обработке игрока {player.id}: {e}")
                    stats['errors'] += 1
            
            logger.info(
                f"✅ Сезоны игроков продвинуты. Статистика: "
                f"Обработано: {stats['players_processed']}, "
                f"Расцветов начато: {stats['blooms_started']}, "
                f"Расцветов завершено: {stats['blooms_ended']}, "
                f"Ошибок: {stats['errors']}"
            )
            
            return {
                'status': 'success',
                'timestamp': now.isoformat(),
                'stats': stats
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка при продвижении сезонов: {e}")
        return {
            'status': 'error',
            'timestamp': now.isoformat(),
            'error': str(e)
        }


def is_training_day():
    """
    Проверяет, является ли сегодняшний день тренировочным.
    Тренировки проходят в понедельник (0), среду (2) и пятницу (4).
    """
    cet = pytz.timezone('CET')
    now_cet = timezone.now().astimezone(cet)
    weekday = now_cet.weekday()
    return weekday in [0, 2, 4]  # Понедельник, среда, пятница


@shared_task(name='players.check_training_schedule', bind=True)
def check_training_schedule(self):
    """
    Проверяет, нужно ли проводить тренировку сегодня.
    Запускается каждый день в 12:00 CET.
    """
    if is_training_day():
        logger.info("📅 Сегодня тренировочный день, запускаем тренировки...")
        return conduct_scheduled_training.delay()
    else:
        logger.info("📅 Сегодня не тренировочный день, пропускаем...")
        return {
            'status': 'skipped',
            'reason': 'Not a training day',
            'timestamp': timezone.now().isoformat()
        }