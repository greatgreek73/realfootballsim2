from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from tournaments.models import Season, League, Championship, ChampionshipTeam
from clubs.models import Club
from datetime import timedelta

class SeasonTransitionTests(TestCase):
    def setUp(self):
        # Создаем сезон
        self.season = Season.objects.create(
            number=1,
            name="Test Season",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True
        )

        # Создаем две лиги для одной страны
        self.league_div1 = League.objects.create(
            name="Test League D1",
            country='GB',
            level=1,
            max_teams=16
        )
        
        self.league_div2 = League.objects.create(
            name="Test League D2",
            country='GB',
            level=2,
            max_teams=16
        )

        # Создаем команды для обоих дивизионов
        self.div1_teams = []
        self.div2_teams = []

        for i in range(16):
            # Команды первого дивизиона
            team = Club.objects.create(
                name=f"D1 Team {i+1}",
                country='GB',
                league=self.league_div1,
                is_bot=True
            )
            self.div1_teams.append(team)

            # Команды второго дивизиона
            team = Club.objects.create(
                name=f"D2 Team {i+1}",
                country='GB',
                league=self.league_div2,
                is_bot=True
            )
            self.div2_teams.append(team)

        # Создаем чемпионаты
        self.championship_div1 = Championship.objects.create(
            season=self.season,
            league=self.league_div1,
            status='in_progress',
            start_date=self.season.start_date,
            end_date=self.season.end_date
        )

        self.championship_div2 = Championship.objects.create(
            season=self.season,
            league=self.league_div2,
            status='in_progress',
            start_date=self.season.start_date,
            end_date=self.season.end_date
        )

        # Добавляем команды в чемпионаты
        for team in self.div1_teams:
            self.championship_div1.teams.add(team)
            ChampionshipTeam.objects.create(
                championship=self.championship_div1,
                team=team
            )

        for team in self.div2_teams:
            self.championship_div2.teams.add(team)
            ChampionshipTeam.objects.create(
                championship=self.championship_div2,
                team=team
            )

    def test_season_transitions(self):
        """Тестируем процесс переходов между дивизионами"""
        
        # Устанавливаем результаты для команд первого дивизиона
        div1_teams = ChampionshipTeam.objects.filter(championship=self.championship_div1)
        for i, team_stats in enumerate(div1_teams):
            team_stats.points = 80 - i * 5  # От 80 до 5 очков
            team_stats.matches_played = 30
            team_stats.save()

        # Устанавливаем результаты для команд второго дивизиона
        div2_teams = ChampionshipTeam.objects.filter(championship=self.championship_div2)
        for i, team_stats in enumerate(div2_teams):
            team_stats.points = 80 - i * 5  # От 80 до 5 очков
            team_stats.matches_played = 30
            team_stats.save()

        # Завершаем сезон и запускаем переходы
        self.season.end_date = timezone.now().date() - timedelta(days=1)
        self.season.save()
        
        call_command('handle_season_transitions')

        # Проверяем что две худшие команды из D1 перешли в D2
        relegated_teams = div1_teams.order_by('points')[:2]
        for team_stats in relegated_teams:
            team = Club.objects.get(id=team_stats.team.id)
            self.assertEqual(
                team.league, 
                self.league_div2,
                f"Team {team.name} should be relegated to D2"
            )

        # Проверяем что две лучшие команды из D2 перешли в D1
        promoted_teams = div2_teams.order_by('-points')[:2]
        for team_stats in promoted_teams:
            team = Club.objects.get(id=team_stats.team.id)
            self.assertEqual(
                team.league, 
                self.league_div1,
                f"Team {team.name} should be promoted to D1"
            )

    def test_new_season_creation(self):
        """Тестируем создание нового сезона после переходов"""
        
        # Завершаем текущий сезон
        self.season.end_date = timezone.now().date() - timedelta(days=1)
        self.season.save()
        
        # Запускаем процесс создания нового сезона
        call_command('create_new_season')

        # Проверяем что новый сезон создан
        new_season = Season.objects.get(number=self.season.number + 1)
        self.assertTrue(new_season.is_active)
        
        # Проверяем что созданы чемпионаты
        new_championships = Championship.objects.filter(season=new_season)
        self.assertEqual(new_championships.count(), 2)
        
        # Проверяем корректность распределения команд
        for championship in new_championships:
            self.assertEqual(
                championship.teams.count(), 
                16,
                f"Championship {championship} should have 16 teams"
            )

    def test_full_transition_process(self):
        """Тестируем полный процесс перехода к новому сезону"""
        
        # Завершаем текущий сезон
        self.season.end_date = timezone.now().date() - timedelta(days=1)
        self.season.save()

        # Запускаем проверку окончания сезона
        call_command('check_season_end')

        # Проверяем что старый сезон неактивен
        old_season = Season.objects.get(id=self.season.id)
        self.assertFalse(old_season.is_active)

        # Проверяем что создан новый сезон
        new_season = Season.objects.exclude(id=self.season.id).get()
        self.assertTrue(new_season.is_active)

        # Проверяем корректность переходов
        # В первом дивизионе должны остаться 14 старых команд + 2 новых
        div1_championship = Championship.objects.get(
            season=new_season,
            league=self.league_div1
        )
        self.assertEqual(div1_championship.teams.count(), 16)

        # Во втором дивизионе должны остаться 14 старых команд + 2 новых
        div2_championship = Championship.objects.get(
            season=new_season,
            league=self.league_div2
        )
        self.assertEqual(div2_championship.teams.count(), 16)