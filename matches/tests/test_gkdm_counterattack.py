from django.test import TestCase
from unittest.mock import patch

from clubs.models import Club
from players.models import Player
from matches.models import Match
from matches.match_simulation import simulate_one_action

DEFAULT_COUNTRY = "RU"
DEFAULT_NATIONALITY = "RU"

TARGET_ZONES = ["DEF-R", "DEF-C", "DEF-L", "DM-R", "DM-C", "DM-L"]


class GKAllZonesCounterattackTests(TestCase):
    """Проверяем, что на любой пас GK → DEF-* или GK → DM-* возникает контратака."""

    def setUp(self):
        self.home = Club.objects.create(name="GKAll Home", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="GKAll Away", is_bot=True, country=DEFAULT_COUNTRY)

        # Вратарь
        self.home_gk = Player.objects.create(
            first_name="GK", last_name="H", club=self.home, position="Goalkeeper",
            nationality=DEFAULT_NATIONALITY
        )

        # Приёмники для каждой зоны
        self.recipients = {
            "DEF-R": Player.objects.create(first_name="HDR", last_name="H", club=self.home,
                                           position="Defender", nationality=DEFAULT_NATIONALITY),
            "DEF-C": Player.objects.create(first_name="HDC", last_name="H", club=self.home,
                                           position="Defender", nationality=DEFAULT_NATIONALITY),
            "DEF-L": Player.objects.create(first_name="HDL", last_name="H", club=self.home,
                                           position="Defender", nationality=DEFAULT_NATIONALITY),
            "DM-R": Player.objects.create(first_name="HMR", last_name="H", club=self.home,
                                          position="Defensive Midfielder", nationality=DEFAULT_NATIONALITY),
            "DM-C": Player.objects.create(first_name="HMC", last_name="H", club=self.home,
                                          position="Defensive Midfielder", nationality=DEFAULT_NATIONALITY),
            "DM-L": Player.objects.create(first_name="HML", last_name="H", club=self.home,
                                          position="Defensive Midfielder", nationality=DEFAULT_NATIONALITY),
        }

        # Один универсальный перехватчик у соперника
        self.away_int = Player.objects.create(
            first_name="INT", last_name="A", club=self.away, position="Attacking Midfielder",
            nationality=DEFAULT_NATIONALITY
        )

        # матчи будем пересоздавать в каждом под-тесте
        self.base_match_kwargs = dict(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={
                "0": {"playerId": str(self.home_gk.id)},
                **{str(i + 1): {"playerId": str(p.id)} for i, p in enumerate(self.recipients.values())},
            },
            away_lineup={"0": {"playerId": str(self.away_int.id)}},
        )

    def choose_factory(self, target_zone):
        """Возвращает функцию-заглушку choose_player под конкретную цель паса."""
        def _choose(team, zone, exclude_ids=None, match=None):
            if team == self.home:
                if zone == target_zone:
                    return self.recipients[target_zone]
                if zone == "GK":
                    return self.home_gk
            else:  # соперник
                # интерцептор в целевой зоне или в зоне AM-* (на всякий случай)
                if zone == target_zone or zone.startswith("AM"):
                    return self.away_int
            return None
        return _choose

    def test_gk_passes_trigger_counterattack(self):
        for tz in TARGET_ZONES:
            with self.subTest(zone=tz):
                match = Match.objects.create(**self.base_match_kwargs)
                match.current_player_with_ball = self.home_gk
                match.current_zone = "GK"
                match.save()

                with patch("matches.match_simulation.next_zone", return_value=tz):
                    with patch("matches.match_simulation.choose_player",
                               side_effect=self.choose_factory(tz)):
                        with patch("matches.commentary.random.choice", side_effect=lambda c: c[0]):
                            # 0.99 — плохой пас, 0.6 — успешный перехват, дальше — нейтральные
                            with patch("matches.match_simulation.random.random",
                                       side_effect=[0.99, 0.6] + [0.5] * 20):
                                result = simulate_one_action(match)

                debug_msg = (
                    f"[DEBUG] Пас GK → {tz}. "
                    f"Контратака: {result.get('additional_event', {}).get('event_type') == 'counterattack'}"
                )
                print(debug_msg)

                self.assertEqual(result["additional_event"]["event_type"], "counterattack")
