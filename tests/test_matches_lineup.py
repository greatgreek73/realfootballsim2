import pytest
from django.utils import timezone

from matches.match_preparation import PreMatchPreparation
from matches.models import Match
from matches.utils import extract_player_id


pytestmark = pytest.mark.django_db


def create_team_squad(player_factory, club, prefix):
    players = {
        "gk": player_factory(club, position="Goalkeeper", idx=1, first_name=prefix),
        "rb": player_factory(club, position="Right Back", idx=2, first_name=prefix),
        "lb": player_factory(club, position="Left Back", idx=3, first_name=prefix),
        "cb1": player_factory(club, position="Center Back", idx=4, first_name=prefix),
        "cb2": player_factory(club, position="Center Back", idx=5, first_name=prefix),
        "cm1": player_factory(club, position="Central Midfielder", idx=6, first_name=prefix),
        "cm2": player_factory(club, position="Central Midfielder", idx=7, first_name=prefix),
        "rm": player_factory(club, position="Right Midfielder", idx=8, first_name=prefix),
        "lm": player_factory(club, position="Left Midfielder", idx=9, first_name=prefix),
        "cf1": player_factory(club, position="Center Forward", idx=10, first_name=prefix),
        "cf2": player_factory(club, position="Center Forward", idx=11, first_name=prefix),
    }
    return players


def make_match(user_with_club, player_factory):
    (home_user, home_club) = user_with_club(username="home-user", club_name="Home FC")
    (away_user, away_club) = user_with_club(username="away-user", club_name="Away FC")

    home_players = create_team_squad(player_factory, home_club, prefix="HPlayer")
    away_players = create_team_squad(player_factory, away_club, prefix="APlayer")

    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="scheduled",
    )
    return match, home_club, away_club, home_players, away_players


def test_get_lineup_from_club_returns_full_lineup(user_with_club, player_factory):
    match, home_club, away_club, home_players, _ = make_match(user_with_club, player_factory)

    lineup = {
        str(idx): {"playerId": str(player.id)} for idx, player in enumerate(home_players.values())
    }
    home_club.lineup = {"lineup": lineup, "tactic": "balanced"}
    home_club.save()

    prep = PreMatchPreparation(match)
    result = prep.get_lineup_from_club(home_club)
    assert result == lineup


def test_get_lineup_from_club_returns_none_for_invalid(user_with_club, player_factory):
    match, home_club, _, _, _ = make_match(user_with_club, player_factory)

    home_club.lineup = {"lineup": {"0": "123"}}
    home_club.save()
    prep = PreMatchPreparation(match)
    assert prep.get_lineup_from_club(home_club) is None

    home_club.lineup = {}
    home_club.save()
    assert prep.get_lineup_from_club(home_club) is None


def test_auto_select_lineup_produces_442(user_with_club, player_factory):
    match, home_club, _, home_players, _ = make_match(user_with_club, player_factory)
    prep = PreMatchPreparation(match)

    auto_lineup = prep.auto_select_lineup(home_club)

    assert len(auto_lineup) == 11
    assert str(home_players["gk"].id) == str(auto_lineup["0"])
    assert len({str(v) for v in auto_lineup.values()}) == len(auto_lineup)


def test_extract_player_id_handles_multiple_formats():
    assert extract_player_id({"playerId": 123}) == "123"
    assert extract_player_id("456") == "456"
    assert extract_player_id(789) == "789"
    assert extract_player_id({"wrong": "value"}) is None
