from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models, transaction
from .models import Championship, ChampionshipMatch, Season
from matches.models import Match

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
    Генерирует сбалансированное расписание матчей по принципу кругового турнира.
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
            # Чередуем домашние и выездные матчи
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
        matches_by_round = {}
        
        # Группируем матчи по турам
        for round_num, day, home_team, away_team in schedule:
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append((day, home_team, away_team))
            
        current_date = championship.start_date

        # Создаем матчи
        for round_num in sorted(matches_by_round.keys()):
            match_time = championship.match_time
            if championship.league.level == 2:
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
                    datetime=match_datetime,  # Исправлено с date на datetime
                    status='scheduled'
                )

                ChampionshipMatch.objects.create(
                    championship=championship,
                    match=match,
                    round=round_num,
                    match_day=current_date.day
                )

            current_date += timedelta(days=1)

def validate_championship_schedule(championship: Championship) -> bool:
    """
    Проверяет корректность расписания чемпионата.
    """
    matches = ChampionshipMatch.objects.filter(championship=championship).select_related('match')
    teams = list(championship.teams.all())

    # Проверка количества матчей
    expected_matches = len(teams) * (len(teams) - 1)
    if matches.count() != expected_matches:
        return False

    # Проверка баланса матчей
    team_matches = {team: {'home': 0, 'away': 0} for team in teams}
    for match in matches:
        team_matches[match.match.home_team]['home'] += 1
        team_matches[match.match.away_team]['away'] += 1

    for team, stats in team_matches.items():
        if stats['home'] != (len(teams) - 1) or stats['away'] != (len(teams) - 1):
            return False

    # Проверка последовательности матчей
    for team in teams:
        team_schedule = list(matches.filter(
            models.Q(match__home_team=team) | models.Q(match__away_team=team)
        ).order_by('round'))

        home_streak = 0
        away_streak = 0
        max_home_streak = 0
        max_away_streak = 0

        for match in team_schedule:
            if match.match.home_team == team:
                home_streak += 1
                away_streak = 0
                max_home_streak = max(max_home_streak, home_streak)
            else:
                away_streak += 1
                home_streak = 0
                max_away_streak = max(max_away_streak, away_streak)

        if max_home_streak > 2 or max_away_streak > 2:
            return False

    return True