# matches/models.py

from django.db import models
# from django.conf import settings # ╨Э╨╡ ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В╤Б╤П
from clubs.models import Club
from players.models import Player # ╨г╨▒╨╡╨┤╨╕╤В╨╡╤Б╤М, ╤З╤В╨╛ ╤Н╤В╨╛╤В ╨╕╨╝╨┐╨╛╤А╤В ╨║╨╛╤А╤А╨╡╨║╤В╨╡╨╜
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
        help_text="Indicates if match result has been processed" # ╨Э╨╡╨╝╨╜╨╛╨│╨╛ ╤Г╤В╨╛╤З╨╜╨╕╨╗ help_text
    )
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    # --- ╨Ш╨б╨Я╨а╨Р╨Т╨Ы╨Х╨Э╨Ю ╨Ш╨Ь╨п ╨Я╨Ю╨Ы╨п ---
    # ╨С╤Л╨╗╨╛: curent_posses
    possession_indicator = models.PositiveIntegerField(
        default=0,
        help_text="Indicates possession: 0=None/Start, 1=Home, 2=Away",
        verbose_name="Possession Indicator" # ╨Ф╨╛╨▒╨░╨▓╨╕╨╗ verbose_name
    )
    # --------------------------

    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('paused', 'Paused'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled'),
            ('error', 'Error')
        ],
        default='scheduled',
        db_index=True
    )

    # ╨б╨╛╤Б╤В╨░╨▓╤Л ╨║╨╛╨╝╨░╨╜╨┤
    home_lineup = models.JSONField(null=True, blank=True)
    away_lineup = models.JSONField(null=True, blank=True)

    # ╨в╨░╨║╤В╨╕╨║╨╕ ╨║╨╛╨╝╨░╨╜╨┤
    home_tactic = models.CharField(max_length=20, default='balanced')
    away_tactic = models.CharField(max_length=20, default='balanced')

    # ╨в╨╡╨║╤Г╤Й╨░╤П ╨╝╨╕╨╜╤Г╤В╨░ ╨╝╨░╤В╤З╨░
    current_minute = models.PositiveIntegerField(default=1)

    # ╨Ь╨╡╤В╨║╨░ ╨▓╤А╨╡╨╝╨╡╨╜╨╕ ╨╜╨░╤З╨░╨╗╨░ ╨╝╨░╤В╤З╨░ ╨╕ ╨┐╨╛╤Б╨╗╨╡╨┤╨╜╨╡╨│╨╛ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╤П ╨╝╨╕╨╜╤Г╤В╤Л
    started_at = models.DateTimeField(null=True, blank=True)
    last_minute_update = models.DateTimeField(null=True, blank=True)
    realtime_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when the current broadcast minute began."
    )
    realtime_last_broadcast_minute = models.PositiveIntegerField(
        default=0,
        help_text="Last game minute that was expanded into a broadcast timeline.",
        db_column='match_last_broadcast_minute'
    )
    minute_building = models.BooleanField(
        default=False,
        help_text="Internal lock that prevents concurrent timeline generation."
    )

    # ╨д╨╗╨░╨│ ╨╛╨╢╨╕╨┤╨░╨╜╨╕╤П ╨┐╨╡╤А╨╡╤Е╨╛╨┤╨░ ╨╜╨░ ╤Б╨╗╨╡╨┤╤Г╤О╤Й╤Г╤О ╨╝╨╕╨╜╤Г╤В╤Г
    waiting_for_next_minute = models.BooleanField(default=False)

    # ╨в╨╡╨║╤Г╤Й╨╕╨╣ ╨╕╨│╤А╨╛╨║, ╨▓╨╗╨░╨┤╨╡╤О╤Й╨╕╨╣ ╨╝╤П╤З╨╛╨╝, ╨╕ ╤В╨╡╨║╤Г╤Й╨░╤П ╨╖╨╛╨╜╨░
    current_player_with_ball = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_with_ball',
        verbose_name="Player with Ball"
    )
    current_zone = models.CharField(
        max_length=10,
        choices=[
            ('GK', 'GK'),
            ('DEF-L', 'DEF-L'), ('DEF-C', 'DEF-C'), ('DEF-R', 'DEF-R'),
            ('DM-L', 'DM-L'), ('DM-C', 'DM-C'), ('DM-R', 'DM-R'),
            ('MID-L', 'MID-L'), ('MID-C', 'MID-C'), ('MID-R', 'MID-R'),
            ('AM-L', 'AM-L'), ('AM-C', 'AM-C'), ('AM-R', 'AM-R'),
            ('FWD-L', 'FWD-L'), ('FWD-C', 'FWD-C'), ('FWD-R', 'FWD-R'),
        ],
        default='GK',
        verbose_name="Current Zone"
    )

    # ╨б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨░ ╨╝╨░╤В╤З╨░
    st_shoots = models.PositiveIntegerField(default=0, verbose_name="Shoots")
    st_passes = models.PositiveIntegerField(default=0, verbose_name="Passes")
    # --- ╨Ш╨б╨Я╨а╨Р╨Т╨Ы╨Х╨Э╨Ю ╨Ш╨Ь╨п ╨Я╨Ю╨Ы╨п ---
    # ╨С╤Л╨╗╨╛: st_posessions
    st_possessions = models.PositiveIntegerField(default=0, verbose_name="Possessions (%)") # ╨г╤В╨╛╤З╨╜╨╕╨╗
    # --------------------------
    st_fouls = models.PositiveIntegerField(default=0, verbose_name="Fouls")
    # ╨Я╨╛╨╗╨╡ ╨┤╨╗╤П ╤В╤А╨░╨▓╨╝ - ╨┐╤А╨╛╤Б╤В╨╛ ╤Б╤З╨╡╤В╤З╨╕╨║? ╨Х╤Б╨╗╨╕ ╨┤╨░, ╨╛╨║. ╨Х╤Б╨╗╨╕ ╨╜╤Г╨╢╨╜╤Л ╨┤╨╡╤В╨░╨╗╨╕, ╨╗╤Г╤З╤И╨╡ JSONField ╨╕╨╗╨╕ ╨╛╤В╨┤╨╡╨╗╤М╨╜╨░╤П ╨╝╨╛╨┤╨╡╨╗╤М.
    st_injury = models.PositiveIntegerField(default=0, verbose_name="Injuries Count")

    # Momentum and pass streaks
    home_momentum = models.IntegerField(default=0)
    away_momentum = models.IntegerField(default=0)
    home_pass_streak = models.PositiveIntegerField(default=0)
    away_pass_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        dt_str = timezone.localtime(self.datetime).strftime('%d.%m.%Y %H:%M') if self.datetime else "N/A" # ╨Ы╨╛╨║╨░╨╗╤М╨╜╨╛╨╡ ╨▓╤А╨╡╨╝╤П
        return f"{self.home_team.name} vs {self.away_team.name} ({dt_str}) - {self.get_status_display()}" # ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝ get_status_display

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['-datetime'] # ╨б╨╛╤А╤В╨╕╤А╨╛╨▓╨║╨░ ╨┐╨╛ ╨┤╨░╤В╨╡ ╨┐╨╛ ╤Г╨╝╨╛╨╗╤З╨░╨╜╨╕╤О


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField(db_index=True)
    event_type = models.CharField(
        max_length=30,
        choices=[
            ('goal', 'Goal'),
            ('pass', 'Pass'),
            ('dribble', 'Dribble'),
            ('interception', 'Interception'),
            ('counterattack', 'Counterattack'),
            ('shot_miss', 'Shot Miss'),
            ('foul', 'Foul'),
            ('injury_concern', 'Injury Concern'),
            ('info', 'Info'),
            ('match_start', 'Match Start'),
            ('half_time', 'Half Time'),
            ('match_end', 'Match End'),
            ('match_paused', 'Match Paused'),
            ('yellow_card', 'Yellow Card'),
            ('red_card', 'Red Card'),
            ('substitution', 'Substitution')
        ],
        db_index=True
    )
    # ╨Ю╤Б╨╜╨╛╨▓╨╜╨╛╨╣ ╨╕╨│╤А╨╛╨║ ╤Б╨╛╨▒╤Л╤В╨╕╤П
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='match_events'
    )
    # ╨Т╤В╨╛╤А╨╛╨╣ ╨╕╨│╤А╨╛╨║, ╤Б╨▓╤П╨╖╨░╨╜╨╜╤Л╨╣ ╤Б ╤Б╨╛╨▒╤Л╤В╨╕╨╡╨╝
    related_player = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='related_match_events'
    )
    description = models.TextField(blank=True)
    personality_reason = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        player_info = f" ({self.player.last_name})" if self.player else ""
        related_info = f" -> {self.related_player.last_name}" if self.related_player else ""
        return f"M{self.match.id}-Min{self.minute}: {self.get_event_type_display()}{player_info}{related_info}"

    class Meta:
        # ╨б╨╛╤А╤В╨╕╤А╨╛╨▓╨║╨░ ╤Б╨╜╨░╤З╨░╨╗╨░ ╨┐╨╛ ╨╝╨╕╨╜╤Г╤В╨╡, ╨┐╨╛╤В╨╛╨╝ ╨┐╨╛ ╨▓╤А╨╡╨╝╨╡╨╜╨╕ ╤Б╨╛╨╖╨┤╨░╨╜╨╕╤П
        ordering = ['match', 'minute', 'timestamp']
        verbose_name = "Match Event"
        verbose_name_plural = "Match Events"
        indexes = [
            models.Index(fields=['match', 'minute']),  # ╨Ш╨╜╨┤╨╡╨║╤Б ╨┤╨╗╤П ╨╛╨┐╤В╨╕╨╝╨╕╨╖╨░╤Ж╨╕╨╕ ╨╖╨░╨┐╤А╨╛╤Б╨╛╨▓ ╤Б╨╛╨▒╤Л╤В╨╕╨╣ ╨┐╨╛ ╨╝╨░╤В╤З╤Г ╨╕ ╨╝╨╕╨╜╤Г╤В╨╡
        ]


class PlayerRivalry(models.Model):
    """
    ╨Ь╨╛╨┤╨╡╨╗╤М ╨┤╨╗╤П ╨╛╤В╤Б╨╗╨╡╨╢╨╕╨▓╨░╨╜╨╕╤П ╤Б╨╛╨┐╨╡╤А╨╜╨╕╤З╨╡╤Б╤В╨▓╨░ ╨╝╨╡╨╢╨┤╤Г ╨╕╨│╤А╨╛╨║╨░╨╝╨╕
    """
    RIVALRY_TYPES = [
        ('competitive', 'Competitive Rivalry'),
        ('personal', 'Personal Dislike'),
        ('positional', 'Positional Competition'),
        ('historical', 'Historical Conflict'),
    ]
    
    INTENSITY_LEVELS = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('strong', 'Strong'),
        ('intense', 'Intense'),
    ]
    
    player1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='rivalries_as_player1'
    )
    player2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='rivalries_as_player2'
    )
    rivalry_type = models.CharField(
        max_length=20,
        choices=RIVALRY_TYPES,
        default='competitive'
    )
    intensity = models.CharField(
        max_length=10,
        choices=INTENSITY_LEVELS,
        default='mild'
    )
    created_date = models.DateField(auto_now_add=True)
    last_interaction = models.DateField(null=True, blank=True)
    interaction_count = models.PositiveIntegerField(default=0)
    
    # ╨Т╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╨╕╨│╤А╤Г
    aggression_modifier = models.FloatField(
        default=0.0,
        help_text="Modifier for aggression when playing against rival (-1.0 to 1.0)"
    )
    performance_modifier = models.FloatField(
        default=0.0,
        help_text="Modifier for performance when playing against rival (-1.0 to 1.0)"
    )
    
    class Meta:
        unique_together = ('player1', 'player2')
        verbose_name = "Player Rivalry"
        verbose_name_plural = "Player Rivalries"
        indexes = [
            models.Index(fields=['player1', 'intensity']),
            models.Index(fields=['player2', 'intensity']),
        ]
    
    def __str__(self):
        return f"{self.player1.full_name} vs {self.player2.full_name} ({self.get_intensity_display()})"


class TeamChemistry(models.Model):
    """
    ╨Ь╨╛╨┤╨╡╨╗╤М ╨┤╨╗╤П ╨╛╤В╤Б╨╗╨╡╨╢╨╕╨▓╨░╨╜╨╕╤П ╤Е╨╕╨╝╨╕╨╕ ╨╝╨╡╨╢╨┤╤Г ╨╕╨│╤А╨╛╨║╨░╨╝╨╕ ╨║╨╛╨╝╨░╨╜╨┤╤Л
    """
    CHEMISTRY_TYPES = [
        ('friendship', 'Friendship'),
        ('mentor_mentee', 'Mentor-Mentee'),
        ('partnership', 'Partnership'),
        ('leadership', 'Leadership Bond'),
    ]
    
    player1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='chemistry_as_player1'
    )
    player2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='chemistry_as_player2'
    )
    chemistry_type = models.CharField(
        max_length=20,
        choices=CHEMISTRY_TYPES,
        default='friendship'
    )
    strength = models.FloatField(
        default=0.0,
        help_text="Chemistry strength (0.0 to 1.0)"
    )
    created_date = models.DateField(auto_now_add=True)
    last_positive_interaction = models.DateField(null=True, blank=True)
    positive_interactions = models.PositiveIntegerField(default=0)
    
    # ╨Т╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╨╕╨│╤А╤Г
    passing_bonus = models.FloatField(
        default=0.0,
        help_text="Bonus for passes between these players (0.0 to 1.0)"
    )
    teamwork_bonus = models.FloatField(
        default=0.0,
        help_text="Bonus for teamwork actions (0.0 to 1.0)"
    )
    
    class Meta:
        unique_together = ('player1', 'player2')
        verbose_name = "Team Chemistry"
        verbose_name_plural = "Team Chemistry"
        indexes = [
            models.Index(fields=['player1', 'strength']),
            models.Index(fields=['player2', 'strength']),
        ]
    
    def __str__(self):
        return f"{self.player1.full_name} + {self.player2.full_name} ({self.get_chemistry_type_display()})"


class CharacterEvolution(models.Model):
    """
    ╨Ь╨╛╨┤╨╡╨╗╤М ╨┤╨╗╤П ╨╛╤В╤Б╨╗╨╡╨╢╨╕╨▓╨░╨╜╨╕╤П ╤Н╨▓╨╛╨╗╤О╤Ж╨╕╨╕ ╤Е╨░╤А╨░╨║╤В╨╡╤А╨░ ╨╕╨│╤А╨╛╨║╨░
    """
    EVOLUTION_TRIGGERS = [
        ('goal_scored', 'Goal Scored'),
        ('match_won', 'Match Won'),
        ('match_lost', 'Match Lost'),
        ('rivalry_interaction', 'Rivalry Interaction'),
        ('team_chemistry', 'Team Chemistry Event'),
        ('injury', 'Injury'),
        ('transfer', 'Transfer'),
        ('captain_appointment', 'Captain Appointment'),
    ]
    
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='character_evolutions'
    )
    trigger_event = models.CharField(
        max_length=30,
        choices=EVOLUTION_TRIGGERS
    )
    trait_changed = models.CharField(
        max_length=50,
        help_text="Which personality trait was affected"
    )
    old_value = models.IntegerField()
    new_value = models.IntegerField()
    change_amount = models.IntegerField()
    
    # ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╤П
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Match where evolution occurred"
    )
    related_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Other player involved in evolution trigger"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Character Evolution"
        verbose_name_plural = "Character Evolutions"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['player', 'timestamp']),
            models.Index(fields=['trigger_event', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.player.full_name}: {self.trait_changed} {self.old_value}тЖТ{self.new_value}"


class NarrativeEvent(models.Model):
    """
    ╨Ь╨╛╨┤╨╡╨╗╤М ╨┤╨╗╤П ╤Е╤А╨░╨╜╨╡╨╜╨╕╤П ╨╜╨░╤А╤А╨░╤В╨╕╨▓╨╜╤Л╤Е ╤Б╨╛╨▒╤Л╤В╨╕╨╣ ╨╕ ╨╕╤Б╤В╨╛╤А╨╕╨╣
    """
    EVENT_TYPES = [
        ('rivalry_clash', 'Rivalry Clash'),
        ('chemistry_moment', 'Chemistry Moment'),
        ('character_growth', 'Character Growth'),
        ('leadership_moment', 'Leadership Moment'),
        ('underdog_story', 'Underdog Story'),
        ('veteran_wisdom', 'Veteran Wisdom'),
    ]
    
    IMPORTANCE_LEVELS = [
        ('minor', 'Minor'),
        ('significant', 'Significant'),
        ('major', 'Major'),
        ('legendary', 'Legendary'),
    ]
    
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES
    )
    importance = models.CharField(
        max_length=20,
        choices=IMPORTANCE_LEVELS,
        default='minor'
    )
    
    # ╨г╤З╨░╤Б╤В╨╜╨╕╨║╨╕ ╤Б╨╛╨▒╤Л╤В╨╕╤П
    primary_player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='primary_narrative_events'
    )
    secondary_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_narrative_events'
    )
    
    # ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='narrative_events'
    )
    minute = models.PositiveIntegerField()
    
    # ╨б╨╛╨┤╨╡╤А╨╢╨░╨╜╨╕╨╡
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # ╨Ь╨╡╤В╨░╨┤╨░╨╜╨╜╤Л╨╡
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Narrative Event"
        verbose_name_plural = "Narrative Events"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['match', 'minute']),
            models.Index(fields=['primary_player', 'event_type']),
            models.Index(fields=['importance', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_importance_display()}: {self.title}"
