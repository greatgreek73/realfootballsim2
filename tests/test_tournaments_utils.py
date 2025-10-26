import collections
from datetime import date, datetime, time, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from clubs.models import Club
from matches.models import Match
from tournaments.models import Championship, League, Season
from tournaments.utils import (
    check_consecutive_matches,
    create_championship_matches,
    generate_league_schedule,
    get_team_matches,
    validate_championship_schedule,
    validate_schedule_balance,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def championship_factory():
    User = get_user_model()
    counter = {"value": 0}

    def _create(level: int = 1, start: date = date(2025, 1, 1), team_count: int = 16):
        counter["value"] += 1
        season_number = 5000 + counter["value"]
        season_name = f"Season {season_number}"
        country = "AX" if level == 1 else "BY"
        season = Season.objects.create(
            number=season_number,
            name=season_name,
            start_date=start,
            end_date=start + timedelta(days=30),
            is_active=True,
        )
        league = League.objects.create(
            name=f"League {season_number}",
            country=country,
            level=level,
            max_teams=16,
            foreign_players_limit=5,
        )
        championship = Championship.objects.create(
            season=season,
            league=league,
            start_date=start,
            end_date=start + timedelta(days=30),
            match_time=time(18, 0),
        )

        clubs = []
        for idx in range(team_count):
            owner = User.objects.create_user(
                username=f"champ-{level}-{counter['value']}-{idx}",
                email=f"champ-{level}-{counter['value']}-{idx}@example.com",
                password="StrongPass123!",
            )
            club = Club.objects.create(
                name=f"Club {season_number}-{idx}",
                country="GB",
                owner=owner,
            )
            championship.teams.add(club)
            clubs.append(club)

        return championship, clubs

    return _create


def test_check_consecutive_matches():
    team_a = "A"
    team_b = "B"
    schedule = [
        (1, 1, team_a, team_b),
        (2, 1, team_a, "C"),
        (3, 1, team_a, "D"),
        (4, 1, "E", team_a),
        (5, 1, "F", team_a),
    ]

    assert check_consecutive_matches(schedule, team=team_a, is_home=True) == 3
    assert check_consecutive_matches(schedule, team=team_a, is_home=False) == 2
    assert check_consecutive_matches(schedule, team=team_b, is_home=False) == 1


def test_get_team_matches_returns_sorted_rounds():
    schedule = [
        (3, 1, "A", "B"),
        (1, 1, "C", "A"),
        (2, 1, "D", "E"),
        (4, 1, "F", "A"),
    ]
    assert get_team_matches(schedule, "A") == [(1, False), (3, True), (4, False)]
    assert get_team_matches(schedule, "B") == [(3, False)]
    assert get_team_matches(schedule, "Z") == []


def test_validate_schedule_balance_counts_home_and_away():
    teams = ["A", "B", "C", "D"]
    schedule = [
        (1, 1, "A", "B"),
        (1, 2, "C", "D"),
        (2, 1, "B", "A"),
        (2, 2, "D", "C"),
    ]
    balance = validate_schedule_balance(schedule, teams)
    assert balance["A"] == {"home": 1, "away": 1}
    assert balance["B"] == {"home": 1, "away": 1}
    assert balance["C"] == {"home": 1, "away": 1}
    assert balance["D"] == {"home": 1, "away": 1}


def test_generate_league_schedule_requires_16_teams(championship_factory):
    championship, clubs = championship_factory(level=1)
    championship.teams.remove(clubs[-1])  # remove one team

    with pytest.raises(ValueError):
        generate_league_schedule(championship)


def test_generate_league_schedule_structure(championship_factory):
    championship, clubs = championship_factory(level=1)

    schedule = generate_league_schedule(championship)
    assert len(schedule) == 240  # 16 teams, double round robin

    matches_per_round = collections.Counter()
    pairings = collections.Counter()
    for round_num, day, home, away in schedule:
        matches_per_round[round_num] += 1
        pairings[(home, away)] += 1

    assert all(count == 8 for count in matches_per_round.values())
    assert all(count == 1 for count in pairings.values())

    balance = validate_schedule_balance(schedule, championship.teams.all())
    for stats in balance.values():
        assert stats["home"] == 15
        assert stats["away"] == 15


def test_create_championship_matches_and_cleanup(championship_factory):
    championship, _ = championship_factory(level=1)

    create_championship_matches(championship)
    assert championship.championshipmatch_set.count() == 240
    assert championship.championshipmatch_set.first().match.status == "scheduled"

    first_match = championship.championshipmatch_set.order_by("round").first().match
    first_local_time = timezone.localtime(first_match.datetime).time()
    assert first_local_time == championship.match_time

    unique_days = {
        cm.match.datetime.date() for cm in championship.championshipmatch_set.all()
    }
    assert len(unique_days) == 30  # 2*(n-1) rounds

    # Re-running should clean previous matches instead of duplicating
    create_championship_matches(championship)
    assert championship.championshipmatch_set.count() == 240


def test_create_championship_matches_adjusts_level_two_time(championship_factory):
    championship, _ = championship_factory(level=2)
    championship.match_time = time(20, 0)
    championship.save()

    create_championship_matches(championship)
    first_match = championship.championshipmatch_set.order_by("round").first().match
    local_time = timezone.localtime(first_match.datetime).time()
    assert local_time == time(18, 0)  # shifted two hours earlier


def test_validate_championship_schedule_success(championship_factory):
    championship, clubs = championship_factory(level=1, team_count=4)

    schedule = [
        [(0, 1), (2, 3)],
        [(1, 2), (3, 0)],
        [(0, 2), (1, 3)],
        [(2, 1), (0, 3)],
        [(3, 1), (2, 0)],
        [(1, 0), (3, 2)],
    ]

    base_date = championship.start_date
    round_number = 1
    for pairings in schedule:
        match_day = base_date + timedelta(days=round_number - 1)
        for home_idx, away_idx in pairings:
            home_team = clubs[home_idx]
            away_team = clubs[away_idx]
            dt = timezone.make_aware(datetime.combine(match_day, championship.match_time))
            match = Match.objects.create(
                home_team=home_team,
                away_team=away_team,
                datetime=dt,
                status="scheduled",
            )
            championship.championshipmatch_set.create(
                match=match,
                round=round_number,
                match_day=match_day.day,
            )
        round_number += 1

    assert validate_championship_schedule(championship) is True
    assert validate_championship_schedule(championship) is True


def test_validate_championship_schedule_missing_match(championship_factory):
    championship, _ = championship_factory(level=1)
    create_championship_matches(championship)

    championship.championshipmatch_set.first().delete()
    assert validate_championship_schedule(championship) is False


def test_validate_championship_schedule_detects_consecutive_home_streak(championship_factory):
    championship, clubs = championship_factory(level=1)
    create_championship_matches(championship)

    team = clubs[0]
    team_matches = (
        championship.championshipmatch_set.select_related("match")
        .filter(models.Q(match__home_team=team) | models.Q(match__away_team=team))
        .order_by("round")
    )

    for cm in team_matches[:3]:
        cm.match.home_team = team
        cm.match.save(update_fields=["home_team"])

    assert validate_championship_schedule(championship) is False
