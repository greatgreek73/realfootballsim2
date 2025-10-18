from unittest.mock import patch

from django.test import TestCase, override_settings

from clubs.models import Club
from players.models import Player
from matches.personality_engine import PersonalityDecisionEngine


class PersonalityEngineActionTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name="Test Club", is_bot=True, country="RU")
        self.player = Player.objects.create(
            first_name="Test",
            last_name="Player",
            club=self.club,
            position="Central Midfielder",
            nationality="RU",
            personality_traits={
                "risk_taking": 20,
                "teamwork": 14,
                "patience": 4,
                "ambition": 18,
                "leadership": 16,
                "confidence": 15,
            },
        )

    @override_settings(USE_PERSONALITY_ENGINE=True)
    @patch("matches.personality_engine.random.random", return_value=0.01)
    def test_choose_action_type_returns_long_pass(self, random_mock):
        context = {
            "goal_distance": 80,
            "pressure_level": 0.1,
            "teammates_nearby": 0,
            "opponents_nearby": 1,
            "possession_type": "defense",
            "score_difference": 0,
            "match_minute": 12,
        }

        action = PersonalityDecisionEngine.choose_action_type(self.player, context)
        self.assertEqual(action, "long_pass")

    @override_settings(USE_PERSONALITY_ENGINE=True)
    @patch("matches.personality_engine.random.random", return_value=0.99)
    def test_choose_action_type_returns_attack(self, random_mock):
        context = {
            "goal_distance": 35,
            "pressure_level": 0.3,
            "teammates_nearby": 2,
            "opponents_nearby": 1,
            "possession_type": "transition",
            "score_difference": -1,
            "match_minute": 82,
        }

        action = PersonalityDecisionEngine.choose_action_type(self.player, context)
        self.assertEqual(action, "attack")
