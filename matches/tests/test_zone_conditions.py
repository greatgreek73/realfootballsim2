from django.test import TestCase

from clubs.models import Club
from players.models import Player
from matches.match_simulation import zone_conditions

DEFAULT_COUNTRY = "RU"
DEFAULT_NATIONALITY = "RU"

class AMZoneConditionsTest(TestCase):
    def test_am_zone_excludes_strikers(self):
        club = Club.objects.create(name="ZC", is_bot=True, country=DEFAULT_COUNTRY)
        am = Player.objects.create(first_name="A", last_name="M", club=club, position="Attacking Midfielder", nationality=DEFAULT_NATIONALITY)
        st = Player.objects.create(first_name="S", last_name="T", club=club, position="Center Forward", nationality=DEFAULT_NATIONALITY)

        cond = zone_conditions("AM-C")
        self.assertTrue(cond(am))
        self.assertFalse(cond(st))
