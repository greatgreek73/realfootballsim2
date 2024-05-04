from django.db import models
from django_countries.fields import CountryField
from clubs.models import Club  # Убедитесь, что путь к модели Club правильный

class Player(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Club")
    age = models.PositiveIntegerField(default=17, verbose_name="Age")
    nationality = CountryField(blank_label='(select country)', verbose_name="Nationality")

    def __str__(self):
        return f"{self.club.name} player aged {self.age} from {self.nationality}"

    def save(self, *args, **kwargs):
        if not self.nationality:
            self.nationality = self.club.country
        super(Player, self).save(*args, **kwargs)
