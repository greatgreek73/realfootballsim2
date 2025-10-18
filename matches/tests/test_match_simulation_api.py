import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clubs.models import Club
from matches.models import Match
from players.models import Player


User = get_user_model()


class MatchSimulateApiTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="Home", is_bot=True, country="RU")
        self.away = Club.objects.create(name="Away", is_bot=True, country="RU")

        self.home_player = Player.objects.create(
            first_name="Home",
            last_name="Player",
            club=self.home,
            position="Goalkeeper",
            nationality="RU",
        )
        self.away_player = Player.objects.create(
            first_name="Away",
            last_name="Player",
            club=self.away,
            position="Goalkeeper",
            nationality="RU",
        )

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            current_minute=10,
            home_lineup={"0": {"playerId": str(self.home_player.id)}},
            away_lineup={"0": {"playerId": str(self.away_player.id)}},
        )

        self.user = User.objects.create_user(username="tester", password="pass")
        self.client.force_login(self.user)

    def _simulate_url(self):
        return reverse("api_match_simulate", args=[self.match.id])

    def test_match_simulate_api_uses_row_lock(self):
        original_select_for_update = Match.objects.select_for_update
        call_counter = {"count": 0}

        def tracking(*args, **kwargs):
            call_counter["count"] += 1
            return original_select_for_update(*args, **kwargs)

        with patch("matches.api_views.Match.objects.select_for_update", side_effect=tracking):
            with patch("matches.api_views._simulate_single_step", return_value=[]):
                response = self.client.post(
                    self._simulate_url(),
                    data=json.dumps({"mode": "step"}),
                    content_type="application/json",
                )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(call_counter["count"], 1)

    def test_match_simulate_api_advances_minute_flags(self):
        self.match.waiting_for_next_minute = True
        self.match.last_minute_update = timezone.now() - timedelta(minutes=5)
        self.match.save(update_fields=["waiting_for_next_minute", "last_minute_update"])

        payload = {"mode": "step"}

        with patch("matches.api_views.simulate_one_action", return_value={
            "event": None,
            "continue": False,
        }):
            response = self.client.post(
                self._simulate_url(),
                data=json.dumps(payload),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

        self.match.refresh_from_db()
        self.assertEqual(self.match.current_minute, 11)
        self.assertFalse(self.match.waiting_for_next_minute)
        self.assertTrue(self.match.last_minute_update > timezone.now() - timedelta(minutes=1))
