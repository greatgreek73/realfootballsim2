from django.db import models
from django.contrib.auth import get_user_model
from clubs.models import Club
from players.models import Player
import random

User = get_user_model()

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
    club = models.OneToOneField(Club, on_delete=models.CASCADE, related_name='team_selection')
    selection = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Team Selection for {self.club.name}"

    def get_or_create_selection(self):
        if not self.selection:
            players = list(Player.objects.filter(club=self.club))
            self.selection = {str(i): player.id for i, player in enumerate(random.sample(players, min(11, len(players))))}
            self.save()
        return self.selection

    def update_selection(self, new_selection):
        self.selection = new_selection
        self.save()

    def complete_selection(self):
        current_selection = set(str(v) for v in self.selection.values())
        all_players = list(Player.objects.filter(club=self.club).exclude(id__in=current_selection))
        
        for i in range(11):
            if str(i) not in self.selection and all_players:
                player = random.choice(all_players)
                self.selection[str(i)] = player.id
                all_players.remove(player)
        
        self.save()