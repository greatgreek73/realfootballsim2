from datetime import date, datetime

import pytest

from django.utils import timezone

from tournaments import tasks as tournament_tasks
from tournaments.models import Season
from tournaments.tasks import complete_lineup, extract_player_ids_from_lineup


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
