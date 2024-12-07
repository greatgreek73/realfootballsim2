from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField
from clubs.models import Club
from matches.models import Match
from datetime import datetime, timedelta, time
import pytz
import calendar
from .date_utils import get_next_season_dates  # Изменен импорт

class Season(models.Model):
    """Model for representing a game season"""
    number = models.PositiveIntegerField(
        unique=True, 
        help_text="Порядковый номер сезона"
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Сезон {self.number} ({self.start_date.strftime('%B %Y')})"

    def clean(self):
        """Проверка корректности дат сезона"""
        if not self.start_date:
            return

        if self.start_date.day != 1:
            raise ValidationError({
                'start_date': 'Дата начала сезона должна быть первым числом месяца'
            })

        # Определяем последний день месяца используя calendar.monthrange
        _, last_day = calendar.monthrange(self.start_date.year, self.start_date.month)
        expected_end_date = self.start_date.replace(day=last_day)
        
        if self.end_date != expected_end_date:
            raise ValidationError({
                'end_date': f'Дата окончания сезона должна быть {last_day}-м числом месяца'
            })

    @property
    def is_february(self) -> bool:
        """Проверяет, является ли текущий сезон февральским"""
        return self.start_date.month == 2

    @property
    def needs_double_matchday(self) -> bool:
        """Определяет, нужны ли двойные туры в этом сезоне"""
        return self.is_february and calendar.monthrange(self.start_date.year, 2)[1] == 28

    def get_double_matchday_dates(self) -> list:
        """Возвращает даты для двойных туров"""
        if not self.needs_double_matchday:
            return []
        
        dates = [self.start_date.replace(day=15)]
        if self.end_date.day == 28:  # Для невисокосного февраля
            dates.append(self.start_date.replace(day=16))
        return dates

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"Сезон {self.number}"
        super().save(*args, **kwargs)

    @classmethod
    def create_next_season(cls) -> 'Season':
        """Создает новый сезон"""
        last_season = cls.objects.order_by('-number').first()
        new_season_number = 1 if not last_season else last_season.number + 1

        # Получаем даты следующего сезона
        start_date, end_date = get_next_season_dates()

        season = cls(
            number=new_season_number,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        season.full_clean()
        season.save()
        return season

class League(models.Model):
    """Model for representing a league/division"""
    name = models.CharField(max_length=100)
    country = CountryField()
    level = models.PositiveIntegerField()  # 1 for top division, 2 for second, etc.
    max_teams = models.PositiveIntegerField(default=16)
    foreign_players_limit = models.PositiveIntegerField(
        default=5, 
        help_text="Maximum number of foreign players allowed in match squad"
    )

    class Meta:
        unique_together = ['country', 'level']
        ordering = ['country', 'level']

    def __str__(self):
        return f"{self.name} ({self.country})"

    def clean(self):
        if self.max_teams != 16:
            raise ValidationError({
                'max_teams': 'Количество команд в лиге должно быть равно 16'
            })

class Championship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')
    ]

    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Club, through='ChampionshipTeam')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    match_time = models.TimeField(
        default=time(18, 0),
        help_text="Match start time (UTC)"
    )

    class Meta:
        unique_together = ['season', 'league']

    def __str__(self):
        return f"{self.league.name} - {self.season.name}"

    def get_local_match_time(self, user_timezone=None):
        if not user_timezone:
            user_timezone = timezone.get_current_timezone()
        utc_time = datetime.combine(datetime.today(), self.match_time)
        utc_time = pytz.utc.localize(utc_time)
        return utc_time.astimezone(user_timezone).time()

    def clean(self):
        if self.teams.count() != 16:
            raise ValidationError('Количество команд в чемпионате должно быть равно 16')

    def can_participate_in_transitions(self) -> bool:
        """Проверяет, может ли чемпионат участвовать в переходах"""
        if not self.is_completed:
            return False
            
        valid, error = self.validate_status()
        if not valid:
            return False
            
        if self.league.level not in [1, 2]:
            return False
            
        return True

    def get_teams_for_relegation(self) -> list:
        """Возвращает две команды для понижения в дивизионе"""
        if self.league.level != 1:
            raise ValidationError("Relegation is only possible from the first division")

        if not self.can_participate_in_transitions():
            raise ValidationError("Championship cannot participate in transitions yet")
            
        return (
            self.championshipteam_set
            .annotate(
                goals_diff=models.F('goals_for') - models.F('goals_against')
            )
            .select_related('team')
            .order_by(
                'points',
                'goals_diff',
                'goals_for'
            )[:2]
        )

    def get_teams_for_promotion(self) -> list:
        """Возвращает две команды для повышения в дивизионе"""
        if self.league.level != 2:
            raise ValidationError("Promotion is only possible from the second division")

        if not self.can_participate_in_transitions():
            raise ValidationError("Championship cannot participate in transitions yet")
            
        return (
            self.championshipteam_set
            .annotate(
                goals_diff=models.F('goals_for') - models.F('goals_against')
            )
            .select_related('team')
            .order_by(
                '-points',
                '-goals_diff',
                '-goals_for'
            )[:2]
        )

    @property
    def is_completed(self) -> bool:
        """Проверяет, завершены ли все матчи чемпионата"""
        return not self.championshipmatch_set.filter(
            ~models.Q(match__status='finished')
        ).exists()

    def get_standings(self) -> list:
        """Возвращает отсортированную таблицу результатов"""
        return (
            self.championshipteam_set
            .annotate(
                goals_diff=models.F('goals_for') - models.F('goals_against')
            )
            .select_related('team')
            .order_by(
                '-points',
                '-goals_diff',
                '-goals_for'
            )
        )

    def validate_status(self) -> tuple:
        """
        Проверяет текущий статус чемпионата
        Возвращает (is_valid, error_message)
        """
        if self.teams.count() != 16:
            return False, "Неверное количество команд в чемпионате"
                
        matches_count = self.championshipmatch_set.count()
        expected_matches = 16 * 15  # Каждая команда играет с каждой другой дважды
        if matches_count != expected_matches:
            return False, f"Неверное количество матчей: {matches_count} вместо {expected_matches}"
                
        return True, None

class ChampionshipTeam(models.Model):
    """Model for storing team statistics in championship"""
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    team = models.ForeignKey(Club, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    matches_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    goals_for = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['championship', 'team']
        ordering = ['-points', '-goals_for']

    def __str__(self):
        return f"{self.team.name} - {self.championship}"

    @property
    def goals_difference(self):
        """Calculate goals difference"""
        return self.goals_for - self.goals_against

    @property
    def points_per_game(self):
        """Calculate average points per game"""
        if self.matches_played > 0:
            return round(self.points / self.matches_played, 2)
        return 0

    @property
    def position(self) -> int:
        """Возвращает текущую позицию команды в таблице"""
        return (
            self.championship.championshipteam_set
            .annotate(
                goals_diff=models.F('goals_for') - models.F('goals_against')
            )
            .filter(
                models.Q(points__gt=self.points) |
                (models.Q(points=self.points) & models.Q(goals_diff__gt=self.goals_difference)) |
                (models.Q(points=self.points) & 
                 models.Q(goals_diff=self.goals_difference) & 
                 models.Q(goals_for__gt=self.goals_for))
            )
            .count() + 1
        )

    @property
    def is_relegation_zone(self) -> bool:
        """Проверяет, находится ли команда в зоне вылета"""
        return self.position >= 15

    @property
    def is_promotion_zone(self) -> bool:
        """Проверяет, находится ли команда в зоне повышения"""
        return self.position <= 2

class ChampionshipMatch(models.Model):
    """Model for linking matches to championship"""
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    round = models.PositiveIntegerField()
    match_day = models.PositiveIntegerField()
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['round', 'match_day']

    def __str__(self):
        return f"Round {self.round}: {self.match}"

    @property
    def match_datetime(self):
        """Возвращает дату и время матча"""
        return datetime.combine(
            self.championship.start_date + timedelta(days=self.match_day - 1),
            datetime.min.time().replace(hour=18)
        )