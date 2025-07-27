# matches/models.py

from django.db import models
# from django.conf import settings # Не используется
from clubs.models import Club
from players.models import Player # Убедитесь, что этот импорт корректен
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
        help_text="Indicates if match result has been processed" # Немного уточнил help_text
    )
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    # --- ИСПРАВЛЕНО ИМЯ ПОЛЯ ---
    # Было: curent_posses
    possession_indicator = models.PositiveIntegerField(
        default=0,
        help_text="Indicates possession: 0=None/Start, 1=Home, 2=Away",
        verbose_name="Possession Indicator" # Добавил verbose_name
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

    # Составы команд
    home_lineup = models.JSONField(null=True, blank=True)
    away_lineup = models.JSONField(null=True, blank=True)

    # Тактики команд
    home_tactic = models.CharField(max_length=20, default='balanced')
    away_tactic = models.CharField(max_length=20, default='balanced')

    # Текущая минута матча
    current_minute = models.PositiveIntegerField(default=1)

    # Метка времени начала матча и последнего обновления минуты
    started_at = models.DateTimeField(null=True, blank=True)
    last_minute_update = models.DateTimeField(null=True, blank=True)

    # Флаг ожидания перехода на следующую минуту
    waiting_for_next_minute = models.BooleanField(default=False)

    # Текущий игрок, владеющий мячом, и текущая зона
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

    # Статистика матча
    st_shoots = models.PositiveIntegerField(default=0, verbose_name="Shoots")
    st_passes = models.PositiveIntegerField(default=0, verbose_name="Passes")
    # --- ИСПРАВЛЕНО ИМЯ ПОЛЯ ---
    # Было: st_posessions
    st_possessions = models.PositiveIntegerField(default=0, verbose_name="Possessions (%)") # Уточнил
    # --------------------------
    st_fouls = models.PositiveIntegerField(default=0, verbose_name="Fouls")
    # Поле для травм - просто счетчик? Если да, ок. Если нужны детали, лучше JSONField или отдельная модель.
    st_injury = models.PositiveIntegerField(default=0, verbose_name="Injuries Count")

    # Momentum and pass streaks
    home_momentum = models.IntegerField(default=0)
    away_momentum = models.IntegerField(default=0)
    home_pass_streak = models.PositiveIntegerField(default=0)
    away_pass_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        dt_str = timezone.localtime(self.datetime).strftime('%d.%m.%Y %H:%M') if self.datetime else "N/A" # Локальное время
        return f"{self.home_team.name} vs {self.away_team.name} ({dt_str}) - {self.get_status_display()}" # Используем get_status_display

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['-datetime'] # Сортировка по дате по умолчанию


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
    # Основной игрок события
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='match_events'
    )
    # Второй игрок, связанный с событием
    related_player = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='related_match_events'
    )
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        player_info = f" ({self.player.last_name})" if self.player else ""
        related_info = f" -> {self.related_player.last_name}" if self.related_player else ""
        return f"M{self.match.id}-Min{self.minute}: {self.get_event_type_display()}{player_info}{related_info}"

    class Meta:
        # Сортировка сначала по минуте, потом по времени создания
        ordering = ['match', 'minute', 'timestamp']
        verbose_name = "Match Event"
        verbose_name_plural = "Match Events"
        indexes = [
            models.Index(fields=['match', 'minute']),  # Индекс для оптимизации запросов событий по матчу и минуте
        ]


class PlayerRivalry(models.Model):
    """
    Модель для отслеживания соперничества между игроками
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
    
    # Влияние на игру
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
    Модель для отслеживания химии между игроками команды
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
    
    # Влияние на игру
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
    Модель для отслеживания эволюции характера игрока
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
    
    # Контекст изменения
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
        return f"{self.player.full_name}: {self.trait_changed} {self.old_value}→{self.new_value}"


class NarrativeEvent(models.Model):
    """
    Модель для хранения нарративных событий и историй
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
    
    # Участники события
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
    
    # Контекст
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='narrative_events'
    )
    minute = models.PositiveIntegerField()
    
    # Содержание
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Метаданные
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
