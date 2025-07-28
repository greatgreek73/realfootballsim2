# tournaments/tasks.py

import time
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.conf import settings
from django.core.management import call_command
from matches.models import Match, MatchEvent
from players.models import Player # Убедитесь, что импорт есть
from clubs.models import Club     # Убедитесь, что импорт есть
from .models import Season, Championship, League
import random # Убедитесь, что импорт есть
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("match_creation")


@shared_task(name='tournaments.simulate_active_matches', bind=True)
def simulate_active_matches(self):
    """
    Пошаговая симуляция матчей - теперь по ДЕЙСТВИЯМ, а не по минутам.
    Запускается периодически (например, каждые 2 секунды).
    """
    now = timezone.now()
    logger.info(f"🔁 [simulate_active_matches] Запуск симуляции активных матчей в {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("🔍 Нет матчей со статусом 'in_progress'.")
        return "No matches in progress"

    logger.info(f"✅ Найдено {matches.count()} матчей для симуляции.")

    from matches.match_simulation import simulate_one_action, send_update
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from django.core.cache import cache
    
    channel_layer = get_channel_layer()

    for match in matches:
        try:
            logger.info(f"🔒 Попытка блокировки матча ID={match.id} для симуляции...")

            with transaction.atomic():
                match_locked = Match.objects.select_for_update().get(id=match.id)

                # Инициализируем время начала и последнего обновления, если не установлены
                if match_locked.started_at is None:
                    match_locked.started_at = timezone.now()
                    match_locked.save(update_fields=['started_at'])
                    logger.info(f"✅ Установлено время начала для матча ID={match_locked.id}")

                if match_locked.last_minute_update is None:
                    match_locked.last_minute_update = timezone.now()
                    match_locked.save(update_fields=['last_minute_update'])
                    logger.info(f"✅ Установлено время последнего обновления для матча ID={match_locked.id}")

                # Если ожидаем начала следующей минуты, пропускаем обработку
                if match_locked.waiting_for_next_minute:
                    logger.info(
                        f"⏭️ Матч ID={match_locked.id} ждёт следующую минуту, пропуск."
                    )
                    continue
                
                # Получаем счетчик действий из кеша
                cache_key = f"match_{match_locked.id}_actions_in_minute"
                actions_in_current_minute = cache.get(cache_key, 0)
                
                # Проверяем, не закончился ли матч
                if match_locked.current_minute >= 90:
                    match_locked.status = 'finished'
                    match_locked.save()
                    cache.delete(cache_key)  # Очищаем кеш
                    logger.info(f"🏁 Матч ID={match_locked.id} завершен")
                    continue
                
                # Симулируем одно действие
                logger.info(
                    f"⚙️ Симуляция действия для матча ID={match_locked.id}, "
                    f"минута {match_locked.current_minute}, действие #{actions_in_current_minute + 1}"
                )
                
                result = simulate_one_action(match_locked)

                possessing_team_id = None
                if match_locked.possession_indicator == 1:
                    possessing_team_id = str(match_locked.home_team_id)
                elif match_locked.possession_indicator == 2:
                    possessing_team_id = str(match_locked.away_team_id)

                # Если действие завершает атаку, ждём следующей минуты
                if result.get('continue', True) is False:
                    match_locked.waiting_for_next_minute = True
                
                
                # Создаем событие, если оно есть
                if result.get('event'):
                    event = MatchEvent.objects.create(**result['event'])
                    logger.info(
                        f"✅ Действие создано: {result['action_type']} "
                        f"для матча ID={match_locked.id}"
                    )
                    
                    # Отправляем событие СРАЗУ через WebSocket
                    if channel_layer:
                        event_data = {
                            "minute": event.minute,
                            "event_type": event.event_type,
                            "description": event.description,
                            "player_name": f"{event.player.first_name} {event.player.last_name}" if event.player else "",
                            "related_player_name": f"{event.related_player.first_name} {event.related_player.last_name}" if event.related_player else ""
                        }

                        
                        message_payload = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
                                "home_score": match_locked.home_score,
                                "away_score": match_locked.away_score,
                                "status": match_locked.status,
                                "st_shoots": match_locked.st_shoots,
                                "st_passes": match_locked.st_passes,
                                "st_possessions": match_locked.st_possessions,
                                "st_fouls": match_locked.st_fouls,
                                "st_injury": match_locked.st_injury,
                                "home_momentum": match_locked.home_momentum,
                                "away_momentum": match_locked.away_momentum,
                                "current_zone": match_locked.current_zone,
                                "possessing_team_id": possessing_team_id,
                                "events": [event_data],
                                "partial_update": True,
                                "action_based": True  # Новый флаг для пошаговой симуляции
                            }
                        }
                        
                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            message_payload
                        )
                        
                        logger.info(
                            f"📡 Событие отправлено через WebSocket для матча ID={match_locked.id}"
                        )
                
                # Проверяем дополнительное событие (например, травма после фола)
                if result.get('additional_event'):
                    add_event = MatchEvent.objects.create(**result['additional_event'])
                    # Отправляем и его через WebSocket
                    if channel_layer:
                        add_event_data = {
                            "minute": add_event.minute,
                            "event_type": add_event.event_type,
                            "description": add_event.description,
                            "player_name": f"{add_event.player.first_name} {add_event.player.last_name}" if add_event.player else "",
                            "related_player_name": ""
                        }
                        
                        add_message_payload = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
                                "home_score": match_locked.home_score,
                                "away_score": match_locked.away_score,
                                "status": match_locked.status,
                                "st_shoots": match_locked.st_shoots,
                                "st_passes": match_locked.st_passes,
                                "st_possessions": match_locked.st_possessions,
                                "st_fouls": match_locked.st_fouls,
                                "st_injury": match_locked.st_injury,
                                "home_momentum": match_locked.home_momentum,
                                "away_momentum": match_locked.away_momentum,
                                "current_zone": match_locked.current_zone,
                                "possessing_team_id": possessing_team_id,
                                "events": [add_event_data],
                                "partial_update": True,
                                "action_based": True
                            }
                        }
                        
                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload
                        )

                # Обрабатываем второе дополнительное событие (например, удар после перехвата)
                if result.get('second_additional_event'):
                    add_event2 = MatchEvent.objects.create(**result['second_additional_event'])
                    if channel_layer:
                        add_event_data2 = {
                            "minute": add_event2.minute,
                            "event_type": add_event2.event_type,
                            "description": add_event2.description,
                            "player_name": f"{add_event2.player.first_name} {add_event2.player.last_name}" if add_event2.player else "",
                            "related_player_name": ""
                        }

                        add_message_payload2 = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
                                "home_score": match_locked.home_score,
                                "away_score": match_locked.away_score,
                                "status": match_locked.status,
                                "st_shoots": match_locked.st_shoots,
                                "st_passes": match_locked.st_passes,
                                "st_possessions": match_locked.st_possessions,
                                "st_fouls": match_locked.st_fouls,
                                "st_injury": match_locked.st_injury,
                                "home_momentum": match_locked.home_momentum,
                                "away_momentum": match_locked.away_momentum,
                                "current_zone": match_locked.current_zone,
                                "possessing_team_id": possessing_team_id,
                                "events": [add_event_data2],
                                "partial_update": True,
                                "action_based": True
                            }
                        }

                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload2
                        )

                # Обрабатываем третье дополнительное событие
                if result.get('third_additional_event'):
                    add_event3 = MatchEvent.objects.create(**result['third_additional_event'])
                    if channel_layer:
                        add_event_data3 = {
                            "minute": add_event3.minute,
                            "event_type": add_event3.event_type,
                            "description": add_event3.description,
                            "player_name": f"{add_event3.player.first_name} {add_event3.player.last_name}" if add_event3.player else "",
                            "related_player_name": ""
                        }

                        add_message_payload3 = {
                            "type": "match_update",
                            "data": {
                                "match_id": match_locked.id,
                                "minute": match_locked.current_minute,
                                "home_score": match_locked.home_score,
                                "away_score": match_locked.away_score,
                                "status": match_locked.status,
                                "st_shoots": match_locked.st_shoots,
                                "st_passes": match_locked.st_passes,
                                "st_possessions": match_locked.st_possessions,
                                "st_fouls": match_locked.st_fouls,
                                "st_injury": match_locked.st_injury,
                                "home_momentum": match_locked.home_momentum,
                                "away_momentum": match_locked.away_momentum,
                                "current_zone": match_locked.current_zone,
                                "possessing_team_id": possessing_team_id,
                                "events": [add_event_data3],
                                "partial_update": True,
                                "action_based": True
                            }
                        }

                        async_to_sync(channel_layer.group_send)(
                            f"match_{match_locked.id}",
                            add_message_payload3
                        )

                # Если событие не создано, отправляем обновление состояния
                if result.get('event') is None:
                    possessing_team = None
                    player_with_ball = match_locked.current_player_with_ball
                    if player_with_ball:
                        if player_with_ball.club_id == match_locked.home_team_id:
                            possessing_team = match_locked.home_team
                        elif player_with_ball.club_id == match_locked.away_team_id:
                            possessing_team = match_locked.away_team
                    send_update(match_locked, possessing_team)
                
                # Увеличиваем счетчик действий
                actions_in_current_minute += 1
                cache.set(cache_key, actions_in_current_minute, timeout=300)  # 5 минут таймаут
                
                # Сохраняем состояние матча
                match_locked.save()

        except Match.DoesNotExist:
            logger.warning(f"❌ Матч ID={match.id} исчез из базы во время симуляции.")
        except OperationalError as e:
            logger.error(f"🔒 Ошибка блокировки базы данных для матча {match.id}: {e}")
        except Exception as e:
            logger.exception(f"🔥 Ошибка при симуляции матча {match.id}: {e}")

    return f"Simulated actions for {matches.count()} matches"



@shared_task(name='tournaments.check_season_end', bind=True)
def check_season_end(self):
    """
    Проверяет окончание сезона и создаёт новый при необходимости.
    Запускается, к примеру, раз в день или раз в час (согласно настройкам Celery Beat).
    """
    try:
        with transaction.atomic():
            # Используем select_for_update для предотвращения гонок при проверке/завершении сезона
            current_season = Season.objects.select_for_update().get(is_active=True)
            today = timezone.now().date()

            is_end_date_passed = today > current_season.end_date

            # Проверяем, все ли матчи сезона завершены
            all_matches_in_season = Match.objects.filter(
                championshipmatch__championship__season=current_season
            )
            finished_matches_count = all_matches_in_season.filter(status='finished').count()
            total_matches_count = all_matches_in_season.count() # Общее количество матчей в сезоне

            # Условие завершения: дата прошла И все матчи сыграны (или нет матчей)
            all_matches_played = (total_matches_count == 0 or finished_matches_count == total_matches_count)

            if is_end_date_passed and all_matches_played:
                # На всякий случай еще раз проверим незавершенные матчи (хотя all_matches_played должно было это покрыть)
                unfinished_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress', 'paused'] # Добавим paused
                ).count()

                if unfinished_matches > 0:
                    return f"Season {current_season.number} has {unfinished_matches} unfinished matches"

                call_command('handle_season_transitions')

                current_season.is_active = False
                current_season.save()

                call_command('create_new_season')

                new_season = Season.objects.get(is_active=True)
                championships = Championship.objects.filter(season=new_season)
                total_teams = sum(c.teams.count() for c in championships)
                return (
                    f"Season {current_season.number} ended. "
                    f"New season {new_season.number} created."
                )
            else:
                 return f"Season {current_season.number} is still active"

    except Season.DoesNotExist:
        try:
             # Попытка создать сезон, если ни одного активного нет
             call_command('create_new_season')
             return "No active season found, created initial season."
        except Exception as e_create:
             return "No active season found, failed to create initial one."
    except Exception as e:
        # Не перевыбрасываем ошибку, чтобы не останавливать Celery Beat
        return f"Error in season end check: {str(e)}"


def extract_player_ids_from_lineup(current_lineup):
    """
    Извлекает ID игроков из словаря состава (ключи '0'-'10').
    Ожидает, что current_lineup - это внутренний словарь {'0': {...}, '1': {...}, ...}.
    """
    player_ids = set()
    if not isinstance(current_lineup, dict):
        return player_ids

    for slot_index_str, player_data in current_lineup.items():
        if isinstance(player_data, dict):
            pid_str = player_data.get('playerId')
            if pid_str:
                try:
                    player_ids.add(int(pid_str))
                except (ValueError, TypeError):
                    pass
        # Можно добавить обработку старого формата, если он еще где-то используется
        # else: ...

    return player_ids


# --- ИСПРАВЛЕННАЯ ФУНКЦИЯ complete_lineup ---
def complete_lineup(club: Club, current_lineup: dict):
    """
    Дополняет переданный состав до 11 игроков, используя существующих
    и добавляя недостающих случайным образом без дублирования.
    Возвращает полный состав (словарь 0-10) или None, если невозможно.
    Ожидает current_lineup в формате {'0': {...}, '1': {...}, ...}.
    """
    all_players_qs = club.player_set.all()
    all_players_map = {p.id: p for p in all_players_qs} # Словарь для быстрого доступа по ID
    total_players_in_club = len(all_players_map)

    if total_players_in_club < 11:
        return None

    final_lineup = {} # Результат будет здесь (копия или дополненный)
    used_player_ids = set()

    # --- 1. Обрабатываем текущий состав (ключи '0' - '10') ---
    if isinstance(current_lineup, dict):
        for slot_index_str, player_data in current_lineup.items():
            # Проверяем корректность ключа слота
            try:
                slot_index_int = int(slot_index_str)
                if not (0 <= slot_index_int <= 10):
                    continue
            except (ValueError, TypeError):
                continue

            if not isinstance(player_data, dict):
                continue

            player_id_str = player_data.get('playerId')
            if not player_id_str:
                continue

            try:
                player_id = int(player_id_str)
                if player_id in used_player_ids:
                    continue

                player_obj = all_players_map.get(player_id)
                if not player_obj:
                    continue

                # Добавляем игрока из текущего состава в итоговый
                final_lineup[slot_index_str] = {
                    "playerId": str(player_obj.id),
                    "slotType": player_data.get("slotType", "unknown"), # Сохраняем тип слота, если есть
                    "slotLabel": player_data.get("slotLabel", f"SLOT_{slot_index_str}"),
                    "playerPosition": player_obj.position
                }
                used_player_ids.add(player_id)

            except (ValueError, TypeError):
                continue

    # --- 2. Проверяем и добавляем вратаря, если его нет ---
    if '0' not in final_lineup:
        # Ищем вратаря среди НЕиспользованных игроков
        available_gks = [
            p for p_id, p in all_players_map.items()
            if p.position == 'Goalkeeper' and p_id not in used_player_ids
        ]
        if not available_gks:
            return None # Не можем сформировать состав без вратаря

        keeper = available_gks[0] # Берем первого доступного
        final_lineup['0'] = {
            "playerId": str(keeper.id),
            "slotType": "goalkeeper",
            "slotLabel": "GK",
            "playerPosition": keeper.position
        }
        used_player_ids.add(keeper.id)

    # --- 3. Добавляем недостающих полевых игроков ---
    needed_players = 11 - len(final_lineup)
    if needed_players <= 0:
        # Проверяем, что все ключи 0-10 есть
        if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
            return final_lineup # Состав уже полный и корректный
        else:
            return None # Неожиданная ситуация

    # Ищем доступных полевых игроков (не вратарей и не использованных)
    available_field_players = [
        p for p_id, p in all_players_map.items()
        if p.position != 'Goalkeeper' and p_id not in used_player_ids
    ]

    if len(available_field_players) < needed_players:
        return None # Не хватает игроков для докомплектации

    # Выбираем случайных из доступных
    chosen_fillers = random.sample(available_field_players, needed_players)
    filler_idx = 0

    # Заполняем пустые слоты 1-10
    for i in range(1, 11):
        slot_key = str(i)
        if slot_key not in final_lineup:
            if filler_idx < len(chosen_fillers):
                player_to_add = chosen_fillers[filler_idx]
                final_lineup[slot_key] = {
                    "playerId": str(player_to_add.id),
                    "slotType": "auto", # Тип слота не известен, ставим авто
                    "slotLabel": f"AUTO_{slot_key}",
                    "playerPosition": player_to_add.position
                }
                used_player_ids.add(player_to_add.id) # Добавляем на всякий случай
                filler_idx += 1
            else:
                return None # Ошибка в логике

    # Финальная проверка
    if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
        return final_lineup
    else:
        return None # Не удалось собрать 11 игроков или ключи не 0-10


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи из scheduled в in_progress и копирует/дополняет составы команд.
    """
    now = timezone.now()

    # Используем transaction.atomic для каждой команды отдельно,
    # чтобы ошибка в одной не откатывала другие.
    matches_to_process = Match.objects.filter(
        status='scheduled',
        datetime__lte=now
    )
    started_count = 0
    skipped_count = 0

    for match in matches_to_process:
        try:
            with transaction.atomic():
                # Блокируем матч на время обработки
                match_locked = Match.objects.select_for_update().get(pk=match.pk)

                # Проверяем статус еще раз внутри транзакции, вдруг он изменился
                if match_locked.status != 'scheduled' or match_locked.datetime > timezone.now():
                    skipped_count += 1
                    continue

                final_home_lineup = None
                final_away_lineup = None
                home_tactic = 'balanced'
                away_tactic = 'balanced'

                # --- Обрабатываем домашнюю команду ---
                home_data_from_club = match_locked.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(home_data_from_club, dict) or 'lineup' not in home_data_from_club:
                     home_data_from_club = {"lineup": {}, "tactic": "balanced"}

                home_lineup_from_club = home_data_from_club.get('lineup', {})
                home_tactic = home_data_from_club.get('tactic', 'balanced')

                if isinstance(home_lineup_from_club, dict) and len(home_lineup_from_club) >= 11 and all(str(i) in home_lineup_from_club for i in range(11)):
                     # Если состав в клубе уже полный (11 игроков, ключи 0-10), просто берем его
                     final_home_lineup = home_lineup_from_club
                else:
                     # Если состав неполный или некорректный, пытаемся дополнить
                     completed_home = complete_lineup(match_locked.home_team, home_lineup_from_club)
                     if completed_home is None:
                         skipped_count += 1
                         continue # Пропускаем этот матч, откатываем транзакцию для него
                     final_home_lineup = completed_home

                # --- Обрабатываем гостевую команду (аналогично) ---
                away_data_from_club = match_locked.away_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(away_data_from_club, dict) or 'lineup' not in away_data_from_club:
                     away_data_from_club = {"lineup": {}, "tactic": "balanced"}

                away_lineup_from_club = away_data_from_club.get('lineup', {})
                away_tactic = away_data_from_club.get('tactic', 'balanced')

                if isinstance(away_lineup_from_club, dict) and len(away_lineup_from_club) >= 11 and all(str(i) in away_lineup_from_club for i in range(11)):
                     final_away_lineup = away_lineup_from_club
                else:
                     completed_away = complete_lineup(match_locked.away_team, away_lineup_from_club)
                     if completed_away is None:
                         skipped_count += 1
                         continue # Пропускаем этот матч
                     final_away_lineup = completed_away

                # --- Если оба состава готовы, сохраняем и меняем статус ---
                if final_home_lineup and final_away_lineup:
                    match_locked.home_lineup = final_home_lineup
                    match_locked.home_tactic = home_tactic
                    match_locked.away_lineup = final_away_lineup
                    match_locked.away_tactic = away_tactic
                    match_locked.status = 'in_progress'
                    now_ts = timezone.now()
                    match_locked.started_at = now_ts
                    match_locked.last_minute_update = now_ts
                    match_locked.waiting_for_next_minute = False
                    match_locked.save()
                    started_count += 1
                else:
                    # Эта ветка не должна сработать, если continue выше отработали правильно
                    skipped_count += 1
                    continue

        except Match.DoesNotExist:
             skipped_count += 1
        except OperationalError as e_lock:
             skipped_count += 1
        except Exception as e_match:
             skipped_count += 1

    return f"{started_count} matches started, {skipped_count} skipped."


@shared_task(name='tournaments.advance_match_minutes')
def advance_match_minutes():
    """Advance match minutes based on real elapsed time."""
    now = timezone.now()
    matches = Match.objects.filter(status='in_progress')
    if not matches:
        return 'No matches to update'

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from django.core.cache import cache

    channel_layer = get_channel_layer()

    for match in matches:
        if match.last_minute_update is None:
            match.last_minute_update = now
            match.save(update_fields=["last_minute_update"])
            continue

        if not match.waiting_for_next_minute:
            continue

        elapsed = (now - match.last_minute_update).total_seconds()
        if elapsed < settings.MATCH_MINUTE_REAL_SECONDS:
            continue

        if match.current_minute < 90:
            match.current_minute += 1
            info_event = MatchEvent.objects.create(
                match=match,
                minute=match.current_minute,
                event_type="info",
                description=f"Minute {match.current_minute}: Play continues...",
            )

            if channel_layer:
                info_event_data = {
                    "minute": info_event.minute,
                    "event_type": info_event.event_type,
                    "description": info_event.description,
                    "player_name": "",
                    "related_player_name": "",
                }

                possessing_team_id = None
                if match.possession_indicator == 1:
                    possessing_team_id = str(match.home_team_id)
                elif match.possession_indicator == 2:
                    possessing_team_id = str(match.away_team_id)

                payload = {
                    "type": "match_update",
                    "data": {
                        "match_id": match.id,
                        "minute": match.current_minute,
                        "home_score": match.home_score,
                        "away_score": match.away_score,
                        "status": match.status,
                        "st_shoots": match.st_shoots,
                        "st_passes": match.st_passes,
                        "st_possessions": match.st_possessions,
                        "st_fouls": match.st_fouls,
                        "st_injury": match.st_injury,
                        "home_momentum": match.home_momentum,
                        "away_momentum": match.away_momentum,
                        "current_zone": match.current_zone,
                        "possessing_team_id": possessing_team_id,
                        "events": [info_event_data],
                        "partial_update": True,
                        "action_based": True,
                    },
                }

                async_to_sync(channel_layer.group_send)(
                    f"match_{match.id}",
                    payload,
                )

        cache.delete(f"match_{match.id}_actions_in_minute")
        match.waiting_for_next_minute = False
        match.last_minute_update = match.last_minute_update + timedelta(
            seconds=settings.MATCH_MINUTE_REAL_SECONDS
        )
        match.save()

    return f'Updated {matches.count()} matches'

# --- КОНЕЦ ФАЙЛА tournaments/tasks.py ---
