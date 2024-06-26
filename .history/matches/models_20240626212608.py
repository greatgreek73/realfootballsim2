from django.db import models
from clubs.models import Club
from players.models import Player
from django.utils import timezone

class Match(models.Model):
    home_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateTimeField()
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')
    ], default='scheduled')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date}"

class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField()
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('substitution', 'Substitution')
    ])
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.match} - {self.event_type} at {self.minute}'"

class TeamSelection(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='team_selections')  # добавьте null=True
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)
    selection = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)  # измените auto_now_add на default
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('match', 'club')

    def __str__(self):
        return f"Team Selection for {self.club} in {self.match}"