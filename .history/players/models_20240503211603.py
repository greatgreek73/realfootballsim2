from django.db import models
from django_countries.fields import CountryField

class Player(models.Model):
    age = models.PositiveIntegerField(default=17, verbose_name="Age")
    nationality = CountryField(blank_label='(select country)', verbose_name="Nationality")

    def __str__(self):
        return f"Player aged {self.age} from {self.nationality}"
