from __future__ import annotations

from typing import Dict, List

from faker import Faker

from players.models import Player
from players.utils import generate_player_stats

from .country_locales import country_locales


def get_locale_from_country_code(country_code: str) -> str:
    """
    Вернуть локаль Faker для указанной страны.
    Использует fall-back на en_US, если код не найден.
    """
    return country_locales.get(country_code, "en_US")


def generate_initial_players(club) -> None:
    """
    Создать стартовый состав из 16 игроков для клуба.
    Повторяет прежнюю логику CreateClubView.generate_initial_players.
    """
    positions: List[Dict[str, object]] = [
        # Основной состав (11)
        {"position": "Goalkeeper", "class": 4},
        {"position": "Right Back", "class": 4},
        {"position": "Center Back", "class": 4},
        {"position": "Center Back", "class": 4},
        {"position": "Left Back", "class": 4},
        {"position": "Left Midfielder", "class": 4},
        {"position": "Central Midfielder", "class": 4},
        {"position": "Central Midfielder", "class": 4},
        {"position": "Right Midfielder", "class": 4},
        {"position": "Center Forward", "class": 4},
        {"position": "Center Forward", "class": 4},
        # Запас (5)
        {"position": "Goalkeeper", "class": 4},
        {"position": "Center Back", "class": 4},
        {"position": "Central Midfielder", "class": 4},
        {"position": "Central Midfielder", "class": 4},
        {"position": "Center Forward", "class": 4},
    ]

    country_code = getattr(club.country, "code", None) or str(club.country)
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    for info in positions:
        while True:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male() if hasattr(fake, "last_name_male") else fake.last_name()
            if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                break

        stats = generate_player_stats(info["position"], info["class"])

        Player.objects.create(
            club=club,
            first_name=first_name,
            last_name=last_name,
            nationality=club.country,
            age=17,
            position=info["position"],
            player_class=info["class"],
            **stats,
        )
