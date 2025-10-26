import random

import pytest
from django.utils import timezone

from matches.match_simulation import (
    auto_select_lineup,
    choose_player,
    choose_player_from_zones,
    choose_players,
    ensure_match_lineup_set,
    send_update,
)
from matches.models import Match


pytestmark = pytest.mark.django_db


def _create_match(home_club, away_club):
    return Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="scheduled",
        current_zone="MID-C",
    )


def test_choose_player_handles_string_lineup(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="lineup-home")
    away_user, away_club = user_with_club(username="lineup-away")
    match = _create_match(home_club, away_club)

    players = [
        player_factory(home_club, position="Goalkeeper", idx=1),
        player_factory(home_club, position="Left Back", idx=2),
        player_factory(home_club, position="Center Back", idx=3),
        player_factory(home_club, position="Center Back", idx=4),
        player_factory(home_club, position="Right Back", idx=5),
        player_factory(home_club, position="Central Midfielder", idx=6),
        player_factory(home_club, position="Central Midfielder", idx=7),
        player_factory(home_club, position="Attacking Midfielder", idx=8),
        player_factory(home_club, position="Right Midfielder", idx=9),
        player_factory(home_club, position="Center Forward", idx=10),
        player_factory(home_club, position="Center Forward", idx=11),
    ]
    match.home_lineup = ",".join(str(p.id) for p in players)

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(random, "choices", lambda seq, weights, k: [seq[0]])

    selected = choose_player(home_club, "DEF-L", match=match)
    assert selected is not None
    assert selected.position == "Left Back"


def test_choose_player_falls_back_to_any_defender(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="fallback-home")
    away_user, away_club = user_with_club(username="fallback-away")
    match = _create_match(home_club, away_club)

    cb1 = player_factory(home_club, position="Center Back", idx=20)
    cb2 = player_factory(home_club, position="Center Back", idx=21)
    match.home_lineup = {
        "0": {"playerId": str(cb1.id)},
        "1": {"playerId": str(cb2.id)},
    }

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(random, "choices", lambda seq, weights, k: [seq[0]])

    selected = choose_player(home_club, "DEF-L", match=match)
    assert selected in {cb1, cb2}
    assert selected.position == "Center Back"


def test_choose_player_uses_positioning_weights(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="weights-home")
    away_user, away_club = user_with_club(username="weights-away")
    match = _create_match(home_club, away_club)

    low_pos = player_factory(home_club, position="Center Back", positioning=10, idx=30)
    high_pos = player_factory(home_club, position="Center Back", positioning=70, idx=31)
    match.home_lineup = {
        "0": {"playerId": str(low_pos.id)},
        "1": {"playerId": str(high_pos.id)},
    }

    captured = {}

    def fake_choices(seq, weights, k):
        captured["weights"] = tuple(weights)
        return [seq[0]]

    monkeypatch.setattr(random, "choices", fake_choices)
    monkeypatch.setattr(random, "choice", lambda seq: pytest.fail("random.choice should not be used"))

    choose_player(home_club, "DEF-C", match=match)
    assert captured["weights"] == (low_pos.positioning, high_pos.positioning)


def test_choose_players_respects_exclude(user_with_club, player_factory):
    _, club = user_with_club(username="choose-players")
    d1 = player_factory(club, position="Center Back", idx=40)
    d2 = player_factory(club, position="Center Back", idx=41)
    players = choose_players(club, "DEF", exclude_ids={d1.id})
    assert d1 not in players
    assert d2 in players


def test_choose_player_from_zones_tries_in_order(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="zones-home")
    away_user, away_club = user_with_club(username="zones-away")
    match = _create_match(home_club, away_club)
    forward = player_factory(home_club, position="Center Forward", idx=50)
    defender = player_factory(home_club, position="Center Back", idx=51)

    match.home_lineup = {
        "0": {"playerId": str(forward.id)},
        "1": {"playerId": str(defender.id)},
    }

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(random, "choices", lambda seq, weights, k: [seq[0]])

    player, zone_used = choose_player_from_zones(
        home_club,
        ["FWD-C", "DEF-C"],
        exclude_ids=set(),
        match=match,
    )
    assert player == forward
    assert zone_used == "FWD-C"


def test_ensure_match_lineup_set_uses_club_lineup(user_with_club, player_factory):
    home_user, home_club = user_with_club(username="ensure-home")
    away_user, away_club = user_with_club(username="ensure-away")
    match = _create_match(home_club, away_club)

    players = [player_factory(home_club, position="Center Back", idx=60 + i) for i in range(11)]
    full_lineup = {str(i): {"playerId": str(players[i].id)} for i in range(11)}
    home_club.lineup = {"lineup": full_lineup, "tactic": "attacking"}
    home_club.save()

    success = ensure_match_lineup_set(match, for_home=True)
    assert success is True
    assert match.home_lineup == full_lineup
    assert match.home_tactic == "attacking"


def test_ensure_match_lineup_set_completes_missing(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="ensure-missing-home")
    away_user, away_club = user_with_club(username="ensure-missing-away")
    match = _create_match(home_club, away_club)

    players = [player_factory(home_club, position="Center Back", idx=80 + i) for i in range(11)]
    partial_lineup = {"0": {"playerId": str(players[0].id)}}
    home_club.lineup = {"lineup": partial_lineup, "tactic": "balanced"}
    home_club.save()

    completed = {str(i): {"playerId": str(players[i].id)} for i in range(11)}
    calls = []

    def fake_complete(team, current):
        calls.append((team, current))
        return completed

    import tournaments.tasks as tournament_tasks

    monkeypatch.setattr(tournament_tasks, "complete_lineup", fake_complete)

    success = ensure_match_lineup_set(match, for_home=True)
    assert success is True
    assert match.home_lineup == completed
    assert match.home_tactic == "balanced"
    assert calls and calls[0][0] == home_club


def test_auto_select_lineup_wraps_complete_lineup(user_with_club, player_factory, monkeypatch):
    _, club = user_with_club(username="auto-select")
    players = [player_factory(club, position="Central Midfielder", idx=120 + i) for i in range(11)]
    completed = {str(i): {"playerId": str(players[i].id)} for i in range(11)}

    import tournaments.tasks as tournament_tasks

    monkeypatch.setattr(tournament_tasks, "complete_lineup", lambda team, current: completed)

    result = auto_select_lineup(club)
    assert result is not None
    assert result["lineup"] == completed
    assert result["tactic"] == "balanced"


def test_send_update_emits_payload(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="send-home")
    away_user, away_club = user_with_club(username="send-away")
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="in_progress",
        current_zone="MID-C",
        current_minute=25,
        home_score=1,
        away_score=0,
        st_shoots=3,
        st_passes=8,
        st_possessions=12,
        st_fouls=1,
        st_injury=0,
        home_momentum=15,
        away_momentum=-10,
    )

    current_player = player_factory(home_club, first_name="John", idx=300)
    match.current_player_with_ball = current_player

    class DummyLayer:
        def __init__(self):
            self.sent = []

        async def group_send(self, group, message):
            self.sent.append((group, message))

    dummy_layer = DummyLayer()
    monkeypatch.setattr(
        "matches.match_simulation.get_channel_layer",
        lambda: dummy_layer,
    )

    send_update(match, home_club)

    assert dummy_layer.sent, "group_send was not invoked"
    group, payload = dummy_layer.sent[0]
    assert group == f"match_{match.id}"
    assert payload["type"] == "match_update"
    data = payload["data"]
    assert data["match_id"] == match.id
    assert data["st_possessions"] == match.st_possessions
    assert data["current_player"]["id"] == current_player.id
    assert data["current_player"]["first_name"] == current_player.first_name
    assert data["possessing_team_id"] == home_club.id
    assert "events" not in data


def test_send_update_gracefully_handles_missing_channel_layer(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="send-none")
    away_user, away_club = user_with_club(username="send-none-away")
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="in_progress",
        current_zone="MID-C",
        current_minute=10,
        st_possessions=2,
    )

    current_player = player_factory(home_club, idx=400)
    match.current_player_with_ball = current_player

    monkeypatch.setattr("matches.match_simulation.get_channel_layer", lambda: None)

    # Should not raise, even without channel layer
    send_update(match, home_club)


def test_ensure_match_lineup_set_returns_false_on_completion_failure(user_with_club, player_factory, monkeypatch):
    home_user, home_club = user_with_club(username="ensure-fail-home")
    away_user, away_club = user_with_club(username="ensure-fail-away")
    match = _create_match(home_club, away_club)

    partial_lineup = {"0": {"playerId": "123"}}
    home_club.lineup = {"lineup": partial_lineup, "tactic": "balanced"}
    home_club.save()

    import tournaments.tasks as tournament_tasks

    monkeypatch.setattr(tournament_tasks, "complete_lineup", lambda *args, **kwargs: None)

    success = ensure_match_lineup_set(match, for_home=True)
    assert success is False
    assert match.home_lineup is None


@pytest.mark.parametrize(
    "exception_cls",
    [ImportError, RuntimeError],
)
def test_auto_select_lineup_handles_completion_errors(user_with_club, exception_cls, monkeypatch):
    _, club = user_with_club(username=f"auto-fail-{exception_cls.__name__}")

    import tournaments.tasks as tournament_tasks

    def broken_complete(*args, **kwargs):
        raise exception_cls("boom")

    monkeypatch.setattr(tournament_tasks, "complete_lineup", broken_complete)

    assert auto_select_lineup(club) is None
