import pytest
from django.utils import timezone

from matches.match_simulation import (
    apply_morale_change,
    apply_team_morale_effect,
    calculate_morale_change,
    decrease_morale,
    get_position_modifier,
    get_score_multiplier,
    get_team_momentum,
    get_time_multiplier,
    get_zone_multiplier,
    increase_morale,
    process_morale_event,
    recover_morale_gradually,
    update_momentum,
)
from matches.models import Match
from players.models import Player


pytestmark = pytest.mark.django_db


@pytest.fixture
def clubs_with_match(user_with_club):
    home_user, home_club = user_with_club(username="morale-home", club_name="Home Morale FC")
    away_user, away_club = user_with_club(username="morale-away", club_name="Away Morale FC")
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="scheduled",
        current_minute=70,
        current_zone="AM-C",
    )
    return home_club, away_club, match


def test_time_multiplier_ranges():
    assert get_time_multiplier(10) == 1.0
    assert get_time_multiplier(45) == 1.1
    assert get_time_multiplier(70) == 1.3
    assert get_time_multiplier(85) == 1.6
    assert get_time_multiplier(95) == 1.0


def test_score_multiplier_leading_and_trailing(clubs_with_match):
    home_club, away_club, match = clubs_with_match

    match.home_score = 2
    match.away_score = 1
    assert get_score_multiplier(match, home_club) == pytest.approx(0.9)
    assert get_score_multiplier(match, away_club) == pytest.approx(1.3)

    match.home_score = 3
    match.away_score = 0
    assert get_score_multiplier(match, home_club) == pytest.approx(0.8)
    assert get_score_multiplier(match, away_club) == pytest.approx(1.5)


def test_zone_and_position_modifiers():
    assert get_zone_multiplier("FWD-L") == pytest.approx(1.2)
    assert get_zone_multiplier("DM-C") == pytest.approx(1.0)
    assert get_zone_multiplier("UNKNOWN") == pytest.approx(1.0)

    assert get_position_modifier("Center Forward", "goal_scored") == pytest.approx(1.5)
    assert get_position_modifier("Goalkeeper", "goal_conceded") == pytest.approx(2.0)
    assert get_position_modifier("Central Midfielder", "nonexistent") == pytest.approx(1.0)


def test_calculate_morale_change_clamps_at_bounds(clubs_with_match, player_factory):
    home_club, away_club, match = clubs_with_match
    match.home_score = 0
    match.away_score = 1
    match.current_minute = 82
    match.current_zone = "FWD-C"

    striker = player_factory(
        home_club,
        position="Center Forward",
        morale=60,
        base_morale=55,
    )

    change = calculate_morale_change(striker, "goal_scored", match, zone="FWD-C")
    assert change == 15  # ограничено clamp_int

    neutral_change = calculate_morale_change(striker, "nonexistent_event", match)
    assert neutral_change == 0


def test_calculate_morale_change_negative_clamp(clubs_with_match, player_factory):
    home_club, away_club, match = clubs_with_match
    match.home_score = 0
    match.away_score = 3
    match.current_minute = 88
    match.current_zone = "GK"

    goalkeeper = player_factory(
        home_club,
        position="Goalkeeper",
        morale=70,
        base_morale=60,
    )

    change = calculate_morale_change(goalkeeper, "goal_conceded_gk", match, zone="GK")
    assert change == -15


def test_apply_and_process_morale_change(clubs_with_match, player_factory):
    home_club, _, match = clubs_with_match
    player = player_factory(home_club, morale=40, base_morale=50)

    apply_morale_change(player, 12)
    player.refresh_from_db()
    assert player.morale == 52

    process_morale_event(player, "shot_miss", match, zone="AM-C")
    player.refresh_from_db()
    assert player.morale < 52


def test_apply_team_morale_effect_updates_all_players(clubs_with_match, player_factory):
    home_club, away_club, match = clubs_with_match
    p1 = player_factory(home_club, morale=45, base_morale=50, position="Center Forward", idx=101)
    p2 = player_factory(home_club, morale=47, base_morale=55, position="Central Midfielder", idx=102)

    match.home_lineup = {
        "0": {"playerId": str(p1.id)},
        "1": {"playerId": str(p2.id)},
    }
    match.home_tactic = "balanced"

    apply_team_morale_effect(home_club, "goal_scored", match)

    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.morale > 45
    assert p2.morale > 47


def test_apply_team_morale_effect_handles_string_lineup(clubs_with_match, player_factory):
    home_club, _, match = clubs_with_match
    p1 = player_factory(home_club, morale=40, base_morale=45, idx=150)
    p2 = player_factory(home_club, morale=42, base_morale=46, idx=151)

    match.home_lineup = f"{p1.id},{p2.id}"

    apply_team_morale_effect(home_club, "successful_pass", match)

    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.morale >= 40
    assert p2.morale >= 42


def test_recover_morale_gradually_moves_towards_base(clubs_with_match, player_factory):
    home_club, _, match = clubs_with_match
    player_high = player_factory(home_club, morale=90, base_morale=60, idx=201)
    player_low = player_factory(home_club, morale=30, base_morale=55, idx=202)

    recover_morale_gradually(player_high)
    recover_morale_gradually(player_low)

    player_high.refresh_from_db()
    player_low.refresh_from_db()
    assert player_high.morale < 90
    # При возврате к базовому значению функция не должна уменьшать показатель
    assert player_low.morale >= 30


def test_decrease_and_increase_morale_helpers(clubs_with_match, player_factory):
    home_club, _, match = clubs_with_match
    player = player_factory(home_club, morale=60, base_morale=50, idx=301)

    decrease_morale(home_club, player, 5, match=match)
    player.refresh_from_db()
    assert player.morale == 55

    increase_morale(home_club, player, 10, match=match)
    player.refresh_from_db()
    assert player.morale == 65


def test_update_and_get_team_momentum(clubs_with_match):
    home_club, away_club, match = clubs_with_match

    update_momentum(match, home_club, 12)
    update_momentum(match, away_club, -8)

    assert get_team_momentum(match, home_club) == 12
    assert get_team_momentum(match, away_club) == -8

    match.home_momentum = 95
    update_momentum(match, home_club, 10)
    assert get_team_momentum(match, home_club) == 100
