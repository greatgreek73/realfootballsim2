from django.db import models
from django_countries.fields import CountryField

class Player(models.Model):
    POSITIONS = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Right Back', 'Right Back'),
        ('Left Back', 'Left Back'),
        ('Center Back', 'Center Back'),
        ('Defensive Midfielder', 'Central Defensive Midfielder'),
        ('Left Defensive Midfielder', 'Left Defensive Midfielder'),
        ('Right Defensive Midfielder', 'Right Defensive Midfielder'),
        ('Right Midfielder', 'Right Midfielder'),
        ('Central Midfielder', 'Central Midfielder'),
        ('Left Midfielder', 'Left Midfielder'),
        ('Attacking Midfielder', 'Attacking Midfielder'),
        ('Center Forward', 'Center Forward'),
    ]

    first_name = models.CharField(max_length=100, default='', verbose_name="First Name")
    last_name = models.CharField(max_length=100, default='', verbose_name="Last Name")
    age = models.PositiveIntegerField(default=17, verbose_name="Age")
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, verbose_name="Club", null=True, blank=True)
    nationality = CountryField(blank_label='(select country)', verbose_name="Nationality", default="Unknown")
    position = models.CharField(max_length=50, choices=POSITIONS, default='Unknown', verbose_name="Position")

    # Skills (характеристики для всех игроков)
    strength = models.IntegerField(null=True, blank=True, verbose_name="Strength")
    stamina = models.IntegerField(null=True, blank=True, verbose_name="Stamina")
    pace = models.IntegerField(null=True, blank=True, verbose_name="Pace")
    marking = models.IntegerField(null=True, blank=True, verbose_name="Marking")
    tackling = models.IntegerField(null=True, blank=True, verbose_name="Tackling")
    work_rate = models.IntegerField(null=True, blank=True, verbose_name="Work Rate")
    positioning = models.IntegerField(null=True, blank=True, verbose_name="Positioning")
    passing = models.IntegerField(null=True, blank=True, verbose_name="Passing")
    crossing = models.IntegerField(null=True, blank=True, verbose_name="Crossing")
    dribbling = models.IntegerField(null=True, blank=True, verbose_name="Dribbling")
    ball_control = models.IntegerField(null=True, blank=True, verbose_name="Ball Control")
    heading = models.IntegerField(null=True, blank=True, verbose_name="Heading")
    finishing = models.IntegerField(null=True, blank=True, verbose_name="Finishing")
    long_range = models.IntegerField(null=True, blank=True, verbose_name="Long Range")
    vision = models.IntegerField(null=True, blank=True, verbose_name="Vision")

    # Goalkeeper-specific skills (для вратарей)
    handling = models.IntegerField(null=True, blank=True, verbose_name="Handling")
    reflexes = models.IntegerField(null=True, blank=True, verbose_name="Reflexes")
    aerial = models.IntegerField(null=True, blank=True, verbose_name="Aerial")
    jumping = models.IntegerField(null=True, blank=True, verbose_name="Jumping")
    command = models.IntegerField(null=True, blank=True, verbose_name="Command")
    throwing = models.IntegerField(null=True, blank=True, verbose_name="Throwing")
    kicking = models.IntegerField(null=True, blank=True, verbose_name="Kicking")

    class Meta:
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.club.name}) - {self.position}"

    def save(self, *args, **kwargs):
        if not self.nationality:
            self.nationality = self.club.country
        super(Player, self).save(*args, **kwargs)
