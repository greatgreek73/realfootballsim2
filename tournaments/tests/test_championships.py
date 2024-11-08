# tournaments/tests/test_championships.py
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django_countries import countries
from tournaments.models import Season, League, Championship, ChampionshipTeam
from tournaments.utils import generate_league_schedule, create_championship_matches, validate_championship_schedule
from clubs.models import Club

class ChampionshipSystemTests(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем сезон
        self.season = Season.objects.create(
            name="Сезон 1",
            number=1,  # Добавляем обязательное поле number
            start_date=datetime(2024, 3, 1).date(),
            end_date=datetime(2024, 3, 30).date(),
            is_active=True
        )

        # Создаем лигу
        self.league = League.objects.create(
            name="Test League",
            country='GB',  # Великобритания
            level=1,
            max_teams=16
        )

        # Создаем тестовые клубы
        self.clubs = []
        for i in range(16):
            club = Club.objects.create(
                name=f"Test Club {i+1}",
                country='GB',
                is_bot=True
            )
            self.clubs.append(club)

        # Создаем чемпионат
        self.championship = Championship.objects.create(
            season=self.season,
            league=self.league,
            status='pending',
            start_date=self.season.start_date,
            end_date=self.season.end_date
        )

        # Добавляем команды в чемпионат
        for club in self.clubs:
            ChampionshipTeam.objects.create(
                championship=self.championship,
                team=club
            )

    def test_schedule_generation_basic(self):
        """Тест базовой генерации расписания"""
        schedule = generate_league_schedule(self.championship)
        
        # Проверяем общее количество матчей
        # 16 команд, каждая играет с каждой дважды = 16 * 15 = 240 матчей
        self.assertEqual(len(schedule), 240, 
                        "Неверное общее количество матчей")
        
        # Проверяем количество туров
        rounds = {match[0] for match in schedule}
        self.assertEqual(len(rounds), 30, 
                        "Должно быть 30 туров")

    def test_home_away_balance(self):
        """Тест баланса домашних/выездных матчей"""
        schedule = generate_league_schedule(self.championship)
        
        # Подсчет домашних и выездных матчей для каждой команды
        home_games = {club: 0 for club in self.clubs}
        away_games = {club: 0 for club in self.clubs}
        
        for round_num, day, home, away in schedule:
            home_games[home] += 1
            away_games[away] += 1
        
        # Проверяем баланс для каждой команды
        for club in self.clubs:
            self.assertEqual(home_games[club], 15, 
                           f"Команда {club} имеет {home_games[club]} домашних матчей вместо 15")
            self.assertEqual(away_games[club], 15, 
                           f"Команда {club} имеет {away_games[club]} выездных матчей вместо 15")

    def test_consecutive_matches(self):
        """Тест на последовательные домашние/выездные матчи"""
        schedule = generate_league_schedule(self.championship)
        
        # Создаем словарь матчей для каждой команды
        team_schedules = {club: [] for club in self.clubs}
        for round_num, day, home, away in sorted(schedule):
            team_schedules[home].append(('home', round_num))
            team_schedules[away].append(('away', round_num))
        
        # Проверяем каждую команду
        for club, matches in team_schedules.items():
            matches.sort(key=lambda x: x[1])  # Сортируем по номеру тура
            
            consecutive_home = 0
            consecutive_away = 0
            max_consecutive_home = 0
            max_consecutive_away = 0
            
            for match_type, _ in matches:
                if match_type == 'home':
                    consecutive_home += 1
                    consecutive_away = 0
                    max_consecutive_home = max(max_consecutive_home, consecutive_home)
                else:
                    consecutive_away += 1
                    consecutive_home = 0
                    max_consecutive_away = max(max_consecutive_away, consecutive_away)
                
            self.assertLess(max_consecutive_home, 3,
                          f"Команда {club} имеет {max_consecutive_home} домашних матчей подряд")
            self.assertLess(max_consecutive_away, 3,
                          f"Команда {club} имеет {max_consecutive_away} выездных матчей подряд")

    def test_all_matches_in_round_same_time(self):
        """Тест, что все матчи тура проходят в одно время"""
        create_championship_matches(self.championship)
        
        matches = self.championship.championshipmatch_set.all()
        rounds = matches.values('round').distinct()
        
        for round_data in rounds:
            round_num = round_data['round']
            round_matches = matches.filter(round=round_num)
            
            # Собираем все времена матчей в этом туре
            match_times = set()
            for match in round_matches:
                match_times.add(match.match.date)
            
            # Проверяем, что все матчи в одно время
            self.assertEqual(len(match_times), 1,
                           f"Матчи тура {round_num} проходят в разное время")

    def test_regular_season_schedule(self):
        """Тест расписания для обычного сезона"""
        create_championship_matches(self.championship)
        
        matches = self.championship.championshipmatch_set.all()
        # Проверяем, что каждый день проводится только один тур
        match_dates = matches.values_list('match__date__date', flat=True).distinct()
        self.assertEqual(len(match_dates), 30, 
                        "Должно быть 30 игровых дней для 30 туров")

        # Проверяем время начала матчей
        for match_date in match_dates:
            date_matches = matches.filter(match__date__date=match_date)
            match_times = set(date_matches.values_list('match__date__hour', flat=True))
            self.assertEqual(len(match_times), 1,
                           f"В обычный день {match_date} должен быть только один тур")
            self.assertEqual(list(match_times)[0], 18,
                           "Все матчи должны начинаться в 18:00")

   # Изменения в тестовом файле
def test_february_schedule(self):
    """Тест для февральского расписания"""
    # Создаем февральский сезон
    february_season = Season.objects.create(
        name="Сезон 2",
        number=2,
        start_date=datetime(2024, 2, 1).date(),
        end_date=datetime(2024, 2, 28).date(),
        is_active=False
    )
    
    february_championship = Championship.objects.create(
        season=february_season,
        league=self.league,
        status='pending',
        start_date=february_season.start_date,
        end_date=february_season.end_date
    )
    
    # Добавляем те же команды
    for club in self.clubs:
        ChampionshipTeam.objects.create(
            championship=february_championship,
            team=club
        )
    
    create_championship_matches(february_championship)
    matches = february_championship.championshipmatch_set.all()
    
    # Проверяем, что в обычные дни все матчи тура в 18:00
    for day in range(1, 29):
        if day not in [15, 16]:  # Не двойные туры
            date_matches = matches.filter(
                match__date__date=datetime(2024, 2, day).date()
            )
            if date_matches.exists():
                # Проверяем только время начала
                match_hours = set(date_matches.values_list(
                    'match__date__hour', flat=True
                ))
                self.assertEqual(match_hours, {18},
                               f"Матчи в день {day} февраля должны начинаться в 18:00")
    
    # Проверяем двойные туры (15 и 16 февраля)
    for day in [15, 16]:
        date_matches = matches.filter(
            match__date__date=datetime(2024, 2, day).date()
        )
        match_hours = set(date_matches.values_list(
            'match__date__hour', flat=True
        ))
        self.assertEqual(match_hours, {18, 20},
                       f"В двойной игровой день {day} февраля матчи должны начинаться в 18:00 и 20:00")