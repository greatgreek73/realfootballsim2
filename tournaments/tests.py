from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django_countries import countries
from .models import Season, League, Championship, ChampionshipTeam
from .utils import generate_league_schedule, create_championship_matches, validate_championship_schedule
from clubs.models import Club

class ChampionshipSystemTests(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем сезон
        self.season = Season.objects.create(
            number=1,
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
        self.assertEqual(len(schedule), 240)  # 16 команд = 30 туров по 8 матчей

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
            
            for match_type, _ in matches:
                if match_type == 'home':
                    consecutive_home += 1
                    consecutive_away = 0
                else:
                    consecutive_away += 1
                    consecutive_home = 0
                
                self.assertLess(consecutive_home, 3,
                              f"Команда {club} имеет более 2 домашних матчей подряд")
                self.assertLess(consecutive_away, 3,
                              f"Команда {club} имеет более 2 выездных матчей подряд")

    def test_all_matches_in_one_day(self):
        """Тест, что все матчи тура проходят в один день"""
        create_championship_matches(self.championship)
        
        matches = self.championship.championshipmatch_set.all()
        rounds = matches.values('round').distinct()
        
        for round_data in rounds:
            round_num = round_data['round']
            round_matches = matches.filter(round=round_num)
            
            # Собираем все даты матчей в этом туре
            match_dates = set()
            for match in round_matches:
                match_dates.add(match.match.datetime.date())
            
            # Проверяем, что все матчи в один день
            self.assertEqual(len(match_dates), 1,
                           f"Матчи тура {round_num} проходят в разные дни: {match_dates}")

    def test_february_schedule(self):
        """Тест для февральского расписания"""
        # Создаем февральский сезон
        february_season = Season.objects.create(
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
        self.assertTrue(validate_championship_schedule(february_championship))

        # Проверяем наличие двойных туров 15 февраля
        double_matchday_matches = february_championship.championshipmatch_set.filter(
            match__date__date=datetime(2024, 2, 15).date()
        )
        self.assertEqual(double_matchday_matches.count(), 16,  # 8 матчей * 2 тура
                        "Неверное количество матчей в двойной игровой день")