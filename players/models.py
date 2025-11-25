from django.db import models
from django.db.models import JSONField
from django.conf import settings
from django_countries.fields import CountryField

# === Добавленная функция вне класса Player ===
def get_player_line(player):
    """
    Возвращает строку из ['GK', 'DEF', 'MID', 'FWD'],
    соответствующую позиции игрока:
      - GK:  если position == 'Goalkeeper'
      - DEF: если 'Back' в position или position == 'Defensive Midfielder'
      - MID: если 'Midfielder' в position (включая Attacking Midfielder)
      - FWD: если 'Forward' в position
    """
    if player.position == 'Goalkeeper':
        return 'GK'
    if 'Back' in player.position or player.position == 'Defensive Midfielder':
        return 'DEF'
    if 'Midfielder' in player.position:  # включая Attacking Midfielder
        return 'MID'
    if 'Forward' in player.position:
        return 'FWD'
    return 'MID'  # fallback


class Player(models.Model):
    POSITIONS = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Right Back', 'Right Back'),
        ('Left Back', 'Left Back'),
        ('Center Back', 'Center Back'),
        ('Defensive Midfielder', 'Central Defensive Midfielder'),
        ('Right Midfielder', 'Right Midfielder'),
        ('Central Midfielder', 'Central Midfielder'),
        ('Left Midfielder', 'Left Midfielder'),
        ('Attacking Midfielder', 'Attacking Midfielder'),
        ('Center Forward', 'Center Forward'),
    ]

    # Базовая информация
    first_name = models.CharField(max_length=100, default='', verbose_name="First Name")
    last_name = models.CharField(max_length=100, default='', verbose_name="Last Name")
    age = models.PositiveIntegerField(default=17, verbose_name="Age")
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        verbose_name="Club",
        null=True,
        blank=True
    )
    nationality = CountryField(
        blank_label='(select country)',
        verbose_name="Nationality",
        default="Unknown"
    )
    position = models.CharField(
        max_length=50,
        choices=POSITIONS,
        default='Unknown',
        verbose_name="Position"
    )
    player_class = models.IntegerField(
        default=1,
        verbose_name="Player Class"
    )

    avatar = models.ImageField(upload_to="players/avatars/", null=True, blank=True)

    # Общие характеристики
    strength = models.IntegerField(default=0, verbose_name="Strength")
    stamina = models.IntegerField(default=0, verbose_name="Stamina")
    morale = models.IntegerField(default=0, verbose_name="Morale")
    base_morale = models.IntegerField(default=50, verbose_name="Base Morale", 
                                     help_text="Базовый уровень морали, к которому стремится текущая мораль")
    pace = models.IntegerField(default=0, verbose_name="Pace")
    positioning = models.IntegerField(default=0, verbose_name="Positioning")

    # Характеристики для вратарей
    reflexes = models.IntegerField(default=0, verbose_name="Reflexes")
    handling = models.IntegerField(default=0, verbose_name="Handling")
    aerial = models.IntegerField(default=0, verbose_name="Aerial")
    command = models.IntegerField(default=0, verbose_name="Command")

    def get_purchase_cost(self):
        """
        Возвращает базовую стоимость покупки игрока
        """
        # Определяем базовые цены в зависимости от класса игрока
        player_prices = {
            1: 100,  # Класс 1 (низший)
            2: 200,  # Класс 2
            3: 300,  # Класс 3
            4: 500,  # Класс 4
            5: 800,  # Класс 5 (высший)
        }
        
        # Базовая цена в зависимости от класса игрока
        base_price = player_prices.get(self.player_class, 100)
        
        # Модификатор в зависимости от возраста
        age_modifier = 1.0
        if self.age < 23:
            age_modifier = 1.2  # Молодые игроки стоят дороже
        elif self.age > 30:
            age_modifier = 0.8  # Возрастные игроки стоят дешевле
        
        # Модификатор в зависимости от общего рейтинга
        rating_modifier = self.overall_rating / 70.0
        
        # Итоговая стоимость
        final_cost = int(base_price * age_modifier * rating_modifier)
        
        return max(50, final_cost)  # Минимальная стоимость 50 токенов

    distribution = models.IntegerField(default=0, verbose_name="Distribution")
    one_on_one = models.IntegerField(default=0, verbose_name="One on One")
    rebound_control = models.IntegerField(default=0, verbose_name="Rebound Control")
    shot_reading = models.IntegerField(default=0, verbose_name="Shot Reading")

    # Характеристики для полевых игроков
    marking = models.IntegerField(default=0, verbose_name="Marking")
    tackling = models.IntegerField(default=0, verbose_name="Tackling")
    work_rate = models.IntegerField(default=0, verbose_name="Work Rate")
    passing = models.IntegerField(default=0, verbose_name="Passing")
    crossing = models.IntegerField(default=0, verbose_name="Crossing")
    dribbling = models.IntegerField(default=0, verbose_name="Dribbling")
    flair = models.IntegerField(default=0, verbose_name="Flair")
    heading = models.IntegerField(default=0, verbose_name="Heading")
    finishing = models.IntegerField(default=0, verbose_name="Finishing")
    long_range = models.IntegerField(default=0, verbose_name="Long Range")
    vision = models.IntegerField(default=0, verbose_name="Vision")
    accuracy = models.IntegerField(default=0, verbose_name="Accuracy")

    # Новое поле опыта
    experience = models.FloatField(default=0.0, verbose_name="Experience")

    # Счётчик, сколько раз уже прокачивали игрока за токены
    boost_count = models.PositiveIntegerField(
        default=0,
        help_text="How many times this player was boosted via tokens."
    )

    last_trained_at = models.DateTimeField(null=True, blank=True, verbose_name="Last regular training at")

    # === Поля системы расцвета ===
    BLOOM_TYPES = [
        ('early', 'Early Bloom'),    # Ранний расцвет (17 лет)
        ('middle', 'Middle Bloom'),  # Средний расцвет (18-19 лет) 
        ('late', 'Late Bloom'),      # Поздний расцвет (20-21 год)
    ]
    
    bloom_type = models.CharField(
        max_length=10,
        choices=BLOOM_TYPES,
        default='middle',
        verbose_name="Bloom Type",
        help_text="Тип расцвета игрока, определяющий возраст и силу бонуса"
    )
    
    bloom_start_age = models.PositiveIntegerField(
        default=18,
        verbose_name="Bloom Start Age",
        help_text="Возраст начала расцвета игрока"
    )
    
    bloom_seasons_left = models.PositiveIntegerField(
        default=0,
        verbose_name="Bloom Seasons Left",
        help_text="Количество оставшихся сезонов расцвета (0 = расцвет не активен)"
    )

    # === Поля для Narrative AI Engine ===
    personality_traits = JSONField(
        default=dict,
        blank=True,
        help_text="Player personality traits for the Narrative AI Engine"
    )

    class Meta:
        unique_together = ('first_name', 'last_name')
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        ordering = ['last_name', 'first_name']

    # === Группы характеристик (полевые игроки) ===
    FIELD_PLAYER_GROUPS = {
        # Физические
        'physical': ('strength', 'stamina', 'pace'),
        # Защитные
        'defensive': ('marking', 'tackling', 'heading'),
        # Атакующие
        'attacking': ('finishing', 'heading', 'long_range'),
        # Ментальные
        'mental': ('vision', 'flair'),
        # Технические
        'technical': ('dribbling', 'crossing', 'passing'),
        # Тактические
        'tactical': ('work_rate', 'positioning', 'accuracy'),
    }

    # === Группы характеристик (вратари) ===
    GOALKEEPER_GROUPS = {
        'physical': ('strength', 'stamina', 'pace'),
        'core_gk_skills': ('reflexes', 'handling', 'positioning', 'aerial'),
        'additional_gk_skills': (
            'command',
            'distribution',
            'one_on_one',
            'shot_reading',
            'rebound_control'
        ),
    }

    def __str__(self):
        club_name = self.club.name if self.club else 'No Club'
        return f"{self.first_name} {self.last_name} ({club_name}) - {self.position}"

    def save(self, *args, **kwargs):
        # Set nationality based on club if not already set
        if not self.nationality and self.club:
            self.nationality = self.club.country
        
        # Auto-generate personality traits for new players
        if (not self.pk and  # только для новых игроков
            not self.personality_traits and  # только если personality_traits пустой  
            getattr(settings, 'USE_PERSONALITY_ENGINE', False)):  # проверка флага
            
            from .personality import PersonalityGenerator
            self.personality_traits = PersonalityGenerator.generate()
        
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_goalkeeper(self):
        return self.position == 'Goalkeeper'

    @property
    def overall_rating(self):
        """
        Вычисляет общий рейтинг игрока на основе его характеристик,
        учитывая опыт (1% прибавки за 1.0 опыта).
        """
        experience_multiplier = 1 + self.experience * 0.01

        if self.is_goalkeeper:
            attributes = [
                self.reflexes, self.handling, self.aerial,
                self.command, self.distribution, self.one_on_one,
                self.rebound_control, self.shot_reading,
                self.strength, self.stamina, self.pace, self.positioning
            ]
        else:
            attributes = [
                self.strength, self.stamina, self.pace,
                self.marking, self.tackling, self.work_rate,
                self.positioning, self.passing, self.crossing,
                self.dribbling, self.flair, self.heading,
                self.finishing, self.long_range, self.vision,
                self.accuracy
            ]

        adjusted = [int(a * experience_multiplier) for a in attributes]
        return sum(adjusted) // len(adjusted)

    def get_position_specific_attributes(self):
        """Возвращает атрибуты, специфичные для позиции игрока."""
        if self.is_goalkeeper:
            return {
                'reflexes': self.reflexes,
                'handling': self.handling,
                'aerial': self.aerial,
                'command': self.command,
                'distribution': self.distribution,
                'one_on_one': self.one_on_one,
                'rebound_control': self.rebound_control,
                'shot_reading': self.shot_reading
            }
        else:
            return {
                'marking': self.marking,
                'tackling': self.tackling,
                'work_rate': self.work_rate,
                'passing': self.passing,
                'crossing': self.crossing,
                'dribbling': self.dribbling,
                'flair': self.flair,
                'heading': self.heading,
                'finishing': self.finishing,
                'long_range': self.long_range,
                'vision': self.vision,
                'accuracy': self.accuracy
            }

    def get_boost_cost(self) -> int:
        """
        Возвращает стоимость (в токенах) для следующей платной тренировки:
          - 1-я тренировка: 0 токенов
          - 2-я тренировка: 1 токен
          - 3-я тренировка: 2 токена
          - 4-я тренировка: 4 токенов
          - 5-я тренировка: 8 токенов
          - ...
        """
        if self.boost_count == 0:
            return 0
        return 2 ** (self.boost_count - 1)

    # === Добавленный метод внутри Player (шаг 1) ===
    def sum_attributes(self):
        """
        Возвращает сумму всех характеристик игрока (и вратарских, и полевых),
        чтобы можно было определить «самого сильного» по общему количеству очков.
        """
        attrs = [
            self.strength, self.stamina, self.pace, self.positioning,
            self.reflexes, self.handling, self.aerial, self.command,
            self.distribution, self.one_on_one, self.rebound_control,
            self.shot_reading, self.marking, self.tackling, self.work_rate,
            self.passing, self.crossing, self.dribbling, self.flair,
            self.heading, self.finishing, self.long_range, self.vision,
            self.accuracy
        ]
        return sum(attrs)
    
    # === Методы для системы расцвета ===
    @property
    def is_in_bloom(self):
        """Проверяет, находится ли игрок в периоде расцвета."""
        return self.bloom_seasons_left > 0
    
    def get_bloom_bonus(self):
        """Возвращает множитель бонуса за тренировки во время расцвета."""
        if not self.is_in_bloom:
            return 0
        
        bloom_bonuses = {
            'early': 1.50,   # +150% очков
            'middle': 1.00,  # +100% очков
            'late': 0.75,    # +75% очков
        }
        return bloom_bonuses.get(self.bloom_type, 0)
    
    def get_age_training_modifier(self):
        """Возвращает множитель эффективности тренировок в зависимости от возраста."""
        if self.age <= 22:
            return 1.20  # +20% (пик молодости)
        elif self.age <= 26:
            return 1.00  # +0% (базовый уровень)
        elif self.age <= 29:
            return 0.85  # -15% (начало спада)
        elif self.age <= 32:
            return 0.75  # -25% (заметный спад)
        elif self.age <= 35:
            return 0.60  # -40% (сильный спад)
        else:
            return 0.40  # -60% (критический спад)
    
    def should_start_bloom(self):
        """Проверяет, должен ли игрок войти в период расцвета."""
        return (self.age >= self.bloom_start_age and 
                self.bloom_seasons_left == 0)
    
    def start_bloom(self):
        """Запускает период расцвета игрока."""
        if self.should_start_bloom():
            self.bloom_seasons_left = 3
            self.save()
    
    def advance_bloom_season(self):
        """Уменьшает количество сезонов расцвета на 1."""
        if self.bloom_seasons_left > 0:
            self.bloom_seasons_left -= 1
            self.save()


# Импорт модели настроек тренировок
from .training import TrainingSettings
