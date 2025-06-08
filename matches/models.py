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
