from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField
from clubs.models import Club
from matches.models import Match
from datetime import datetime, timedelta

class Season(models.Model):
    """Model for representing a game season"""
    number = models.PositiveIntegerField(
        unique=True, 
        help_text="Порядковый номер сезона"
    )
    name = models.CharField(max_length=100)  # Оставляем для обратной совместимости
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

        # Проверяем, что начало сезона - первое число месяца
        if self.start_date.day != 1:
            raise ValidationError({
                'start_date': 'Дата начала сезона должна быть первым числом месяца'
            })

        # Проверяем корректность даты окончания
        if self.start_date.month == 2:  # Февраль
            last_day = 29 if self.start_date.year % 4 == 0 else 28
        else:
            last_day = 30  # Для всех остальных месяцев используем 30 дней
        
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
        return self.is_february

    def get_double_matchday_dates(self) -> list:
        """Возвращает даты для двойных туров"""
        if not self.is_february:
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

        today = timezone.now().date()
        if today.day == 1:
            start_date = today
        else:
            if today.month == 12:
                start_date = today.replace(year=today.year + 1, month=1, day=1)
            else:
                start_date = today.replace(month=today.month + 1, day=1)

        if start_date.month == 2:
            last_day = 29 if start_date.year % 4 == 0 else 28
        else:
            last_day = 30
        end_date = start_date.replace(day=last_day)

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
    max_teams = models.PositiveIntegerField(default=16)  # Изменено с 20 на 16
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
    """Model for representing a championship competition"""
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

    class Meta:
        unique_together = ['season', 'league']

    def __str__(self):
        return f"{self.league.name} - {self.season.name}"

    def clean(self):
        if self.teams.count() != 16:
            raise ValidationError('Количество команд в чемпионате должно быть равно 16')

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