import time
import logging
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Match, MatchEvent
from .match_simulation import simulate_one_minute

logger = logging.getLogger(__name__)


@shared_task(name='matches.simulate_match_minute')
def simulate_match_minute(match_id: int):
    """
    Запускает симуляцию 1 виртуальной минуты матча (через match_simulation).
    Это вызывается, например, каждые 5 секунд, 
    или любым другим механизмом.
    """
    try:
        simulate_one_minute(match_id)
        logger.info(f"Successfully simulated minute for match {match_id}")
    except Exception as e:
        logger.error(f"Error simulating minute for match {match_id}: {str(e)}")
        raise


@shared_task(name='matches.broadcast_minute_events_in_chunks')
def broadcast_minute_events_in_chunks(match_id: int, minute: int, duration: int = 10):
    """
    Поштучно (с паузой) отправляет по WebSocket все события, 
    созданные в указанную минуту матча.

    :param match_id: ID матча
    :param minute: виртуальная футбольная минута, события которой нужно разослать
    :param duration: за сколько секунд мы хотим показать все события этой минуты
                     (напр. если в минуте 5 событий и duration=10, то каждые ~2с отправляем событие)
    """
    try:
        match = Match.objects.get(id=match_id)

        # Если матч уже 'finished', просто игнорируем
        if match.status == 'finished':
            logger.info(f"Match {match_id} is finished. No chunked broadcast needed.")
            return

        # Получаем все события, относящиеся к этой минуте
        # и сортируем их в порядке добавления (в базе может быть порядок по id).
        events = list(
            MatchEvent.objects.filter(match=match, minute=minute).order_by('id')
        )
        total_events = len(events)

        if total_events == 0:
            logger.info(f"No events to broadcast for match {match_id}, minute {minute}")
            return

        logger.info(
            f"Will broadcast {total_events} events for match {match_id}, minute {minute}, "
            f"spread over {duration} seconds."
        )

        # Подключаемся к каналам
        channel_layer = get_channel_layer()

        # Рассчитываем, через какой интервал отправлять события
        # Например, если 5 событий и duration=10, то каждые 2 секунды.
        chunk_time = duration / float(total_events)

        for i, event in enumerate(events):
            # Формируем "mini-update" со списком из 1 события
            single_event_data = {
                "minute": event.minute,
                "event_type": event.event_type,
                "description": event.description,
            }

            # Собираем структуру данных для отправки
            update_data = {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "status": match.status,
                # В этот раз отправляем только 1 событие (event),
                # чтобы на фронте поочередно "проигрывать" их внутри одной минуты
                "events": [single_event_data]
            }

            # Логируем
            logger.info(
                f"Broadcasting event {i+1}/{total_events} for match {match_id}, minute {minute}"
            )

            # Отправляем в WebSocket (через group_send)
            async_to_sync(channel_layer.group_send)(
                f"match_{match_id}",
                {
                    "type": "match_update",
                    "data": update_data
                }
            )

            # Делаем паузу между событиями
            if i < total_events - 1:
                logger.debug(f"Sleeping {chunk_time:.2f} seconds before next event...")
                time.sleep(chunk_time)

        logger.info(f"Finished broadcasting {total_events} events for match {match_id}, minute {minute}")

    except Match.DoesNotExist:
        logger.error(f"Match {match_id} does not exist")
    except Exception as e:
        logger.error(f"Error in broadcast_minute_events_in_chunks for match {match_id}: {str(e)}")
        raise
