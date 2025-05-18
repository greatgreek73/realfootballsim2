# matches/tasks.py

import time
import logging
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction # Импортируем transaction
from django.conf import settings
from django.db import transaction  # Импортируем transaction

# Убедитесь, что импорты Player и Club есть
from players.models import Player 
from clubs.models import Club 

from .models import Match, MatchEvent
# Импортируем simulate_one_minute здесь, если simulate_match_minute его использует
# Если он используется в другом приложении (напр. tournaments), то импорт тут не нужен.
# from .match_simulation import simulate_one_minute 

logger = logging.getLogger(__name__)

# Duration of one simulated minute in seconds. Set MATCH_TICK_SECONDS in
# Django settings to override. Use 60 for real time or shorter for testing.
TICK_SECONDS = getattr(settings, "MATCH_TICK_SECONDS", 5)


# --- Interactive minute simulation task ---
@shared_task(name="matches.simulate_next_minute")
def simulate_next_minute(match_id: int):
    """Simulate one minute, broadcast events and pause the match."""
    start = time.monotonic()
    try:
        with transaction.atomic():
            match = Match.objects.select_for_update().get(id=match_id)

            if match.status != "in_progress":
                logger.info(
                    f"Match {match_id} not in progress (status {match.status})."
                )
                return f"Match {match_id} not in progress"

            from .match_simulation import simulate_one_minute

            match = simulate_one_minute(match)
            if not match:
                logger.error(f"simulate_one_minute failed for match {match_id}")
                return f"Simulation failed {match_id}"

            minute = match.current_minute
            match.save()

        broadcast_minute_events_in_chunks.delay(match_id, minute)

        broadcast_minute_events_in_chunks.delay(
            match_id, minute, duration=TICK_SECONDS
        )

        with transaction.atomic():
            match = Match.objects.select_for_update().get(id=match_id)
            if match.current_minute >= 90:
                match.status = "finished"
            else:
                match.status = "paused"
            match.save()

        elapsed = time.monotonic() - start
        remain = TICK_SECONDS - elapsed
        if remain > 0:
            time.sleep(remain)

        return f"Minute {minute} done for match {match_id}"

    except Match.DoesNotExist:
        logger.error(f"Match {match_id} does not exist in simulate_next_minute")
    except Exception as e:
        logger.exception(f"Error in simulate_next_minute {match_id}: {e}")


# --- ЗАДАЧА СИМУЛЯЦИИ МИНУТЫ ---
# ПРЕДУПРЕЖДЕНИЕ: Эта задача здесь для примера. Если реальный вызов 
# simulate_one_minute происходит из другого места (напр., tournaments.tasks),
# то именно ТАМ нужно добавить .save() и другие улучшения.
@shared_task(name='matches.simulate_match_minute')
def simulate_match_minute(match_id: int):
    """
    Пример задачи, которая вызывает симуляцию ОДНОЙ минуты для ОДНОГО матча.
    ВАЖНО: Она должна сохранять результат! Адаптируйте ваш реальный код вызова.
    """
    logger.debug(f"Task simulate_match_minute received for match_id: {match_id}")
    try:
        # Используем select_for_update и транзакцию для атомарности
        with transaction.atomic():
            match = Match.objects.select_for_update().get(id=match_id)
            
            # Проверяем статус ДО вызова симуляции
            if match.status != 'in_progress':
                 logger.info(f"Match {match_id} is not in progress (status: {match.status}). Skipping minute simulation.")
                 return f"Match {match_id} not in progress."

            # Импортируем функцию симуляции здесь
            # Убедитесь, что путь импорта правильный
            from .match_simulation import simulate_one_minute 
            
            # Вызываем симуляцию
            updated_match = simulate_one_minute(match)
            
            # СОХРАНЯЕМ РЕЗУЛЬТАТ!
            if updated_match:
                if updated_match.status == 'error':
                     logger.error(f"simulate_one_minute indicated an error for match {match_id}. Saving error status.")
                
                # Сохраняем обновленное состояние матча
                updated_match.save() 
                logger.info(f"Successfully simulated and saved minute {updated_match.current_minute} for match {match_id}")
                return f"Simulated minute {updated_match.current_minute} for match {match_id}"
            else:
                 logger.error(f"simulate_one_minute returned None for match {match_id}. State not saved.")
                 return f"Simulation failed for match {match_id}"

    except Match.DoesNotExist:
         logger.error(f"Match {match_id} not found in simulate_match_minute task.")
         # Не перевыбрасываем ошибку, чтобы задача не повторялась
    except Exception as e:
        logger.exception(f"Error in simulate_match_minute for match {match_id}: {e}")
        # Не перевыбрасываем ошибку


# --- ИЗМЕНЕННАЯ ЗАДАЧА broadcast_minute_events_in_chunks ---
@shared_task(name='matches.broadcast_minute_events_in_chunks')
def broadcast_minute_events_in_chunks(match_id: int, minute: int, duration: int = 4):
    """
    Поштучно (с паузой) отправляет по WebSocket ТОЛЬКО СОБЫТИЯ, 
    созданные в указанную минуту матча.
    """
    logger.debug(f"Task broadcast_minute_events received for match {match_id}, minute {minute}")
    try:
        # Проверяем существование и статус матча
        match = Match.objects.filter(id=match_id).first()
        if not match:
             logger.error(f"Match {match_id} does not exist for broadcasting events.")
             return f"Match {match_id} not found"
        
        # Если матч завершён с ошибкой или отменён, прекращаем трансляцию
        if match.status in ['error', 'cancelled']:
            logger.info(
                f"Match {match_id} already {match.status}. Skipping broadcast for minute {minute}."
            )
            return f"Match {match_id} {match.status}, no broadcast needed for minute {minute}"

        # Получаем все события минуты, включая связанные объекты для имен
        events = list(
            MatchEvent.objects.select_related('player', 'related_player')
            .filter(match_id=match_id, minute=minute)
            .order_by('timestamp', 'id') # Сортируем по времени создания + ID
        )
        total_events = len(events)

        if total_events == 0:
            logger.info(f"No events to broadcast for match {match_id}, minute {minute}")
            return f"No events for M{match_id} Min{minute}"

        logger.info(
            f"Broadcasting {total_events} events for match {match_id}, minute {minute}, "
            f"spread over {duration} seconds."
        )

        channel_layer = get_channel_layer()
        if not channel_layer:
             logger.warning("Cannot get channel layer in broadcast task.")
             return "Channel layer unavailable"
             
        # Расчитываем интервал
        chunk_time = max(0.1, duration / float(total_events)) 

        for i, event in enumerate(events):
            # Формируем данные ТОЛЬКО для этого события
            event_player_name = f"{event.player.first_name} {event.player.last_name}" if event.player else ""
            related_player_name = (
                f"{event.related_player.first_name} {event.related_player.last_name}"
                if event.related_player else ""
            )
            
            single_event_data = {
                "minute": event.minute,
                "event_type": event.event_type,
                "description": event.description,
                "player_name": event_player_name,
                "related_player_name": related_player_name,
                # "event_id": event.id, # Можно добавить ID события
            }

            # --- Собираем структуру данных ТОЛЬКО с событием и флагом ---
            message_payload = {
                "type": "match_update",  # Тип сообщения для consumer
                "data": {
                    "match_id": match_id,
                    "minute": minute,  # Передаем минуту события явно
                    "home_score": match.home_score,
                    "away_score": match.away_score,
                    "status": match.status,
                    "st_shoots": match.st_shoots,
                    "st_passes": match.st_passes,
                    "st_possessions": match.st_possessions,
                    "st_fouls": match.st_fouls,
                    "st_injury": match.st_injury,
                    "events": [single_event_data],
                    "partial_update": True,  # Помечаем как частичное обновление
                },
            }
            # -----------------------------------------------------------

            logger.info(
                f"Broadcasting event {i+1}/{total_events} for match {match_id}, minute {minute} (Type: {event.event_type})"
            )

            # Отправляем в WebSocket
            async_to_sync(channel_layer.group_send)(
                f"match_{match_id}",
                message_payload
            )

            # Делаем паузу между событиями
            if i < total_events - 1:
                # logger.debug(f"Sleeping {chunk_time:.2f} seconds before next event...")
                time.sleep(chunk_time)

        logger.info(f"Finished broadcasting {total_events} events for match {match_id}, minute {minute}")
        return f"Broadcasted {total_events} events for M{match_id} Min{minute}"

    # Обработка конкретных ожидаемых исключений
    except Match.DoesNotExist:
        logger.error(f"Match {match_id} does not exist (broadcast task race condition?)")
    # Обработка всех остальных исключений
    except Exception as e:
        logger.exception(f"Error in broadcast_minute_events_in_chunks for match {match_id}, minute {minute}: {e}")
        # Не перевыбрасываем ошибку, чтобы не зацикливать задачу при сбое


@shared_task(name='matches.simulate_match_realtime')
def simulate_match_realtime(match_id: int, tick_seconds: int = TICK_SECONDS):
    """Simulate a match minute by minute using a fixed tick duration."""
    logger.info(
        f"Starting realtime simulation for match {match_id} with tick={tick_seconds}s"
    )
    while True:
        tick_start = time.monotonic()
        try:
            with transaction.atomic():
                match = Match.objects.select_for_update().get(id=match_id)

                if match.status != 'in_progress':
                    logger.info(
                        f"Match {match_id} ended with status {match.status}. Stopping realtime simulation."
                    )
                    break

                minute_to_simulate = match.current_minute
                from .match_simulation import simulate_one_minute

                updated_match = simulate_one_minute(match)
                if updated_match:
                    updated_match.save()
                    logger.info(
                        f"Simulated minute {minute_to_simulate + 1} for match {match_id}"
                    )
                else:
                    logger.warning(
                        f"Simulation returned None for match {match_id} at minute {minute_to_simulate + 1}"
                    )

        except Match.DoesNotExist:
            logger.error(f"Match {match_id} not found during realtime simulation")
            break
        except Exception as e:
            logger.exception(
                f"Error during realtime simulation of match {match_id}: {e}"
            )

        # Отправляем события этой минуты отдельной задачей
        broadcast_minute_events_in_chunks.delay(match_id, minute_to_simulate + 1, duration=4)

        elapsed = time.monotonic() - tick_start
        remaining = tick_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        else:
            logger.warning(
                f"Minute {minute_to_simulate + 1} for match {match_id} took {elapsed:.2f}s which exceeds tick"
            )

    logger.info(f"Realtime simulation completed for match {match_id}")
    return f"Match {match_id} simulation finished"

# --- КОНЕЦ ФАЙЛА matches/tasks.py ---
