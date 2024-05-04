from django.db import models
from clubs.models import Club

class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Characteristic(models.Model):
    name = models.CharField(max_length=255)
    default_value = models.IntegerField(default=20)  # Добавлено значение по умолчанию

    def __str__(self):
        return self.name

class PlayerCharacteristic(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='characteristics')
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    value = models.IntegerField(default=20)  # Начальное значение характеристик

    def __str__(self):
        return f"{self.player.name} - {self.characteristic.name}: {self.value}"
