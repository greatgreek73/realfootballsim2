from django.test import TestCase
from matches.match_simulation import simulate_one_action
from matches.models import Match
from clubs.models import Club
from players.models import Player

class MatchSimulationTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="Home", is_bot=True)
        self.away = Club.objects.create(name="Away", is_bot=True)
        self.home_players = [
            Player.objects.create(first_name=f"H{i}", last_name="P", club=self.home, position="Center Forward")
            for i in range(11)
        ]
        self.away_players = [
            Player.objects.create(first_name=f"A{i}", last_name="P", club=self.away, position="Center Forward")
            for i in range(11)
        ]
        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status='in_progress',
            home_lineup={str(i): {'playerId': str(p.id)} for i,p in enumerate(self.home_players)},
            away_lineup={str(i): {'playerId': str(p.id)} for i,p in enumerate(self.away_players)},
        )
        self.match.current_player_with_ball = self.home_players[0]
        self.match.save()

    def test_simulate_one_action_returns_dict(self):
        result = simulate_one_action(self.match)
        self.assertIsInstance(result, dict)
        self.assertIn('action_type', result)
