from django.db import models
from clubs.models import Club

class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Characteristic(models.Model):
    TYPE_CHOICES = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Field Player', 'Field Player'),
        ('Common', 'Common')  # Общие характеристики для всех
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='Common')

    def __str__(self):
        return self.name

class PlayerCharacteristic(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_characteristics')
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)  # Начальное значение может быть задано здесь или определено в другом месте

    def __str__(self):
        return f"{self.player.name} - {self.characteristic.name}: {self.value}"
