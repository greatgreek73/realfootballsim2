from django.db import models
from django.conf import settings
from clubs.models import Club
from django.utils import timezone

class Match(models.Model):
    home_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='away_matches')
    datetime = models.DateTimeField(
        verbose_name="Match Date and Time",
        db_index=True,
        null=True,
        blank=True
    )
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates if match has been processed"
    )
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('paused', 'Paused'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled')
        ],
        default='scheduled',
        db_index=True
    )
    
    # Составы команд (хранятся в формате JSON)
    home_lineup = models.JSONField(null=True, blank=True)
    away_lineup = models.JSONField(null=True, blank=True)

    # Тактики команд
    home_tactic = models.CharField(max_length=20, default='balanced')
    away_tactic = models.CharField(max_length=20, default='balanced')

    # Текущая минута матча
    current_minute = models.PositiveIntegerField(default=0)

    # Новые поля: текущий игрок, владеющий мячом, и текущая зона (5-уровневая система)
    current_player_with_ball = models.ForeignKey(
        'players.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_with_ball'
    )
    current_zone = models.CharField(
        max_length=10,
        choices=[
            ('GK', 'GK'),
            ('DEF', 'DEF'),
            ('DM', 'DM'),
            ('AM', 'AM'),
            ('FWD', 'FWD')
        ],
        default='GK'
    )
    #statistics
    st_shoots = models.PositiveBigIntegerField(default=0)
    st_passes = models.PositiveBigIntegerField(default=0)
    st_posessions = models.PositiveBigIntegerField(default=0)
    st_fouls = models.PositiveBigIntegerField(default=0)
    st_injury = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.datetime}"


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField()
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('pass', 'Pass'),
        ('interception', 'Interception'),
        ('shot_miss', 'Shot Miss'),
        ('info', 'Info'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('substitution', 'Substitution')
    ])
    # Теперь поле player позволяет указать конкретного игрока, участвующего в событии
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.match} - {self.event_type} at {self.minute}'"
