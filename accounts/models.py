from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    # Поле для хранения баланса токенов
    tokens = models.PositiveIntegerField(
        default=0,
        help_text="Current balance of tokens for user."
    )
    
    # Поле для хранения баланса игровой валюты (деньги)
    money = models.PositiveIntegerField(
        default=1000,
        help_text="Current balance of in-game money for user."
    )
