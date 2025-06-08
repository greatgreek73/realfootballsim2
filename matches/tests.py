from django.test import TestCase
from matches.match_simulation import simulate_one_action, choose_player
from unittest.mock import patch
from matches.models import Match
from clubs.models import Club
from players.models import Player

# Один раз задаём код страны, чтобы не дублировать строку.
DEFAULT_COUNTRY = "RUS"


class MatchSimulationTests(TestCase):
    def setUp(self):
        # ‼️ добавлен аргумент country
        self.home = Club.objects.create(name="Home", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="Away", is_bot=True, country=DEFAULT_COUNTRY)

        self.home_players = [
            Player.objects.create(first_name=f"H{i}", last_name="P",
                                  club=self.home, position="Center Forward")
            for i in range(11)
        ]
        self.away_players = [
            Player.objects.create(first_name=f"A{i}", last_name="P",
                                  club=self.away, position="Center Forward")
            for i in range(11)
        ]

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={str(i): {"playerId": str(p.id)} for i, p in enumerate(self.home_players)},
            away_lineup={str(i): {"playerId": str(p.id)} for i, p in enumerate(self.away_players)},
        )
        self.match.current_player_with_ball = self.home_players[0]
        self.match.save()

    def test_simulate_one_action_returns_dict(self):
        result = simulate_one_action(self.match)
        self.assertIsInstance(result, dict)
        self.assertIn("action_type", result)


class DMRecipientTests(TestCase):
    def setUp(self):
        # ‼️ добавлен аргумент country
        self.home = Club.objects.create(name="Home DM", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="Away DM", is_bot=True, country=DEFAULT_COUNTRY)

        # домашняя команда: полный набор позиций
        self.home_players = [
            Player.objects.create(first_name="GK", last_name="H", club=self.home, position="Goalkeeper"),
            Player.objects.create(first_name="RB", last_name="H", club=self.home, position="Right Back"),
            Player.objects.create(first_name="CB1", last_name="H", club=self.home, position="Center Back"),
            Player.objects.create(first_name="CB2", last_name="H", club=self.home, position="Center Back"),
            Player.objects.create(first_name="LB", last_name="H", club=self.home, position="Left Back"),
            Player.objects.create(first_name="DM1", last_name="H", club=self.home, position="Defensive Midfielder"),
            Player.objects.create(first_name="CM", last_name="H", club=self.home, position="Central Midfielder"),
            Player.objects.create(first_name="RM", last_name="H", club=self.home, position="Right Midfielder"),
            Player.objects.create(first_name="LM", last_name="H", club=self.home, position="Left Midfielder"),
            Player.objects.create(first_name="AM", last_name="H", club=self.home, position="Attacking Midfielder"),
            Player.objects.create(first_name="ST", last_name="H", club=self.home, position="Center Forward"),
        ]
        self.away_players = [
            Player.objects.create(first_name=f"A{i}", last_name="P",
                                  club=self.away, position="Center Forward")
            for i in range(11)
        ]

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={str(i): {"playerId": str(p.id)} for i, p in enumerate(self.home_players)},
            away_lineup={str(i): {"playerId": str(p.id)} for i, p in enumerate(self.away_players)},
        )
        # начинаем с правым защитником (RB) у мяча
        self.match.current_player_with_ball = self.home_players[1]
        self.match.save()

    def test_dm_recipient_position(self):
        defender = self.home_players[1]  # тот самый RB
        dm_positions = {"Defensive Midfielder", "Central Midfielder"}

        for _ in range(50):
            recipient = choose_player(
                self.home,
                "DM-C",
                exclude_ids={defender.id},
                match=self.match,
            )
            self.assertIsNotNone(recipient)
            self.assertIn(recipient.position, dm_positions)


class SpecialCounterLoggingTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="SC Home", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="SC Away", is_bot=True, country=DEFAULT_COUNTRY)

        self.home_gk = Player.objects.create(first_name="HGK", last_name="P", club=self.home, position="Goalkeeper")
        self.home_def = Player.objects.create(first_name="HDEF", last_name="P", club=self.home, position="Right Back")
        self.away_gk = Player.objects.create(first_name="AGK", last_name="P", club=self.away, position="Goalkeeper")
        self.away_def = Player.objects.create(first_name="ADEF", last_name="P", club=self.away, position="Center Back")

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={"0": {"playerId": str(self.home_gk.id)}, "1": {"playerId": str(self.home_def.id)}},
            away_lineup={"0": {"playerId": str(self.away_gk.id)}, "1": {"playerId": str(self.away_def.id)}}
        )
        self.match.current_player_with_ball = self.home_gk
        self.match.current_zone = "GK"
        self.match.save()

    def test_pass_event_returned_for_special_counter(self):
        def choose_stub(team, zone, exclude_ids=None, match=None):
            if team == self.home:
                return self.home_def if zone == "DEF-C" else self.home_gk
            else:
                return self.away_gk if zone == "GK" else self.away_def

        with patch("matches.match_simulation.choose_player", side_effect=choose_stub):
            with patch("matches.match_simulation.random.random", side_effect=[0.99, 0.6]):
                result = simulate_one_action(self.match)

        self.assertEqual(result["event"]["event_type"], "pass")
        self.assertEqual(result["additional_event"]["event_type"], "counterattack")

class CounterPassAfterInterceptionTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="CP Home", is_bot=True, country=DEFAULT_COUNTRY)
        self.away = Club.objects.create(name="CP Away", is_bot=True, country=DEFAULT_COUNTRY)

        self.home_gk = Player.objects.create(first_name="HGK", last_name="P", club=self.home, position="Goalkeeper")
        self.home_def = Player.objects.create(first_name="HDEF", last_name="P", club=self.home, position="Right Back")
        self.home_dm = Player.objects.create(first_name="HDM", last_name="P", club=self.home, position="Defensive Midfielder")

        self.away_gk = Player.objects.create(first_name="AGK", last_name="P", club=self.away, position="Goalkeeper")
        self.away_def = Player.objects.create(first_name="ADEF", last_name="P", club=self.away, position="Center Back")
        self.away_fwd = Player.objects.create(first_name="AFWD", last_name="P", club=self.away, position="Center Forward")

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            status="in_progress",
            home_lineup={"0": {"playerId": str(self.home_gk.id)}, "1": {"playerId": str(self.home_def.id)}, "2": {"playerId": str(self.home_dm.id)}},
            away_lineup={"0": {"playerId": str(self.away_gk.id)}, "1": {"playerId": str(self.away_def.id)}, "2": {"playerId": str(self.away_fwd.id)}}
        )
        self.match.current_player_with_ball = self.home_def
        self.match.current_zone = "DEF-C"
        self.match.save()

    def test_counter_pass_created_when_no_long_shot(self):
        def choose_stub(team, zone, exclude_ids=None, match=None):
            if team == self.home:
                if zone == "DM-C":
                    return self.home_dm
                if zone == "DEF-C":
                    return self.home_def
                if zone == "GK":
                    return self.home_gk
                return self.home_dm
            else:
                if zone == "GK":
                    return self.away_gk
                if zone == "DEF-C":
                    return self.away_def
                if zone == "FWD-C":
                    return self.away_fwd
                return self.away_def

        with patch("matches.match_simulation.choose_player", side_effect=choose_stub):
            with patch("matches.match_simulation.random.random", side_effect=[0.99, 0.6, 0.1, 0.99]):
                result = simulate_one_action(self.match)

        self.assertEqual(result["action_type"], "counterattack")
        self.assertEqual(result["additional_event"]["event_type"], "counterattack")
        self.assertIn("second_additional_event", result)
        self.assertEqual(result["second_additional_event"]["event_type"], "pass")


class LongPassProbabilityTests(TestCase):
    def test_heading_affects_long_pass(self):
        club = Club.objects.create(name="LP", is_bot=True, country=DEFAULT_COUNTRY)
        opp = Club.objects.create(name="OPP", is_bot=True, country=DEFAULT_COUNTRY)

        passer = Player.objects.create(
            first_name="P",
            last_name="P",
            club=club,
            position="Central Midfielder",
            passing=80,
            vision=80,
        )
        recipient_good = Player.objects.create(
            first_name="R",
            last_name="H",
            club=club,
            position="Center Forward",
            heading=90,
            positioning=80,
        )
        opponent = Player.objects.create(
            first_name="O",
            last_name="O",
            club=opp,
            position="Center Back",
            marking=50,
            tackling=50,
        )
        prob_high = pass_success_probability(
            passer,
            recipient_good,
            opponent,
            from_zone="DM-C",
            to_zone="FWD-C",
            high=True,
            momentum=0,
        )

        recipient_bad = Player.objects.create(
            first_name="R2",
            last_name="L",
            club=club,
            position="Center Forward",
            heading=10,
            positioning=80,
        )
        prob_low = pass_success_probability(
            passer,
            recipient_bad,
            opponent,
            from_zone="DM-C",
            to_zone="FWD-C",
            high=True,
            momentum=0,
        )
        self.assertGreater(prob_high, prob_low)


class DribbleProbabilityTests(TestCase):
    def test_dribbling_attributes_affect_probability(self):
        club = Club.objects.create(name="DR", is_bot=True, country=DEFAULT_COUNTRY)
        opp = Club.objects.create(name="OP", is_bot=True, country=DEFAULT_COUNTRY)

        dribbler_good = Player.objects.create(
            first_name="D",
            last_name="G",
            club=club,
            position="Attacking Midfielder",
            dribbling=90,
            pace=85,
            flair=80,
            stamina=80,
            morale=80,
        )
        dribbler_bad = Player.objects.create(
            first_name="D",
            last_name="B",
            club=club,
            position="Attacking Midfielder",
            dribbling=30,
            pace=30,
            flair=20,
            stamina=80,
            morale=80,
        )
        defender = Player.objects.create(
            first_name="DEF",
            last_name="D",
            club=opp,
            position="Center Back",
            tackling=60,
            marking=60,
            strength=60,
        )

        from matches.match_simulation import dribble_success_probability

        prob_good = dribble_success_probability(dribbler_good, defender, momentum=0)
        prob_bad = dribble_success_probability(dribbler_bad, defender, momentum=0)
        self.assertGreater(prob_good, prob_bad)
