from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models, transaction
from .models import Championship, ChampionshipMatch, Season
from matches.models import Match
import logging

logger = logging.getLogger(__name__)

def check_consecutive_matches(schedule: List[Tuple], team, is_home: bool) -> int:
    """
    Проверяет количество последовательных домашних или гостевых матчей для команды.
    """
    max_consecutive = 0
    current_consecutive = 0

    for match in schedule:
        if is_home:
            is_match = match[2] == team  # домашняя команда
        else:
            is_match = match[3] == team  # гостевая команда

        if is_match:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0

    return max_consecutive

def get_team_matches(schedule: List[Tuple], team) -> List[Tuple[int, bool]]:
    """
    Возвращает список матчей команды с информацией о домашних/гостевых играх.
    """
    team_matches = []
    for round_num, day, home, away in schedule:
        if home == team:
            team_matches.append((round_num, True))
        elif away == team:
            team_matches.append((round_num, False))
    return sorted(team_matches)

def validate_schedule_balance(schedule: List[Tuple], teams: List) -> Dict:
    """
    Проверяет баланс домашних и гостевых матчей для каждой команды.
    """
    balance = {team: {'home': 0, 'away': 0} for team in teams}

    for _, _, home, away in schedule:
        balance[home]['home'] += 1
        balance[away]['away'] += 1

    return balance

def generate_league_schedule(championship: Championship) -> List[Tuple]:
    """
    Генерирует сбалансированное расписание матчей по принципу кругового турнира для чемпионата,
    учитывая ограничение не более двух подряд домашних или выездных матчей.
    """
    teams = list(championship.teams.all())
    if len(teams) != 16:
        raise ValueError(f"Требуется ровно 16 команд, сейчас: {len(teams)}")
    
    n = len(teams)
    rounds = n - 1
    schedule = []
    
    # Создаем массив с номерами команд
    team_numbers = list(range(n))
    
    # Генерируем матрицу встреч
    matches = []
    for round_num in range(rounds):
        round_matches = []
        for i in range(n // 2):
            home = team_numbers[i]
            away = team_numbers[n - i - 1]
            # Чередуем домашние и выездные матчи по турам и парам
            if (i + round_num) % 2 == 0:
                round_matches.append((home, away))
            else:
                round_matches.append((away, home))
        matches.append(round_matches)
        # Ротация команд
        team_numbers = [team_numbers[0]] + team_numbers[-1:] + team_numbers[1:-1]
    
    # Создаем расписание для первого и второго кругов
    for half in range(2):
        for round_num in range(rounds):
            actual_round = round_num + 1 + half * rounds
            round_matches = matches[round_num]
            for match_num, (home_idx, away_idx) in enumerate(round_matches):
                if half == 1:
                    # Во втором круге меняем хозяев и гостей
                    home_idx, away_idx = away_idx, home_idx
                home_team = teams[home_idx]
                away_team = teams[away_idx]
                schedule.append((actual_round, match_num + 1, home_team, away_team))
    
    return schedule

def create_championship_matches(championship: Championship) -> None:
    """
    Создает матчи чемпионата на основе сгенерированного расписания.
    """
    with transaction.atomic():
        ChampionshipMatch.objects.filter(championship=championship).delete()

        schedule = generate_league_schedule(championship)
        is_february = championship.season.is_february

        logger.info(f"Начинаем генерацию для {championship} (Дивизион {championship.league.level})")
        logger.info(f"Всего матчей для генерации: {len(schedule)}")

        matches_by_round = {}
        for round_num, day, home_team, away_team in schedule:
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append((day, home_team, away_team))

        logger.info(f"Количество туров: {len(matches_by_round)}")

        current_date = championship.start_date

        # Для каждого тура создаем матчи
        for round_num in sorted(matches_by_round.keys()):
            logger.info(f"Генерация тура {round_num} на дату {current_date}")

            # Определяем время начала матчей
            # Матчи первого дивизиона в 18:00, второго в 16:00
            match_time = championship.match_time
            if championship.league.level == 2:
                # Для второго дивизиона сдвигаем время на 2 часа раньше
                match_time = (
                    datetime.combine(datetime.min, match_time) - 
                    timedelta(hours=2)
                ).time()

            match_datetime = timezone.make_aware(
                datetime.combine(current_date, match_time)
            )

            for day, home_team, away_team in matches_by_round[round_num]:
                match = Match.objects.create(
                    home_team=home_team,
                    away_team=away_team,
                    date=match_datetime,
                    status='scheduled'
                )

                ChampionshipMatch.objects.create(
                    championship=championship,
                    match=match,
                    round=round_num,
                    match_day=current_date.day
                )

            current_date += timedelta(days=1)

        logger.info("Генерация расписания завершена")

def validate_championship_schedule(championship: Championship) -> bool:
    """
    Проверяет корректность расписания чемпионата.
    """
    print("\nНачало валидации расписания для", championship)
    matches = ChampionshipMatch.objects.filter(championship=championship).select_related('match')
    teams = list(championship.teams.all())

    print("\n1. Проверка общего количества матчей:")
    expected_matches = len(teams) * (len(teams) - 1)
    actual_matches = matches.count()
    print(f"Ожидается матчей: {expected_matches}")
    print(f"Фактически матчей: {actual_matches}")
    if actual_matches != expected_matches:
        print(f"ОШИБКА: Неверное количество матчей: {actual_matches} вместо {expected_matches}")
        return False

    print("\n2. Проверка баланса матчей:")
    team_matches = {team: {'home': 0, 'away': 0} for team in teams}
    for match in matches:
        team_matches[match.match.home_team]['home'] += 1
        team_matches[match.match.away_team]['away'] += 1

    for team, stats in team_matches.items():
        print(f"\nКоманда {team}:")
        print(f"Домашних матчей: {stats['home']}")
        print(f"Выездных матчей: {stats['away']}")
        print(f"Ожидается: по {len(teams) - 1} матчей каждого типа")
        if stats['home'] != (len(teams) - 1) or stats['away'] != (len(teams) - 1):
            print(f"ОШИБКА: Неверный баланс матчей для {team}")
            return False

    print("\n3. Проверка последовательности матчей:")
    for team in teams:
        print(f"\nПроверка последовательности для {team}:")
        team_schedule = list(matches.filter(
            models.Q(match__home_team=team) | models.Q(match__away_team=team)
        ).order_by('round'))

        home_streak = 0
        away_streak = 0
        max_home_streak = 0
        max_away_streak = 0

        print("Последовательность матчей:")
        for match in team_schedule:
            match_type = 'дома' if match.match.home_team == team else 'в гостях'
            print(f"Тур {match.round}: {match_type}")
            if match.match.home_team == team:
                home_streak += 1
                away_streak = 0
                max_home_streak = max(max_home_streak, home_streak)
            else:
                away_streak += 1
                home_streak = 0
                max_away_streak = max(max_away_streak, away_streak)

        if max_home_streak > 2:
            print(f"ОШИБКА: Команда {team} имеет {max_home_streak} домашних матчей подряд")
            return False
        if max_away_streak > 2:
            print(f"ОШИБКА: Команда {team} имеет {max_away_streak} выездных матчей подряд")
            return False

    print("\n4. Проверка дат и времени матчей:")
    used_dates_times = set()
    is_february = championship.season.is_february
    double_matchdays = championship.season.get_double_matchday_dates()

    for match in matches:
        match_datetime = match.match.date
        match_date = match_datetime.date()
        match_time = match_datetime.time()

        # Проверяем, что время матча либо стандартное, либо на 2 часа позже
        base_time = championship.match_time
        allowed_times = {
            base_time,
            (datetime.combine(datetime.min, base_time) + timedelta(hours=2)).time()
        }

        if match_time not in allowed_times:
            print(f"ОШИБКА: Неверное время начала матча: {match_time}")
            return False

        if match_datetime in used_dates_times:
            if not (is_february and match_date in double_matchdays):
                print(f"ОШИБКА: Обнаружены матчи в одно и то же время: {match_datetime}")
                return False
        used_dates_times.add(match_datetime)

    print("\nВсе проверки пройдены успешно!")
    return True
