from django.db import models
from django_countries.fields import CountryField

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
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, verbose_name="Club", null=True, blank=True)
    nationality = CountryField(blank_label='(select country)', verbose_name="Nationality", default="Unknown")
    position = models.CharField(max_length=50, choices=POSITIONS, default='Unknown', verbose_name="Position")
    player_class = models.IntegerField(default=1, verbose_name="Player Class")

    # Общие характеристики
    strength = models.IntegerField(default=0, verbose_name="Strength")
    stamina = models.IntegerField(default=0, verbose_name="Stamina")
    pace = models.IntegerField(default=0, verbose_name="Pace")
    positioning = models.IntegerField(default=0, verbose_name="Positioning")

    # Характеристики для вратарей
    reflexes = models.IntegerField(default=0, verbose_name="Reflexes")
    handling = models.IntegerField(default=0, verbose_name="Handling")
    aerial = models.IntegerField(default=0, verbose_name="Aerial")
    command = models.IntegerField(default=0, verbose_name="Command")
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

    class Meta:
        unique_together = ('first_name', 'last_name')
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.club.name if self.club else 'No Club'}) - {self.position}"

    def save(self, *args, **kwargs):
        if not self.nationality and self.club:
            self.nationality = self.club.country
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_goalkeeper(self):
        return self.position == 'Goalkeeper'

    @property
    def overall_rating(self):
        """Вычисляет общий рейтинг игрока на основе его характеристик,
        учитывая опыт. Допустим, за каждый 1.0 опыта характеристики растут на 1%."""

        # Коэффициент влияния опыта (1% за единицу опыта)
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

        # Применяем опытный множитель к каждой характеристике
        adjusted_attributes = [int(attr * experience_multiplier) for attr in attributes]

        return sum(adjusted_attributes) // len(adjusted_attributes)

    def get_position_specific_attributes(self):
        """Возвращает атрибуты, специфичные для позиции игрока"""
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
