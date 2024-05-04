from django.db import models
from django_countries.fields import CountryField

class Player(models.Model):
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, verbose_name="Club")
    age = models.PositiveIntegerField(default=17, verbose_name="Age")
    nationality = CountryField(blank_label='(select country)', verbose_name="Nationality")

    def __str__(self):
        return f"{self.club.name} player aged {self.age} from {self.nationality}"

    def save(self, *args, **kwargs):
        if not self.nationality:
            self.nationality = self.club.country
        super(Player, self).save(*args, **kwargs)
