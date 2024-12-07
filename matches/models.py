from django.db import models
from django.conf import settings
from clubs.models import Club
from players.models import Player
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
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled')
        ],
        default='scheduled',
        db_index=True
    )
    home_lineup = models.JSONField(null=True, blank=True)
    away_lineup = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.datetime}"


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField()
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('miss', 'Miss'),
        ('possession', 'Possession Change'),
        ('defense_to_midfield', 'Defense to Midfield Transition'),
        ('midfield_to_attack', 'Midfield to Attack Transition'),
        ('attack_to_shot', 'Attack to Shot Opportunity'),
        ('interception', 'Interception'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('substitution', 'Substitution')
    ])
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.match} - {self.event_type} at {self.minute}'"