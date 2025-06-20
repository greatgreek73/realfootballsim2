from django.test import TestCase
from unittest.mock import patch

from clubs.models import Club
from players.models import Player
from matches.models import Match
from matches.match_simulation import simulate_one_action

DEFAULT_COUNTRY = "RU"
DEFAULT_NATIONALITY = "RU"

class DribbleInterceptionTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="Home", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="Away", is_bot=True, country=DEFAULT_COUNTRY)

        self.dribbler = Player.objects.create(
            first_name="D", last_name="H", club=self.home, position="Attacking Midfielder",
            nationality=DEFAULT_NATIONALITY, dribbling=70, pace=70
        )

        self.defender = Player.objects.create(
            first_name="Def", last_name="A", club=self.away, position="Defender",
            nationality=DEFAULT_NATIONALITY
        )

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={"0": {"playerId": str(self.dribbler.id)}},
            away_lineup={"0": {"playerId": str(self.defender.id)}},
        )
        self.match.current_player_with_ball = self.dribbler
        self.match.current_zone = "DM-C"
        self.match.save()

    def choose_mock(self, team, zone, exclude_ids=None, match=None):
        if team == self.away and zone == "DEF-R":
            return self.defender
        if team == self.home and zone == "DM-C":
            return self.dribbler
        return None

    def test_failed_dribble_moves_ball_to_defender(self):
        with patch("matches.match_simulation.forward_dribble_zone", return_value="DM-R"):
            with patch("matches.match_simulation.choose_player", side_effect=self.choose_mock):
                with patch("matches.match_simulation.random.random", side_effect=[0.0, 0.9]):
                    with patch("matches.match_simulation.dribble_success_probability", return_value=0.0):
                        result = simulate_one_action(self.match)
        self.assertEqual(result["action_type"], "interception")
        self.assertEqual(self.match.current_zone, "DEF-R")
        self.assertEqual(self.match.current_player_with_ball, self.defender)

    def test_failed_dribble_triggers_counterattack_in_dm(self):
        """Counterattack event is generated when interception happens in DM."""
        with patch("matches.match_simulation.forward_dribble_zone", return_value="DM-R"):
            with patch("matches.match_simulation.choose_player", side_effect=self.choose_mock):
                with patch("matches.match_simulation.random.random", side_effect=[0.0, 0.9]):
                    with patch("matches.match_simulation.dribble_success_probability", return_value=0.0):
                        result = simulate_one_action(self.match)
        self.assertEqual(result["second_additional_event"]["event_type"], "counterattack")
        self.assertEqual(result["action_type"], "counterattack")

    def test_failed_dribble_triggers_counterattack_in_def(self):
        """Counterattack when the ball is lost in DEF zone."""
        with patch("matches.match_simulation.forward_dribble_zone", return_value="DEF-R"):
            with patch("matches.match_simulation.choose_player", side_effect=self.choose_mock):
                with patch("matches.match_simulation.random.random", side_effect=[0.0, 0.9]):
                    with patch("matches.match_simulation.dribble_success_probability", return_value=0.0):
                        result = simulate_one_action(self.match)
        self.assertEqual(result["second_additional_event"]["event_type"], "counterattack")
        self.assertEqual(result["action_type"], "counterattack")
