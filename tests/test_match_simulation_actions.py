import random

import pytest
from django.utils import timezone

import matches.match_simulation as match_sim
from matches.match_simulation import (
    get_opponent_team,
    simulate_one_action,
)
from matches.models import Match
from tournaments import tasks as tournament_tasks


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def stub_personality(monkeypatch, settings):
    settings.USE_PERSONALITY_ENGINE = False

    monkeypatch.setattr(
        "matches.match_simulation.PersonalityDecisionEngine.choose_action_type",
        lambda *args, **kwargs: "pass",
    )
    monkeypatch.setattr(
        "matches.match_simulation.PersonalityDecisionEngine.should_attempt_risky_action",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "matches.match_simulation.PersonalityDecisionEngine.get_influencing_trait",
        lambda *args, **kwargs: (None, None),
    )
    monkeypatch.setattr(
        "matches.match_simulation.PersonalityModifier.get_pass_modifier",
        lambda *args, **kwargs: {"accuracy": 0.0, "preference": 0.0, "risk": 0.0},
    )
    monkeypatch.setattr(
        "matches.match_simulation.PersonalityModifier.get_shot_modifier",
        lambda *args, **kwargs: {"accuracy": 0.0},
    )
    monkeypatch.setattr(
        "matches.match_simulation.PersonalityModifier.get_foul_modifier",
        lambda *args, **kwargs: 0.0,
    )
    monkeypatch.setattr("matches.match_simulation.render_comment", lambda *a, **k: "comment")


@pytest.fixture
def prepared_match(user_with_club, player_factory):
    (home_user, home_club) = user_with_club(username="action-home", club_name="Action Home FC")
    (away_user, away_club) = user_with_club(username="action-away", club_name="Action Away FC")

    positions = [
        ("gk", "Goalkeeper"),
        ("rb", "Right Back"),
        ("cb1", "Center Back"),
        ("cb2", "Center Back"),
        ("lb", "Left Back"),
        ("cm1", "Central Midfielder"),
        ("cm2", "Central Midfielder"),
        ("am", "Attacking Midfielder"),
        ("rm", "Right Midfielder"),
        ("cf1", "Center Forward"),
        ("cf2", "Center Forward"),
    ]

    home_players = {}
    away_players = {}
    for idx, (key, pos) in enumerate(positions, start=1):
        home_players[key] = player_factory(home_club, position=pos, idx=idx)
        away_players[key] = player_factory(away_club, position=pos, idx=idx + 20)

    def lineup_dict(players):
        data = {}
        for index, player in enumerate(players.values()):
            data[str(index)] = {
                "playerId": str(player.id),
                "playerPosition": player.position,
            }
        return data

    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        datetime=timezone.now(),
        status="scheduled",
        current_zone="MID-C",
        st_shoots=0,
        st_passes=0,
        st_possessions=0,
        st_fouls=0,
        st_injury=0,
        possession_indicator=0,
    )
    match.home_lineup = lineup_dict(home_players)
    match.away_lineup = lineup_dict(away_players)
    match.home_tactic = "balanced"
    match.away_tactic = "balanced"
    match.save()

    return match, home_players, away_players


def set_deterministic_random(monkeypatch, sequence, randint_value=None):
    store = list(sequence)
    if not store:
        store = [0.0]
    iterator = iter(store)

    def next_value():
        try:
            return next(iterator)
        except StopIteration:
            return store[-1]

    monkeypatch.setattr(random, "random", next_value)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(random, "choices", lambda seq, weights, k: [seq[0]])
    if randint_value is None:
        monkeypatch.setattr(random, "randint", lambda a, b: a)
    else:
        monkeypatch.setattr(random, "randint", lambda a, b: randint_value)


def test_simulate_one_action_initializes_from_goalkeeper(
    prepared_match, monkeypatch
):
    match, home, _ = prepared_match
    match.current_player_with_ball = None
    match.current_zone = "MID-C"
    match.status = "in_progress"
    match.home_momentum = 0
    match.away_momentum = 0
    match.save()

    set_deterministic_random(monkeypatch, [0.99, 0.99, 0.99])
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 1.0)
    monkeypatch.setattr("matches.match_simulation.dribble_success_probability", lambda *a, **k: 0.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "pass"
    assert result["continue"] is True
    assert match.current_player_with_ball is not None
    assert match.current_zone != "GK"
    assert match.st_passes == 1
    assert match.st_possessions == 1
    assert match.possession_indicator == 1
    assert match.home_momentum == 1
    assert match.away_momentum == -1


def test_simulate_one_action_scores_goal(prepared_match, monkeypatch):
    match, home, away = prepared_match
    match.status = "in_progress"
    striker = home["cf1"]
    match.current_player_with_ball = striker
    match.current_zone = "FWD-C"
    match.home_score = 0
    match.away_score = 0
    match.save()

    set_deterministic_random(monkeypatch, [0.0])
    monkeypatch.setattr("matches.match_simulation.shot_success_probability", lambda *a, **k: 1.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "shot"
    assert result["continue"] is False
    assert match.home_score == 1
    assert match.away_score == 0
    assert match.current_zone == "GK"
    assert match.current_player_with_ball.position == "Goalkeeper"


def test_simulate_one_action_shot_miss_returns_possession_to_goalkeeper(
    prepared_match, monkeypatch
):
    match, home, away = prepared_match
    match.status = "in_progress"
    striker = home["cf2"]
    match.current_player_with_ball = striker
    match.current_zone = "FWD-C"
    match.home_score = 2
    match.away_score = 1
    match.save()

    set_deterministic_random(monkeypatch, [0.99])
    monkeypatch.setattr("matches.match_simulation.shot_success_probability", lambda *a, **k: 0.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "shot"
    assert result["continue"] is False
    assert match.home_score == 2
    assert match.away_score == 1
    assert match.current_player_with_ball.position == "Goalkeeper"
    assert match.current_zone == "GK"


def test_simulate_one_action_successful_pass_increments_possessions(
    prepared_match, monkeypatch
):
    match, home, away = prepared_match
    match.status = "in_progress"
    passer = home["cm1"]
    passer.dribbling = 30
    passer.save()
    match.current_player_with_ball = passer
    match.current_zone = "MID-C"
    match.st_passes = 0
    match.st_possessions = 0
    match.save()

    set_deterministic_random(monkeypatch, [0.99, 0.99])
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 1.0)
    monkeypatch.setattr("matches.match_simulation.foul_probability", lambda *a, **k: 0.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "pass"
    assert result["continue"] is True
    assert match.st_possessions == 1
    assert match.st_passes == 1


def test_simulate_one_action_interception_triggers_counterattack(
    prepared_match, monkeypatch
):
    match, home, away = prepared_match
    match.status = "in_progress"
    defender = home["cb1"]
    match.current_player_with_ball = defender
    match.current_zone = "DEF-C"
    match.save()

    set_deterministic_random(monkeypatch, [0.99, 0.99, 0.99])
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 0.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "counterattack"
    assert result["additional_event"]["event_type"] == "interception"
    assert match.current_player_with_ball is not None


def test_simulate_one_action_dribble_success_with_foul(
    prepared_match, monkeypatch
):
    match, home, away = prepared_match
    match.status = "in_progress"
    dribbler = home["cm1"]
    dribbler.dribbling = 90
    dribbler.pace = 85
    dribbler.save()
    match.current_player_with_ball = dribbler
    match.current_zone = "MID-C"
    match.save()

    set_deterministic_random(monkeypatch, [0.99, 0.0, 0.0, 0.0, 0.0])
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 0.6)
    monkeypatch.setattr("matches.match_simulation.dribble_success_probability", lambda *a, **k: 1.0)
    monkeypatch.setattr("matches.match_simulation.foul_probability", lambda *a, **k: 1.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "dribble"
    assert result["additional_event"]["event_type"] == "foul"
    assert result["continue"] is False
    assert match.st_fouls == 1


def test_simulate_one_action_no_recipient_returns_early(prepared_match, monkeypatch):
    match, home, away = prepared_match
    match.status = "in_progress"
    passer = home["cm2"]
    passer.dribbling = 30
    passer.save()
    match.current_player_with_ball = passer
    match.current_zone = "MID-C"
    match.st_possessions = 0
    match.save()

    original_choose = match_sim.choose_player

    def fake_choose(team, zone, **kwargs):
        if zone == "AM-C":
            return None
        return original_choose(team, zone, **kwargs)

    monkeypatch.setattr("matches.match_simulation.choose_player", fake_choose)
    monkeypatch.setattr("matches.match_simulation.foul_probability", lambda *a, **k: 0.0)
    set_deterministic_random(monkeypatch, [0.99])

    result = simulate_one_action(match)

    assert result["action_type"] == "no_recipient"
    assert result["continue"] is False
    assert match.st_possessions == 1
    assert match.st_passes == 0


def test_simulate_one_action_generates_long_pass(prepared_match, monkeypatch):
    match, home, away = prepared_match
    match.status = "in_progress"
    passer = home["cb2"]
    passer.dribbling = 30
    passer.save()
    match.current_player_with_ball = passer
    match.current_zone = "DEF-C"
    match.st_possessions = 0
    match.save()

    set_deterministic_random(monkeypatch, [0.0, 0.99], randint_value=3)
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 1.0)
    monkeypatch.setattr("matches.match_simulation.foul_probability", lambda *a, **k: 0.0)

    result = simulate_one_action(match)

    assert result["action_type"] == "pass"
    assert result["continue"] is True
    assert match.current_zone == "AM-C"
    assert match.st_possessions == 1


@pytest.mark.parametrize("is_goal,expected_away,expected_status", [(True, 1, "goal"), (False, 0, "shot_miss")])
def test_simulate_one_action_counterattack_long_shot(prepared_match, monkeypatch, is_goal, expected_away, expected_status):
    match, home, away = prepared_match
    match.status = "in_progress"
    defender = home["cb1"]
    defender.dribbling = 30
    defender.save()
    match.current_player_with_ball = defender
    match.current_zone = "DEF-C"
    match.home_score = 0
    match.away_score = 0
    match.save()

    set_deterministic_random(monkeypatch, [0.99, 0.0, 0.0])
    monkeypatch.setattr("matches.match_simulation.pass_success_probability", lambda *a, **k: 0.0)
    monkeypatch.setattr(
        "matches.match_simulation.long_shot_success_probability",
        lambda *a, **k: 1.0 if is_goal else 0.0,
    )

    result = simulate_one_action(match)

    assert result["action_type"] == "counterattack"
    assert result["continue"] is False
    if expected_away:
        assert match.away_score == expected_away
    else:
        assert match.away_score == 0
    assert match.home_score == 0
    shot_event = result.get("third_additional_event")
    assert shot_event is not None
    assert shot_event["event_type"] == expected_status
    assert match.st_shoots == 1
    assert match.current_player_with_ball.position == "Goalkeeper"
    assert match.current_zone == "GK"


def test_simulate_active_matches_smoke(prepared_match, monkeypatch):
    match, home, away = prepared_match
    match.status = "in_progress"
    match.current_player_with_ball = home["gk"]
    match.current_zone = "GK"
    match.waiting_for_next_minute = False
    match.started_at = timezone.now()
    match.last_minute_update = timezone.now()
    match.save()

    monkeypatch.setattr("channels.layers.get_channel_layer", lambda: None)
    monkeypatch.setattr(
        "matches.match_simulation.simulate_one_action",
        lambda match: {"continue": False, "action_type": "test"},
    )
    events = []
    monkeypatch.setattr(
        "matches.match_simulation.send_update",
        lambda match, team: events.append((match.id, team.id)),
    )

    result = tournament_tasks.simulate_active_matches.run()
    assert "Simulated actions" in result

    match.refresh_from_db()
    assert match.waiting_for_next_minute is True
    assert events


def test_get_opponent_team_returns_home_when_missing(prepared_match):
    match, home, away = prepared_match
    assert get_opponent_team(match, None) == match.home_team
