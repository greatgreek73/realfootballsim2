from django.db import models
from django_countries.fields import CountryField
from clubs.models import Club
from matches.models import Match

class Season(models.Model):
    """Model for representing a game season"""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class League(models.Model):
    """Model for representing a league/division"""
    name = models.CharField(max_length=100)
    country = CountryField()
    level = models.PositiveIntegerField()  # 1 for top division, 2 for second, etc.
    max_teams = models.PositiveIntegerField(default=20)
    foreign_players_limit = models.PositiveIntegerField(
        default=5, 
        help_text="Maximum number of foreign players allowed in match squad"
    )

    class Meta:
        unique_together = ['country', 'level']
        ordering = ['country', 'level']

    def __str__(self):
        return f"{self.name} ({self.country})"

class Championship(models.Model):
    """Model for representing a championship competition"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')
    ]

    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE
    )
    league = models.ForeignKey(
        League, 
        on_delete=models.CASCADE
    )
    teams = models.ManyToManyField(
        Club, 
        through='ChampionshipTeam'
    )
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
    championship = models.ForeignKey(
        Championship, 
        on_delete=models.CASCADE
    )
    match = models.OneToOneField(
        Match, 
        on_delete=models.CASCADE
    )
    round = models.PositiveIntegerField()
    match_day = models.PositiveIntegerField()
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['round', 'match_day']

    def __str__(self):
        return f"Round {self.round}: {self.match}"