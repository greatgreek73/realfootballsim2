# matches/models.py

from django.db import models
from django.conf import settings # Не используется, можно убрать, если нет User = settings.AUTH_USER_MODEL
from clubs.models import Club
from players.models import Player # Добавляем импорт Player
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
    
    # Опечатка исправлена: curent_posses -> current_posses
    curent_posses = models.PositiveIntegerField(
        default=0, 
        help_text="Indicates possession: 0=None/Start, 1=Home, 2=Away"
    ) 
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('paused', 'Paused'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled'),
            ('error', 'Error') # Добавим статус ошибки
        ],
        default='scheduled',
        db_index=True
    )
    
    # Составы команд (хранятся в формате JSON)
    # Убедитесь, что у вас установлен необходимый бэкенд для JSONField (например, PostgreSQL)
    home_lineup = models.JSONField(null=True, blank=True)
    away_lineup = models.JSONField(null=True, blank=True)

    # Тактики команд
    home_tactic = models.CharField(max_length=20, default='balanced')
    away_tactic = models.CharField(max_length=20, default='balanced')

    # Текущая минута матча
    current_minute = models.PositiveIntegerField(default=0)

    # Текущий игрок, владеющий мячом, и текущая зона
    current_player_with_ball = models.ForeignKey(
        Player, # Используем импортированную модель Player
        on_delete=models.SET_NULL, # При удалении игрока поле обнуляется
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
            ('MID', 'MID'), # Добавим MID, если используется в transition_map
            ('AM', 'AM'),
            ('FWD', 'FWD')
        ],
        default='GK'
    )
    
    # Статистика матча
    # Опечатка исправлена: st_posessions -> st_possessions
    st_shoots = models.PositiveIntegerField(default=0) # BigIntegerField может быть избыточен
    st_passes = models.PositiveIntegerField(default=0)
    st_posessions = models.PositiveIntegerField(default=0)
    st_fouls = models.PositiveIntegerField(default=0)
    st_injury = models.PositiveIntegerField(default=0)

    def __str__(self):
        dt_str = self.datetime.strftime('%Y-%m-%d %H:%M') if self.datetime else "N/A"
        return f"{self.home_team.name} vs {self.away_team.name} ({dt_str}) - Status: {self.status}"

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['-datetime'] # Сортировка по дате по умолчанию


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField(db_index=True) # Добавим индекс для фильтрации по минуте
    event_type = models.CharField(
        max_length=30, # Увеличим длину для возможных новых типов
        choices=[
            ('goal', 'Goal'),
            ('pass', 'Pass'),
            ('interception', 'Interception'),
            ('shot_miss', 'Shot Miss'),
            ('foul', 'Foul'), # Добавим фол
            ('injury_concern', 'Injury Concern'), # Добавим травму
            ('info', 'Info'),
            ('match_start', 'Match Start'), # Добавим события старта/конца
            ('half_time', 'Half Time'),
            ('match_end', 'Match End'),
            ('match_paused', 'Match Paused'), # Событие паузы
            ('yellow_card', 'Yellow Card'),
            ('red_card', 'Red Card'),
            ('substitution', 'Substitution')
        ],
        db_index=True # Добавим индекс для фильтрации по типу
    )
    # Основной игрок события
    player = models.ForeignKey(
        Player, # Используем импортированную модель Player
        on_delete=models.SET_NULL, # При удалении игрока поле обнуляется (лучше, чем CASCADE)
        null=True,
        blank=True,
        related_name='match_events' # Стандартное имя для связи "один ко многим"
    )
    
    # --- ДОБАВЛЕНО ПОЛЕ related_player ---
    # Второй игрок, связанный с событием (кому пас, на ком сфолили и т.д.)
    related_player = models.ForeignKey(
        Player, # Используем импортированную модель Player
        null=True,       # Разрешаем быть пустым
        blank=True,      # Разрешаем быть пустым в формах/админке
        on_delete=models.SET_NULL, # При удалении связанного игрока поле станет NULL
        related_name='related_match_events' # Уникальное related_name
    )
    # --------------------------------------

    description = models.TextField(blank=True) # Описание может быть пустым
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True) # Индекс для сортировки

    def __str__(self):
        player_info = f" ({self.player.last_name})" if self.player else ""
        related_info = f" -> {self.related_player.last_name}" if self.related_player else ""
        return f"M{self.match.id}-Min{self.minute}: {self.get_event_type_display()}{player_info}{related_info}"

    class Meta:
        ordering = ['timestamp'] # Сортировка по времени создания по умолчанию
        verbose_name = "Match Event"
        verbose_name_plural = "Match Events"