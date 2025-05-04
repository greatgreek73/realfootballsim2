# Файл match_simulation.py

import random
import logging
from django.db import transaction
from django.utils import timezone
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
import time
# Для рассылки обновлений через WebSocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def serialize_player(p: Player):
    """Сериализует данные игрока для отправки."""
    if not p:
        return None
    return {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "position": p.position,
        # "overall": p.overall_rating # Раскомментировать при необходимости
    }

def send_update(match, possessing_team):
    """Отправляет обновление состояния матча через WebSocket."""
    try:
        # Получаем последние 5 событий
        recent_events_qs = match.events.order_by('-id')[:5]
        recent_events = list(reversed(recent_events_qs)) # Показываем в хронологическом порядке
        events_data = []
        for e in recent_events:
            event_player_name = f"{e.player.first_name} {e.player.last_name}" if e.player else ""
            related_player_name = f"{e.related_player.first_name} {e.related_player.last_name}" if e.related_player else ""
            events_data.append({
                "minute": e.minute,
                "event_type": e.event_type,
                "description": e.description,
                "player_name": event_player_name,
                "related_player_name": related_player_name,
            })

        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Cannot get channel layer. Updates will not be sent.")
            return

        # Получаем текущего игрока и его данные
        current_player = match.current_player_with_ball
        current_player_data = serialize_player(current_player)

        update_data = {
            "type": "match_update", # Важно для consumer.py
            "data": {
                "match_id": match.id,
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "st_shoots": match.st_shoots,
                "st_passes": match.st_passes,
                "st_posessions": match.st_posessions, # Опечатка исправлена на 'possessions'
                "st_fouls": match.st_fouls,
                "st_injury": match.st_injury,
                "status": match.status,
                "current_player": current_player_data,
                "current_zone": match.current_zone,
                "possessing_team_id": possessing_team.id if possessing_team else None,
                "events": events_data, # Список последних событий
            }
        }

        # Отправляем асинхронно
        async_to_sync(channel_layer.group_send)(
            f"match_{match.id}",
            update_data
        )
    except Exception as e:
        logger.error(f"Error sending update for match {match.id}: {e}")


def zone_conditions(zone: str):
    """
    Возвращает функцию-предикат для проверки, подходит ли игрок для указанной зоны.
    (Функция не используется в текущей choose_player, но может пригодиться)
    """
    if zone == "GK":
        return lambda p: p.position == "Goalkeeper"
    elif zone == "DEF":
        # Расширяем для разных названий защитных позиций
        return lambda p: "Back" in p.position or "Defender" in p.position or p.position == "CB" or p.position == "LB" or p.position == "RB"
    elif zone in ["DM", "MID"]: # Объединим опорников и центр
        return lambda p: "Midfielder" in p.position and "Defensive" in p.position or p.position == "CM"
    elif zone == "AM":
        return lambda p: "Midfielder" in p.position and "Attacking" in p.position or p.position == "CAM"
    elif zone == "WING": # Для фланговых полузащитников/нападающих
         return lambda p: p.position in ["LW", "RW", "LM", "RM"]
    elif zone == "FWD":
        return lambda p: "Forward" in p.position or "Striker" in p.position or p.position == "ST" or p.position == "CF"
    else: # Если зона не указана или неизвестна, любой игрок подходит
        return lambda p: True

def choose_player(team: Club, zone: str, exclude_ids: set = None) -> Player | None:
    """
    Выбирает случайного игрока из команды для указанной зоны.
    Если зона не 'ANY', пытается найти игрока нужной позиции.
    Если таких нет или зона 'ANY', выбирает любого доступного.
    Возвращает None, если нет подходящих игроков.
    """
    if exclude_ids is None:
        exclude_ids = set()

    players = team.player_set.all() # Получаем всех игроков один раз
    available_players = [p for p in players if p.id not in exclude_ids]

    if not available_players:
        logger.warning(f"No available players in team {team.name} (excluding {exclude_ids})")
        return None

    candidates = []
    if zone != "ANY": # Если нужна конкретная зона
        condition = zone_conditions(zone)
        candidates = [p for p in available_players if condition(p)]

    if candidates:
        # Если есть кандидаты для зоны, выбираем из них
        return random.choice(candidates)
    elif available_players:
         # Если для зоны нет, но есть хоть какие-то игроки, выбираем любого
        logger.debug(f"No players found for zone '{zone}' in team {team.name}, choosing any available player.")
        return random.choice(available_players)
    else:
        # Сюда не должны попасть, но на всякий случай
        return None

def choose_players(team: Club, zone: str, exclude_ids: set = None) -> list[Player]:
    """
    Выбирает ВСЕХ игроков команды, удовлетворяющих условию для зоны.
    (Используется редко, возможно, для сериализации всех игроков зоны)
    """
    if exclude_ids is None:
        exclude_ids = set()
    condition = zone_conditions(zone)
    players = team.player_set.all()
    candidates = [p for p in players if condition(p) and p.id not in exclude_ids]
    return candidates

def get_opponent_team(match: Match, possessing_team: Club) -> Club:
    """Возвращает команду-соперника."""
    return match.away_team if possessing_team.id == match.home_team.id else match.home_team

def auto_select_lineup(club: Club) -> dict:
    """
    Простейшая автогенерация состава (4-4-2).
    Теперь использует новую функцию complete_lineup из tasks.py.
    Возвращает структуру {'lineup': {...}, 'tactic': 'balanced'} или None.
    """
    from tournaments.tasks import complete_lineup # Импортируем актуальную функцию
    logger.info(f"Attempting to auto-select lineup for club {club.name} (ID: {club.id})")
    # Вызываем complete_lineup с пустым начальным составом
    generated_lineup_dict = complete_lineup(club, {})
    if generated_lineup_dict:
        logger.info(f"Auto-selected lineup for {club.name}: {generated_lineup_dict}")
        return {"lineup": generated_lineup_dict, "tactic": "balanced"}
    else:
        logger.warning(f"Failed to auto-select lineup for {club.name}")
        return None # Возвращаем None, если не удалось

def ensure_match_lineup_set(match: Match, for_home: bool) -> bool:
    """
    Проверяет и устанавливает состав команды в матче.
    Если у клуба нет полного состава, пытается сгенерировать его.
    Возвращает True, если состав установлен, False - если не удалось.
    """
    team = match.home_team if for_home else match.away_team
    lineup_attr = 'home_lineup' if for_home else 'away_lineup'
    tactic_attr = 'home_tactic' if for_home else 'away_tactic'

    club_data = team.lineup # Ожидаем {'lineup': {...}, 'tactic': '...'}
    club_lineup = {}
    club_tactic = 'balanced'

    if isinstance(club_data, dict):
        club_lineup = club_data.get('lineup', {})
        club_tactic = club_data.get('tactic', 'balanced')

    # Проверяем полноту и корректность ключей 0-10
    is_complete = (
        isinstance(club_lineup, dict) and
        len(club_lineup) >= 11 and
        all(str(i) in club_lineup for i in range(11))
    )

    if is_complete:
        logger.info(f"Using existing complete lineup from club {team.name} for match {match.id}")
        setattr(match, lineup_attr, club_lineup)
        setattr(match, tactic_attr, club_tactic)
        return True
    else:
        logger.warning(f"Lineup from club {team.name} is incomplete or invalid. Attempting auto-selection...")
        # Используем актуальную функцию автодополнения
        from tournaments.tasks import complete_lineup
        completed_lineup_dict = complete_lineup(team, club_lineup if isinstance(club_lineup, dict) else {})

        if completed_lineup_dict:
            logger.info(f"Successfully generated lineup for {team.name} for match {match.id}")
            setattr(match, lineup_attr, completed_lineup_dict)
            setattr(match, tactic_attr, club_tactic) # Используем тактику клуба или 'balanced'
            return True
        else:
            logger.error(f"Failed to generate lineup for {team.name} (ID: {team.id}). Cannot start match {match.id}.")
            return False # Не удалось создать состав

# Функции для стамины/морали (оставляем заглушками)
def process_injury(match): logger.warning(f"Injury processing not implemented for match {match.id}")
def decrease_stamina(team, player, val): pass
def increase_stamina(team, player, val): pass
def decrease_morale(team, player, val): pass
def increase_morale(team, player, val): pass


# --- ОСНОВНАЯ ФУНКЦИЯ СИМУЛЯЦИИ МИНУТЫ ---
def simulate_one_minute(match: Match) -> Match | None:
    """
    Симулирует одну минуту матча, создавая события и обновляя состояние.
    Включает специальную логику для вратаря, начинающего с мячом.
    Возвращает обновленный объект match или None в случае критической ошибки.
    Предполагается, что match.save() будет вызван ВНЕ этой функции.
    """
    # Вероятности
    PASS_SUCCESS_PROB = 0.65 # Немного увеличим шанс паса
    SHOT_SUCCESS_PROB = 0.18 # Немного увеличим шанс гола
    BOUNCE_PROB = 0.60 # Шанс, что мяч отскочит к атаковавшей команде
    FOUL_PROB = 0.12 # Уменьшим шанс фола
    INJURY_PROB = 0.05 # Значительно уменьшим шанс травмы после фола

    # Новые вероятности для сценария с вратарем
    GK_PASS_SUCCESS_PROB = 0.10
    GK_INTERCEPTION_SHOT_SUCCESS_PROB = 0.90

    # Карта переходов по зонам
    transition_map = {"GK": "DEF", "DEF": "DM", "DM": "MID", "MID":"AM", "AM": "FWD"} # Добавили MID

    try:
        # Проверки статуса и времени матча
        if match.status != 'in_progress':
            logger.debug(f"simulate_one_minute: match {match.id} status is '{match.status}', skipping.")
            return match
        if match.current_minute >= 90:
            if match.status != 'finished':
                 logger.info(f"Match {match.id} reached minute 90 and is now finished.")
                 match.status = 'finished'
                 # Отправляем финальное обновление здесь, до возврата
                 possessing_team = match.home_team # Неважно кто владел последним
                 send_update(match, possessing_team)
            return match # Возвращаем с финальным статусом

        minute = match.current_minute + 1
        logger.debug(f"--- Simulating Minute {minute} for Match {match.id} ---")
        # decrease_stamina('all', 'all', 1) # Если нужно

        # --- Определяем владеющую команду и игрока ---
        current_player = match.current_player_with_ball
        possessing_team = None
        if current_player:
            if match.home_team.player_set.filter(id=current_player.id).exists():
                possessing_team = match.home_team
            elif match.away_team.player_set.filter(id=current_player.id).exists():
                possessing_team = match.away_team
            else:
                logger.warning(f"Player {current_player} not in home or away team for match {match.id}. Resetting possession.")
                current_player = None # Сбрасываем игрока

        if not current_player:
            # Начало матча / сброс / начало тайма(?) -> отдаем вратарю домашней команды
            possessing_team = match.home_team
            current_player = choose_player(possessing_team, "GK")
            if not current_player: # Крайний случай - у команды нет вратаря
                 logger.error(f"Match {match.id}: Home team {possessing_team.name} has no GK! Cannot proceed.")
                 match.status = 'error' # Или 'aborted'
                 return match # Выходим с ошибкой
            match.current_player_with_ball = current_player
            match.current_zone = "GK"
            match.st_posessions += 1
            logger.info(f"Match {match.id} minute {minute}: Possession reset to home GK {current_player}.")

        # Устанавливаем current_posses на основе владеющей команды
        match.current_posses = 1 if possessing_team.id == match.home_team.id else 2

        # --- Событие начала минуты ---
        start_event_desc = (f"Minute {minute}: Team '{possessing_team.name}' starts with the ball. "
                            f"{current_player.first_name} {current_player.last_name} "
                            f"in zone {match.current_zone}.")
        MatchEvent.objects.create(
            match=match, minute=minute, event_type='info',
            description=start_event_desc, player=current_player
        )
        logger.info(start_event_desc)
        send_update(match, possessing_team) # Отправляем начальное состояние минуты

        # --- Основная логика минуты ---
        minute_action_resolved = False

        # --- СПЕЦИАЛЬНАЯ ЛОГИКА: ЕСЛИ ВРАТАРЬ НАЧИНАЕТ С МЯЧОМ ---
        if match.current_zone == "GK":
            logger.info(f"Match {match.id} Min {minute}: Goalkeeper ({current_player.last_name}) initiates action.")
            gk_player = current_player
            opponent_team = get_opponent_team(match, possessing_team)

            if random.random() < GK_PASS_SUCCESS_PROB:
                # --- Пас вратаря успешен (90%) ---
                target_zone = "DEF"
                recipient = choose_player(possessing_team, target_zone, exclude_ids={gk_player.id})
                if recipient:
                    match.st_passes += 1
                    pass_desc = (f"GK {gk_player.last_name} passes successfully "
                                 f"to Defender {recipient.last_name}.")
                    MatchEvent.objects.create(
                        match=match, minute=minute, event_type='pass',
                        player=gk_player, related_player=recipient, description=pass_desc
                    )
                    logger.info(pass_desc)
                    match.current_player_with_ball = recipient
                    match.current_zone = target_zone
                    send_update(match, possessing_team)
                    minute_action_resolved = True # Действие выполнено
                else:
                    logger.warning(f"Match {match.id} Min {minute}: GK pass ok, but no defender found!")
                    # Отдаем мяч случайному полевому игроку своей команды
                    any_player = choose_player(possessing_team, "ANY", exclude_ids={gk_player.id})
                    if any_player:
                         match.current_player_with_ball = any_player
                         match.current_zone = "DEF" # Предполагаем, что мяч дошел до защиты
                         logger.info(f"Ball goes to random player {any_player.last_name}")
                         send_update(match, possessing_team)
                         minute_action_resolved = True
                    else:
                         logger.error(f"Match {match.id} Min {minute}: No players found for team {possessing_team.name}!")
                         minute_action_resolved = False # Переходим к осн. циклу (маловероятно)
            else:
                # --- Пас вратаря перехвачен (10%) ---
                interceptor = choose_player(opponent_team, "FWD") # Ищем ФОРВАРДА соперника
                if interceptor:
                    intercept_desc = (f"INTERCEPTION! GK {gk_player.last_name}'s pass intercepted "
                                      f"by Forward {interceptor.last_name} ({opponent_team.name})!")
                    MatchEvent.objects.create(
                        match=match, minute=minute, event_type='interception',
                        player=interceptor, related_player=gk_player, description=intercept_desc
                    )
                    logger.info(intercept_desc)

                    # Смена владения
                    match.current_player_with_ball = interceptor
                    possessing_team = opponent_team # Меняем команду!
                    match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                    # Зону не меняем, удар будет "из глубины"
                    send_update(match, possessing_team) # Обновляем сразу после перехвата

                    # --- Немедленный удар по воротам ---
                    logger.info(f"Match {match.id} Min {minute}: {interceptor.last_name} takes an immediate shot after interception!")
                    match.st_shoots += 1
                    shooter = interceptor

                    if random.random() < GK_INTERCEPTION_SHOT_SUCCESS_PROB: # ГОЛ (90%)
                        if possessing_team.id == match.home_team.id: match.home_score += 1
                        else: match.away_score += 1
                        goal_desc = (f"GOAL!!! After interception! {shooter.first_name} {shooter.last_name} "
                                     f"({possessing_team.name}) scores! Score: {match.home_score}-{match.away_score}")
                        MatchEvent.objects.create(match=match, minute=minute, event_type='goal', player=shooter, description=goal_desc)
                        logger.info(goal_desc)
                    else: # Промах (10%)
                        miss_desc = (f"Missed! {shooter.first_name} {shooter.last_name} fails to score after the interception.")
                        MatchEvent.objects.create(match=match, minute=minute, event_type='shot_miss', player=shooter, description=miss_desc)
                        logger.info(miss_desc)

                    # --- Сброс мяча после удара (гол или промах) ---
                    # Мяч вводит вратарь команды, ПРОПУСТИВШЕЙ гол, или команды, чей игрок бил (если промах)
                    if MatchEvent.objects.filter(match=match, minute=minute, event_type='goal').exists():
                         # После гола мяч у команды, пропустившей гол
                         reset_team = get_opponent_team(match, possessing_team)
                    else:
                         # После промаха мяч у вратаря защищавшейся команды
                         reset_team = get_opponent_team(match, possessing_team)
                         # Альтернатива: мяч у команды, которая била (если BOUNCE_PROB выше)
                         # if random.random() < BOUNCE_PROB: reset_team = possessing_team
                         # else: reset_team = get_opponent_team(match, possessing_team)


                    new_owner = choose_player(reset_team, "GK")
                    if new_owner:
                        logger.info(f"Match {match.id} Min {minute}: Ball resets to GK {new_owner.last_name} ({reset_team.name}).")
                        match.current_player_with_ball = new_owner
                        match.current_zone = "GK"
                        possessing_team = reset_team # Обновляем владеющую команду!
                        match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                    else:
                         logger.error(f"Match {match.id} Min {minute}: Could not find GK for {reset_team.name} after interception/shot. Resetting to home GK.")
                         match.current_player_with_ball = choose_player(match.home_team, "GK")
                         match.current_zone = "GK"
                         possessing_team = match.home_team
                         match.current_posses = 1

                    send_update(match, possessing_team) # Обновляем после удара и сброса
                    minute_action_resolved = True # Действие (перехват->удар) выполнено

                else: # Не нашли форварда для перехвата
                    logger.warning(f"Match {match.id} Min {minute}: GK pass intercepted, but no opponent FWD found. Ball out?")
                    # Можно сделать потерю мяча и отдать ГК соперника или оставить как есть
                    # Пока оставляем resolved=False, чтобы сработал основной цикл
                    minute_action_resolved = False

        # --- ОБЩИЙ ЦИКЛ СОБЫТИЙ МИНУТЫ (если действие вратаря не произошло или не завершило минуту) ---
        if not minute_action_resolved:
            subevents = 3 # Количество "попыток" действия в минуту
            for i in range(subevents):
                 if match.status != 'in_progress': break # Проверка статуса

                 current_player = match.current_player_with_ball
                 if not current_player: # Доп. проверка
                      logger.error(f"Match {match.id} Min {minute}: Lost player with ball! Resetting possession.")
                      match.current_player_with_ball = choose_player(match.home_team, "GK")
                      match.current_zone = "GK"
                      possessing_team = match.home_team
                      match.current_posses = 1
                      send_update(match, possessing_team)
                      break # Выходим из цикла subevents

                 logger.debug(f"Sub-event {i+1}: Player {current_player.last_name}, Zone {match.current_zone}")

                 # --- Шанс фола ---
                 if random.random() < FOUL_PROB:
                     match.st_fouls += 1
                     opponent_team = get_opponent_team(match, possessing_team)
                     fouler = choose_player(opponent_team, "ANY") # Фолит любой соперник
                     fouled = current_player
                     if fouler and fouled:
                          foul_desc = f"Foul! {fouler.last_name} ({opponent_team.name}) fouls {fouled.last_name} in zone {match.current_zone}."
                          MatchEvent.objects.create(match=match, minute=minute, event_type='foul', player=fouler, related_player=fouled, description=foul_desc)
                          logger.info(foul_desc)
                          # Обработка фола (пока только лог)
                          if random.random() < INJURY_PROB:
                              match.st_injury += 1
                              injury_desc = f"Injury concern for {fouled.last_name} after the foul!"
                              MatchEvent.objects.create(match=match, minute=minute, event_type='injury_concern', player=fouled, description=injury_desc)
                              logger.warning(injury_desc)
                          send_update(match, possessing_team)
                          # Фол может прервать атаку, но пока не меняем владение/не выходим из цикла

                 # --- Основное действие: Пас или Удар ---
                 if match.current_zone != "FWD":
                     # --- Попытка паса ---
                     target_zone = transition_map.get(match.current_zone, match.current_zone)
                     match.st_posessions += 1

                     if random.random() < PASS_SUCCESS_PROB: # Успешный пас
                         recipient = choose_player(possessing_team, target_zone, exclude_ids={current_player.id})
                         if recipient:
                             match.st_passes += 1
                             pass_desc = (f"Pass: {current_player.last_name} -> {recipient.last_name} "
                                          f"(Zone: {match.current_zone} -> {target_zone})")
                             MatchEvent.objects.create(
                                 match=match, minute=minute, event_type='pass',
                                 player=current_player, related_player=recipient, description=pass_desc
                             )
                             logger.info(pass_desc)
                             match.current_player_with_ball = recipient
                             match.current_zone = target_zone
                             send_update(match, possessing_team)
                         else:
                             logger.warning(f"Match {match.id} Min {minute}: Pass OK, but no player in zone {target_zone}.")
                             # Потеря мяча? Пока просто пропускаем ход.
                     else: # Неудачный пас (перехват)
                         opponent_team = get_opponent_team(match, possessing_team)
                         interceptor = choose_player(opponent_team, match.current_zone) # Перехват в текущей зоне
                         if interceptor:
                             intercept_desc = (f"INTERCEPTION! {interceptor.last_name} ({opponent_team.name}) "
                                               f"intercepts pass from {current_player.last_name} in {match.current_zone} zone.")
                             MatchEvent.objects.create(
                                 match=match, minute=minute, event_type='interception',
                                 player=interceptor, related_player=current_player, description=intercept_desc
                             )
                             logger.info(intercept_desc)
                             # Смена владения и сброс к вратарю новой команды
                             match.current_player_with_ball = choose_player(opponent_team, "GK")
                             if not match.current_player_with_ball: # Если нет ГК у соперника
                                  match.current_player_with_ball = interceptor # Отдаем перехватившему
                                  match.current_zone = "DEF" # или зона перехвата
                             else:
                                  match.current_zone = "GK"
                             possessing_team = opponent_team
                             match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                             send_update(match, possessing_team)
                             break # Прерываем цикл subevents - смена владения

                         else:
                             logger.warning(f"Match {match.id} Min {minute}: Pass failed, no interceptor found. Ball out?")
                             # Можно реализовать аут и смену владения
                             break # Пока просто прерываем атаку

                 else: # match.current_zone == "FWD"
                     # --- Попытка удара ---
                     match.st_shoots += 1
                     shooter = current_player

                     if random.random() < SHOT_SUCCESS_PROB: # ГОЛ!
                         if possessing_team.id == match.home_team.id: match.home_score += 1
                         else: match.away_score += 1
                         goal_desc = (f"GOAL!!! Scored by {shooter.first_name} {shooter.last_name} "
                                      f"({possessing_team.name})! Score: {match.home_score}-{match.away_score}")
                         MatchEvent.objects.create(match=match, minute=minute, event_type='goal', player=shooter, description=goal_desc)
                         logger.info(goal_desc)
                     else: # Промах
                         miss_desc = (f"Missed shot by {shooter.first_name} {shooter.last_name} ({possessing_team.name}).")
                         MatchEvent.objects.create(match=match, minute=minute, event_type='shot_miss', player=shooter, description=miss_desc)
                         logger.info(miss_desc)

                     # --- Сброс мяча после удара ---
                     reset_team = get_opponent_team(match, possessing_team) # Мяч у вратаря оборонявшихся
                     # Альтернатива с отскоком
                     # if random.random() < BOUNCE_PROB: reset_team = possessing_team
                     # else: reset_team = get_opponent_team(match, possessing_team)

                     new_owner = choose_player(reset_team, "GK")
                     if new_owner:
                         logger.info(f"Match {match.id} Min {minute}: Ball resets to GK {new_owner.last_name} ({reset_team.name}).")
                         match.current_player_with_ball = new_owner
                         match.current_zone = "GK"
                         possessing_team = reset_team
                         match.current_posses = 1 if possessing_team.id == match.home_team.id else 2
                     else:
                          logger.error(f"Match {match.id} Min {minute}: Could not find GK for {reset_team.name} after shot. Resetting to home GK.")
                          match.current_player_with_ball = choose_player(match.home_team, "GK")
                          match.current_zone = "GK"
                          possessing_team = match.home_team
                          match.current_posses = 1

                     send_update(match, possessing_team)
                     break # Прерываем цикл subevents после удара

        # --- Завершение минуты ---
        match.current_minute = minute
        if match.current_minute >= 90 and match.status != 'finished':
             match.status = 'finished'
             logger.info(f"Match {match.id} FINAL MINUTE {minute}. Finishing.")
             # Отправляем финальное обновление
             send_update(match, possessing_team if possessing_team else match.home_team)

        logger.debug(f"--- Minute {minute} simulation ended for Match {match.id} ---")

        # Запуск задачи для трансляции событий (если нужна)
        # from .tasks import broadcast_minute_events_in_chunks
        # broadcast_minute_events_in_chunks.delay(match.id, minute, duration=10) # Увеличили duration

        return match # Возвращаем обновленный объект

    except Exception as e:
        logger.exception(f"!!! CRITICAL Error in simulate_one_minute for match {match.id} at minute {match.current_minute + 1}: {e}")
        # Можно изменить статус матча на 'error' или вернуть None
        # match.status = 'error'
        return match # Возвращаем текущий объект, чтобы не прерывать цикл

# Остальные функции (simulate_match, passed_time и т.д.) остаются как были,
# но убедитесь, что simulate_match вызывает simulate_one_minute и СОХРАНЯЕТ результат:
#
# def simulate_match(match_id: int):
#     ...
#     for _ in range(90):
#         try:
#              match = Match.objects.get(id=match_id) # Получаем актуальное состояние
#              updated_match = simulate_one_minute(match)
#              if updated_match:
#                   updated_match.save() # Сохраняем после каждой минуты
#                   match = updated_match # Обновляем локальную переменную
#              else:
#                   logger.error(f"simulate_one_minute returned None for match {match_id}. Stopping simulation.")
#                   break # Прерываем цикл, если симуляция минуты не удалась
#              
#              # Проверяем статус после симуляции и сохранения
#              if match.status == 'paused':
#                  time.sleep(5) # Пауза
#                  match.status = 'in_progress'
#                  match.save() # Сохраняем возобновление
#                  # Отправляем обновление после возобновления
#                  possessing_team = match.home_team if match.current_posses == 1 else match.away_team
#                  send_update(match, possessing_team)
#
#              # passed_time(match, _) # Если нужна эта логика
#
#              if match.status == 'finished' or match.status == 'error':
#                   logger.info(f"Match {match.id} ended with status '{match.status}' during simulation loop.")
#                   break # Выходим из цикла, если матч завершен или ошибка
#
#         except Match.DoesNotExist:
#              logger.error(f"Match {match_id} not found during simulation loop.")
#              break
#         except Exception as loop_e:
#              logger.exception(f"Error in simulate_match loop for match {match_id}: {loop_e}")
#              # Можно добавить логику остановки или пропуска минуты
#
#     # Финальная проверка статуса после цикла (на случай, если 90 минут прошли без статуса finished)
#     try:
#          match = Match.objects.get(id=match_id)
#          if match.status != 'finished' and match.status != 'error':
#              logger.info(f"Match {match.id} reached end of loop without finishing. Setting status to finished.")
#              match.status = 'finished'
#              match.current_minute = 90
#              match.save()
#              possessing_team = match.home_team # Для финального апдейта
#              send_update(match, possessing_team)
#     except Match.DoesNotExist:
#          logger.error(f"Match {match_id} not found after simulation loop.")
#     except Exception as final_e:
#          logger.exception(f"Error during final status check for match {match_id}: {final_e}")
#
#     logger.info(f"Simulation finished for match {match_id}")