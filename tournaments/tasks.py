# tournaments/tasks.py

import time
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction, OperationalError
from django.core.management import call_command
from matches.models import Match
from players.models import Player # Убедитесь, что импорт есть
from clubs.models import Club     # Убедитесь, что импорт есть
from .models import Season, Championship, League
import random # Убедитесь, что импорт есть
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def retry_on_db_lock(func, max_attempts=3, delay=1):
    """
    Декоратор для повторных попыток в случае Database is locked (SQLite).
    """
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "database is locked" in str(e) and attempts < max_attempts - 1:
                    attempts += 1
                    time.sleep(delay)
                    continue
                raise
    return wrapper


@shared_task(name='tournaments.simulate_active_matches', bind=True)
def simulate_active_matches(self):
    """
    Пошаговая симуляция матчей (каждая «минута»).
    Запускается периодически (например, каждые 5 секунд).
    """
    now = timezone.now()
    logger.info(f"Starting active matches simulation at {now}")

    matches = Match.objects.filter(status='in_progress')
    if not matches.exists():
        logger.info("No matches in progress at the moment.")
        return "No matches in progress"

    # Импорт здесь, чтобы избежать циклических зависимостей, если tasks импортируются в match_simulation
    from matches.match_simulation import simulate_one_minute

    for match in matches:
        try:
            # Используем select_for_update для блокировки строки матча на время симуляции минуты
            with transaction.atomic():
                match_locked = Match.objects.select_for_update().get(id=match.id)
                # Передаем заблокированный объект в симуляцию
                updated_match = simulate_one_minute(match_locked) 
                # simulate_one_minute должен вернуть обновленный объект match
                if updated_match: # Убедимся, что simulate_one_minute что-то вернул
                    updated_match.save() # Сохраняем изменения
                    logger.info(
                        f"Simulated one minute for match {updated_match.id} "
                        f"({updated_match.home_team} vs {updated_match.away_team}, current_minute={updated_match.current_minute})"
                    )
                else:
                     logger.warning(f"simulate_one_minute did not return a match object for ID {match.id}")

        except Match.DoesNotExist:
             logger.warning(f"Match {match.id} disappeared during simulation loop.")
        except OperationalError as e:
             # Ловим ошибку блокировки здесь тоже, если select_for_update не помог сразу
             logger.error(f"Database lock error during simulation for match {match.id}: {e}")
             # Возможно, стоит пропустить эту итерацию или повторить позже
        except Exception as e:
             logger.exception(f"Unexpected error during simulation for match {match.id}: {e}")


    return f"Attempted simulation for {matches.count()} matches"


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

            logger.info(
                f"Checking season {current_season.number} (end date: {current_season.end_date})"
            )

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
                logger.info(f"Season {current_season.number} conditions met. Starting end-season process...")

                # На всякий случай еще раз проверим незавершенные матчи (хотя all_matches_played должно было это покрыть)
                unfinished_matches = Match.objects.filter(
                    championshipmatch__championship__season=current_season,
                    status__in=['scheduled', 'in_progress', 'paused'] # Добавим paused
                ).count()

                if unfinished_matches > 0:
                    logger.warning(f"Season {current_season.number} end date passed, but {unfinished_matches} matches are not finished. Postponing season end.")
                    return f"Season {current_season.number} has {unfinished_matches} unfinished matches"

                logger.info("Processing teams transitions between divisions...")
                call_command('handle_season_transitions')

                current_season.is_active = False
                current_season.save()
                logger.info(f"Season {current_season.number} marked as inactive.")

                logger.info("Creating new season...")
                call_command('create_new_season')

                new_season = Season.objects.get(is_active=True)
                championships = Championship.objects.filter(season=new_season)
                total_teams = sum(c.teams.count() for c in championships)

                logger.info(
                    f"Season {current_season.number} ended successfully. "
                    f"Created new season {new_season.number} with "
                    f"{championships.count()} championships and {total_teams} teams"
                )
                return (
                    f"Season {current_season.number} ended. "
                    f"New season {new_season.number} created."
                )
            else:
                 logger.info(f"Season {current_season.number} is still active. End date passed: {is_end_date_passed}, All matches played: {all_matches_played}")
                 return f"Season {current_season.number} is still active"

    except Season.DoesNotExist:
        logger.warning("No active season found. Attempting to create one.")
        try:
             # Попытка создать сезон, если ни одного активного нет
             call_command('create_new_season')
             logger.info("Initial season created.")
             return "No active season found, created initial season."
        except Exception as e_create:
             logger.error(f"Failed to create initial season: {e_create}")
             return "No active season found, failed to create initial one."
    except Exception as e:
        logger.error(f"Error in season end check: {str(e)}")
        # Не перевыбрасываем ошибку, чтобы не останавливать Celery Beat
        return f"Error in season end check: {str(e)}"


def extract_player_ids_from_lineup(current_lineup):
    """
    Извлекает ID игроков из словаря состава (ключи '0'-'10').
    Ожидает, что current_lineup - это внутренний словарь {'0': {...}, '1': {...}, ...}.
    """
    player_ids = set()
    if not isinstance(current_lineup, dict):
        logger.warning(f"extract_player_ids_from_lineup expects a dict, got {type(current_lineup)}")
        return player_ids

    for slot_index_str, player_data in current_lineup.items():
        if isinstance(player_data, dict):
            pid_str = player_data.get('playerId')
            if pid_str:
                try:
                    player_ids.add(int(pid_str))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid playerId format: {pid_str} in slot {slot_index_str}")
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
    logger.info(f"Attempting to complete lineup for {club.name}. Initial count: {len(current_lineup)}. Data: {current_lineup}")

    all_players_qs = club.player_set.all()
    all_players_map = {p.id: p for p in all_players_qs} # Словарь для быстрого доступа по ID
    total_players_in_club = len(all_players_map)

    if total_players_in_club < 11:
        logger.warning(f"Club {club.name} has less than 11 players ({total_players_in_club}). Cannot complete lineup.")
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
                    logger.warning(f"Invalid slot index '{slot_index_str}' in current_lineup. Ignoring.")
                    continue
            except (ValueError, TypeError):
                logger.warning(f"Invalid slot index key '{slot_index_str}' in current_lineup. Ignoring.")
                continue

            if not isinstance(player_data, dict):
                logger.warning(f"Invalid player_data format in current_lineup slot {slot_index_str}: {player_data}")
                continue

            player_id_str = player_data.get('playerId')
            if not player_id_str:
                logger.warning(f"Missing playerId in current_lineup slot {slot_index_str}")
                continue

            try:
                player_id = int(player_id_str)
                if player_id in used_player_ids:
                    logger.warning(f"Duplicate player ID {player_id} found trying to place in slot {slot_index_str}. Skipping.")
                    continue

                player_obj = all_players_map.get(player_id)
                if not player_obj:
                    logger.warning(f"Player with ID {player_id} from current_lineup slot {slot_index_str} not found in club {club.name}. Skipping.")
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
                logger.warning(f"Invalid player ID format '{player_id_str}' in current_lineup slot {slot_index_str}. Skipping.")
                continue
    else:
        logger.warning(f"complete_lineup received current_lineup not as dict: {type(current_lineup)}. Starting fresh.")
        # Если current_lineup не словарь, начинаем с нуля

    logger.info(f"After processing current_lineup: {len(final_lineup)} players placed, used IDs: {used_player_ids}")

    # --- 2. Проверяем и добавляем вратаря, если его нет ---
    if '0' not in final_lineup:
        # Ищем вратаря среди НЕиспользованных игроков
        available_gks = [
            p for p_id, p in all_players_map.items()
            if p.position == 'Goalkeeper' and p_id not in used_player_ids
        ]
        if not available_gks:
            logger.error(f"Club {club.name} has no available Goalkeeper to complete the lineup.")
            return None # Не можем сформировать состав без вратаря

        keeper = available_gks[0] # Берем первого доступного
        final_lineup['0'] = {
            "playerId": str(keeper.id),
            "slotType": "goalkeeper",
            "slotLabel": "GK",
            "playerPosition": keeper.position
        }
        used_player_ids.add(keeper.id)
        logger.info(f"Added missing goalkeeper: {keeper.id}")
    # Если вратарь уже был в final_lineup['0'], проверяем его позицию (опционально)
    elif final_lineup.get('0'):
         goalkeeper_data = final_lineup['0']
         keeper_id = int(goalkeeper_data.get('playerId', -1))
         keeper_obj = all_players_map.get(keeper_id)
         if keeper_obj and keeper_obj.position != 'Goalkeeper':
            logger.warning(f"Player in slot 0 (ID: {keeper_id}) is not a Goalkeeper! Position: {keeper_obj.position}")
            # Здесь можно решить: заменить его или оставить. Пока оставляем.

    # --- 3. Добавляем недостающих полевых игроков ---
    needed_players = 11 - len(final_lineup)
    if needed_players <= 0:
        # Проверяем, что все ключи 0-10 есть
        if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
             logger.info(f"Lineup already complete with 11 players.")
             return final_lineup # Состав уже полный и корректный
        else:
             logger.warning(f"Lineup has {len(final_lineup)} players but structure might be wrong (missing keys?). Needs rebuild.")
             # Если игроков 11, но ключи не 0-10, лучше пересобрать или вернуть None
             return None # Неожиданная ситуация

    # Ищем доступных полевых игроков (не вратарей и не использованных)
    available_field_players = [
        p for p_id, p in all_players_map.items()
        if p.position != 'Goalkeeper' and p_id not in used_player_ids
    ]

    if len(available_field_players) < needed_players:
        logger.error(f"Club {club.name} needs {needed_players} more field players, but only {len(available_field_players)} are available.")
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
                logger.info(f"Added filler player {player_to_add.id} to slot {slot_key}")
            else:
                # Этого не должно произойти, если расчеты верны
                logger.error(f"Ran out of filler players while trying to fill slot {slot_key}. Needed: {needed_players}, Available: {len(available_field_players)}, Chosen: {len(chosen_fillers)}")
                return None # Ошибка в логике

    # Финальная проверка
    if len(final_lineup) == 11 and all(str(i) in final_lineup for i in range(11)):
        logger.info(f"Successfully completed lineup for {club.name}: {final_lineup}")
        return final_lineup
    else:
        logger.error(f"Failed to complete lineup for {club.name}. Result has {len(final_lineup)} players, expected 11 with keys 0-10. Data: {final_lineup}")
        return None # Не удалось собрать 11 игроков или ключи не 0-10


@shared_task(name='tournaments.start_scheduled_matches')
def start_scheduled_matches():
    """
    Переводит матчи из scheduled в in_progress и копирует/дополняет составы команд.
    """
    now = timezone.now()
    logger.info("===== STARTING start_scheduled_matches TASK =====")

    # Используем transaction.atomic для каждой команды отдельно,
    # чтобы ошибка в одной не откатывала другие.
    matches_to_process = Match.objects.filter(
        status='scheduled',
        datetime__lte=now
    )
    started_count = 0
    skipped_count = 0

    logger.info(f"Found {matches_to_process.count()} scheduled matches ready to start.")

    for match in matches_to_process:
        try:
            with transaction.atomic():
                # Блокируем матч на время обработки
                match_locked = Match.objects.select_for_update().get(pk=match.pk)

                # Проверяем статус еще раз внутри транзакции, вдруг он изменился
                if match_locked.status != 'scheduled' or match_locked.datetime > timezone.now():
                    logger.warning(f"Match {match_locked.id} status changed or datetime invalid after locking. Skipping.")
                    skipped_count += 1
                    continue

                logger.info(f"Processing match ID={match_locked.id}: {match_locked.home_team} vs {match_locked.away_team}")

                final_home_lineup = None
                final_away_lineup = None
                home_tactic = 'balanced'
                away_tactic = 'balanced'

                # --- Обрабатываем домашнюю команду ---
                home_data_from_club = match_locked.home_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(home_data_from_club, dict) or 'lineup' not in home_data_from_club:
                     logger.warning(f"Invalid lineup format for home team {match_locked.home_team.name} (ID: {match_locked.home_team.id}). Using empty lineup.")
                     home_data_from_club = {"lineup": {}, "tactic": "balanced"}

                home_lineup_from_club = home_data_from_club.get('lineup', {})
                home_tactic = home_data_from_club.get('tactic', 'balanced')

                if isinstance(home_lineup_from_club, dict) and len(home_lineup_from_club) >= 11 and all(str(i) in home_lineup_from_club for i in range(11)):
                     # Если состав в клубе уже полный (11 игроков, ключи 0-10), просто берем его
                     logger.info(f"Using full lineup from home team {match_locked.home_team.name}")
                     final_home_lineup = home_lineup_from_club
                else:
                     # Если состав неполный или некорректный, пытаемся дополнить
                     logger.info(f"Home lineup for {match_locked.home_team.name} is incomplete or invalid ({len(home_lineup_from_club)} players). Attempting to complete...")
                     completed_home = complete_lineup(match_locked.home_team, home_lineup_from_club)
                     if completed_home is None:
                         logger.error(
                             f"Failed to complete lineup for home team {match_locked.home_team.name}. "
                             f"Skipping match {match_locked.id}."
                         )
                         skipped_count += 1
                         continue # Пропускаем этот матч, откатываем транзакцию для него
                     final_home_lineup = completed_home

                # --- Обрабатываем гостевую команду (аналогично) ---
                away_data_from_club = match_locked.away_team.lineup or {"lineup": {}, "tactic": "balanced"}
                if not isinstance(away_data_from_club, dict) or 'lineup' not in away_data_from_club:
                     logger.warning(f"Invalid lineup format for away team {match_locked.away_team.name} (ID: {match_locked.away_team.id}). Using empty lineup.")
                     away_data_from_club = {"lineup": {}, "tactic": "balanced"}

                away_lineup_from_club = away_data_from_club.get('lineup', {})
                away_tactic = away_data_from_club.get('tactic', 'balanced')

                if isinstance(away_lineup_from_club, dict) and len(away_lineup_from_club) >= 11 and all(str(i) in away_lineup_from_club for i in range(11)):
                     logger.info(f"Using full lineup from away team {match_locked.away_team.name}")
                     final_away_lineup = away_lineup_from_club
                else:
                     logger.info(f"Away lineup for {match_locked.away_team.name} is incomplete or invalid ({len(away_lineup_from_club)} players). Attempting to complete...")
                     completed_away = complete_lineup(match_locked.away_team, away_lineup_from_club)
                     if completed_away is None:
                         logger.error(
                             f"Failed to complete lineup for away team {match_locked.away_team.name}. "
                             f"Skipping match {match_locked.id}."
                         )
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
                    match_locked.save()
                    started_count += 1
                    logger.info(f"Match {match_locked.id} successfully started and lineups set.")
                else:
                    # Эта ветка не должна сработать, если continue выше отработали правильно
                    logger.error(f"Lineups were not finalized for match {match_locked.id}. Skipping.")
                    skipped_count += 1
                    continue

        except Match.DoesNotExist:
             logger.warning(f"Match {match.id} was deleted before processing.")
             skipped_count += 1
        except OperationalError as e_lock:
             logger.error(f"Database lock error processing match {match.id}: {e_lock}. Skipping this match.")
             skipped_count += 1
        except Exception as e_match:
             logger.exception(f"Unexpected error processing match {match.id}: {e_match}. Skipping this match.")
             skipped_count += 1


    logger.info(f"===== FINISHED start_scheduled_matches TASK: Started {started_count}, Skipped {skipped_count} =====")
    return f"{started_count} matches started, {skipped_count} skipped."

# --- КОНЕЦ ФАЙЛА tournaments/tasks.py ---