from django.test import TestCase
from tournaments.tasks import simulate_active_matches

class CeleryTaskTests(TestCase):
    def test_simulate_active_matches_no_games(self):
        result = simulate_active_matches()
        self.assertEqual(result, "No matches in progress")
