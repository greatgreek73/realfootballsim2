from datetime import date, datetime, timedelta

import pytest

from django.conf import settings
from django.utils import timezone

from tournaments import tasks as tournament_tasks
from tournaments.models import Season
from tournaments.tasks import (
    advance_match_minutes,
    complete_lineup,
    extract_player_ids_from_lineup,
    start_scheduled_matches,
)
from matches.models import Match


pytestmark = pytest.mark.django_db


def make_season(number: int, start: date, end: date, active: bool = True) -> Season:
    return Season.objects.create(
        number=number,
        name=f"Season {number}",
        start_date=start,
        end_date=end,
        is_active=active,
    )


def patch_time(monkeypatch, target_date: date):
    fixed_dt = datetime.combine(target_date, datetime.min.time())

    class FixedDatetime:
        @staticmethod
        def now():
            return fixed_dt

    monkeypatch.setattr(timezone, "now", lambda: fixed_dt)


def test_check_season_end_creates_new_season(monkeypatch):
    current = make_season(number=5, start=date(2025, 1, 1), end=date(2025, 1, 31))
    patch_time(monkeypatch, date(2025, 2, 10))

    commands_called = []

    def fake_call_command(name, *args, **kwargs):
        commands_called.append(name)
        if name == "create_new_season":
            latest = Season.objects.order_by("-number").first()
            next_number = (latest.number if latest else 0) + 1
            make_season(
                number=next_number,
                start=date(2025, 2, 1),
                end=date(2025, 2, 28),
                active=True,
            )

    monkeypatch.setattr("tournaments.tasks.call_command", fake_call_command)

    result = tournament_tasks.check_season_end.run()

    current.refresh_from_db()
    assert current.is_active is False
    assert Season.objects.filter(is_active=True).exclude(pk=current.pk).exists()
    assert "handle_season_transitions" in commands_called
    assert "create_new_season" in commands_called
    assert "Season 5 ended" in result


def test_check_season_end_skips_if_not_ready(monkeypatch):
    current = make_season(number=6, start=date(2025, 3, 1), end=date(2025, 3, 31))
    patch_time(monkeypatch, date(2025, 3, 10))

    def fake_call_command(*args, **kwargs):
        raise AssertionError("call_command should not be invoked")

    monkeypatch.setattr("tournaments.tasks.call_command", fake_call_command)

    result = tournament_tasks.check_season_end.run()
    current.refresh_from_db()
    assert current.is_active is True
    assert "still active" in result


def test_check_season_end_creates_initial_if_none(monkeypatch):
    Season.objects.all().delete()
    patch_time(monkeypatch, date(2025, 4, 5))

    def fake_call_command(name, *args, **kwargs):
        if name == "create_new_season":
            make_season(
                number=1,
                start=date(2025, 4, 1),
                end=date(2025, 4, 30),
                active=True,
            )

    monkeypatch.setattr("tournaments.tasks.call_command", fake_call_command)

    result = tournament_tasks.check_season_end.run()

    assert Season.objects.filter(is_active=True).count() == 1
    assert "created initial season" in result or "created initial" in result

def test_extract_player_ids_from_lineup_handles_values():
    lineup = {
        "0": {"playerId": "10"},
        "1": {"playerId": 20},
        "2": {"playerId": None},
    }
    assert extract_player_ids_from_lineup(lineup) == {10, 20}
    assert extract_player_ids_from_lineup("invalid") == set()


def test_complete_lineup_fills_missing_slots(monkeypatch, user_with_club, player_factory):
    _, club = user_with_club(username="lineup-complete", club_name="Auto Complete FC")
    positions = [
        "Goalkeeper",
        "Right Back",
        "Left Back",
        "Center Back",
        "Center Back",
        "Central Midfielder",
        "Central Midfielder",
        "Right Midfielder",
        "Left Midfielder",
        "Center Forward",
        "Center Forward",
        "Attacking Midfielder",
        "Defensive Midfielder",
    ]
    players = [player_factory(club, position=pos, idx=idx + 1) for idx, pos in enumerate(positions)]

    current_lineup = {
        "1": {"playerId": str(players[1].id), "playerPosition": players[1].position},
        "2": {"playerId": str(players[2].id), "playerPosition": players[2].position},
    }

    monkeypatch.setattr("tournaments.tasks.random.sample", lambda seq, k: list(seq)[:k])

    result = complete_lineup(club, current_lineup)
    assert result is not None
    assert len(result) == 11
    assert result["0"]["playerId"] == str(players[0].id)
    assert len({slot["playerId"] for slot in result.values()}) == 11


def test_complete_lineup_returns_none_when_insufficient_players(user_with_club, player_factory):
    _, club = user_with_club(username="lineup-short", club_name="Short Squad FC")
    for idx in range(9):
        player_factory(club, position="Center Back", idx=idx + 1)

    assert complete_lineup(club, {}) is None


def _create_players_with_prefix(club, positions, factory, prefix):
    return [
        factory(
            club,
            position=pos,
            idx=idx + 1,
            first_name=f"{prefix}{idx}_{club.id}_",
        )
        for idx, pos in enumerate(positions)
    ]


def _build_full_lineup(players):
    lineup = {}
    for idx in range(11):
        player = players[idx]
        lineup[str(idx)] = {
            "playerId": str(player.id),
            "playerPosition": player.position,
            "slotType": "manual",
            "slotLabel": f"SLOT_{idx}",
        }
    return lineup


def test_start_scheduled_matches_promotes_ready_match(user_with_club, player_factory):
    Match.objects.all().delete()
    home_user, home_club = user_with_club(username="start-home", club_name="Start FC")
    away_user, away_club = user_with_club(username="start-away", club_name="Visitors FC")

    positions = [
        "Goalkeeper",
        "Right Back",
        "Left Back",
        "Center Back",
        "Center Back",
        "Central Midfielder",
        "Central Midfielder",
        "Right Midfielder",
        "Left Midfielder",
        "Center Forward",
        "Center Forward",
    ]
    home_players = _create_players_with_prefix(home_club, positions, player_factory, "Home")
    away_players = _create_players_with_prefix(away_club, positions, player_factory, "Away")

    home_lineup = _build_full_lineup(home_players)
    away_lineup = _build_full_lineup(away_players)
    home_club.lineup = {"lineup": home_lineup, "tactic": "attacking"}
    home_club.save()
    away_club.lineup = {"lineup": away_lineup, "tactic": "defensive"}
    away_club.save()

    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now() - timedelta(minutes=5),
        status="scheduled",
    )

    result = start_scheduled_matches()

    match.refresh_from_db()
    assert "1 matches started" in result
    assert match.status == "in_progress"
    assert match.home_lineup == home_lineup
    assert match.away_lineup == away_lineup
    assert match.home_tactic == "attacking"
    assert match.away_tactic == "defensive"
    assert match.started_at is not None
    assert match.last_minute_update is not None
    assert match.waiting_for_next_minute is False


def test_start_scheduled_matches_skips_when_lineup_incomplete(user_with_club, player_factory):
    Match.objects.all().delete()
    home_user, home_club = user_with_club(username="start-home2", club_name="Start FC 2")
    away_user, away_club = user_with_club(username="start-away2", club_name="Visitors FC 2")

    for idx in range(9):
        player_factory(
            home_club,
            position="Center Back",
            idx=idx + 1,
            first_name=f"Incomplete{idx}_{home_club.id}_",
        )

    positions = [
        "Goalkeeper",
        "Center Back",
        "Center Back",
        "Center Back",
        "Center Back",
        "Central Midfielder",
        "Central Midfielder",
        "Right Midfielder",
        "Left Midfielder",
        "Center Forward",
        "Center Forward",
    ]
    away_players = _create_players_with_prefix(away_club, positions, player_factory, "Opp")
    away_club.lineup = {"lineup": _build_full_lineup(away_players), "tactic": "balanced"}
    away_club.save()

    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now() - timedelta(minutes=5),
        status="scheduled",
    )

    result = start_scheduled_matches()

    match.refresh_from_db()
    assert "0 matches started" in result and "1 skipped" in result
    assert match.status == "scheduled"
    assert match.home_lineup is None
    assert match.away_lineup is None


def test_advance_match_minutes_increments_when_ready(monkeypatch, user_with_club):
    settings.MATCH_MINUTE_REAL_SECONDS = 1

    home_user, home_club = user_with_club(username="advance-home", club_name="Advance Home")
    away_user, away_club = user_with_club(username="advance-away", club_name="Advance Away")
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="in_progress",
        current_minute=10,
        waiting_for_next_minute=True,
        last_minute_update=timezone.now() - timedelta(seconds=5),
        possession_indicator=1,
    )

    class DummyLayer:
        def __init__(self):
            self.messages = []

        async def group_send(self, group, message):
            self.messages.append((group, message))

    dummy_layer = DummyLayer()
    monkeypatch.setattr("channels.layers.get_channel_layer", lambda: dummy_layer)

    previous_update = match.last_minute_update
    result = advance_match_minutes()

    match.refresh_from_db()
    assert result == "Updated 1 matches"
    assert match.current_minute == 11
    assert match.waiting_for_next_minute is False
    assert match.last_minute_update == previous_update + timedelta(seconds=settings.MATCH_MINUTE_REAL_SECONDS)
    assert match.events.filter(event_type="info", minute=11).exists()
    assert dummy_layer.messages


def test_advance_match_minutes_no_matches_returns_message():
    Match.objects.all().delete()
    assert advance_match_minutes() == "No matches to update"
