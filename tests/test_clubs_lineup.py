import json

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def build_lineup(players):
    lineup = {}
    for idx, player in enumerate(players):
        lineup[str(idx)] = {
            "playerId": str(player.id),
            "playerPosition": player.position,
            "slotType": "manual",
            "slotLabel": f"SLOT_{idx}",
        }
    return lineup


def test_save_team_lineup_persists_lineup(client, user_with_club, player_factory):
    user, club = user_with_club(username="lineup-owner", club_name="Lineup FC")

    # Create 11 players including goalkeeper
    players = [
        player_factory(club, position="Goalkeeper", idx=0),
        player_factory(club, position="Right Back", idx=1),
        player_factory(club, position="Left Back", idx=2),
        player_factory(club, position="Center Back", idx=3),
        player_factory(club, position="Center Back", idx=4),
        player_factory(club, position="Central Midfielder", idx=5),
        player_factory(club, position="Central Midfielder", idx=6),
        player_factory(club, position="Attacking Midfielder", idx=7),
        player_factory(club, position="Right Midfielder", idx=8),
        player_factory(club, position="Center Forward", idx=9),
        player_factory(club, position="Center Forward", idx=10),
    ]

    lineup = build_lineup(players)
    lineup["0"]["playerPosition"] = "Goalkeeper"

    client.force_login(user)
    url = reverse("clubs:save_team_lineup", args=[club.id])
    response = client.post(
        url,
        data=json.dumps({"lineup": lineup, "tactic": "balanced"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    club.refresh_from_db()
    assert club.lineup["tactic"] == "balanced"
    assert club.lineup["lineup"] == lineup


def test_save_team_lineup_rejects_more_than_eleven(client, user_with_club, player_factory):
    user, club = user_with_club(username="lineup-owner2", club_name="Lineup Eleven")
    players = [player_factory(club, idx=i, position="Center Back") for i in range(12)]
    lineup = build_lineup(players)
    lineup["0"]["playerPosition"] = "Goalkeeper"

    client.force_login(user)
    url = reverse("clubs:save_team_lineup", args=[club.id])
    response = client.post(
        url,
        data=json.dumps({"lineup": lineup}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "cannot have more than 11" in response.json()["error"]


def test_save_team_lineup_requires_goalkeeper(client, user_with_club, player_factory):
    user, club = user_with_club(username="lineup-owner3", club_name="No GK FC")
    players = [player_factory(club, idx=i, position="Center Back") for i in range(11)]
    lineup = build_lineup(players)
    # deliberately avoid goalkeeper string in position

    client.force_login(user)
    url = reverse("clubs:save_team_lineup", args=[club.id])
    response = client.post(
        url,
        data=json.dumps({"lineup": lineup}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "must include a goalkeeper" in response.json()["error"]


def test_save_team_lineup_rejects_foreign_player(client, user_with_club, player_factory):
    owner, club = user_with_club(username="lineup-owner4", club_name="Owner FC")
    other_user, other_club = user_with_club(username="other-owner", club_name="Other FC")

    gk = player_factory(club, position="Goalkeeper", idx=100)
    foreign_player = player_factory(other_club, position="Center Back", idx=200)
    extra_players = [player_factory(club, position="Center Back", idx=i) for i in range(10, 19)]
    lineup = build_lineup([gk, foreign_player] + extra_players)
    lineup["0"]["playerPosition"] = "Goalkeeper"

    client.force_login(owner)
    url = reverse("clubs:save_team_lineup", args=[club.id])
    response = client.post(
        url,
        data=json.dumps({"lineup": lineup}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "does not belong to club" in response.json()["error"]


def test_get_team_lineup_returns_players(client, user_with_club, player_factory):
    user, club = user_with_club(username="lineup-owner5", club_name="Get Lineup")
    players = [
        player_factory(club, position="Goalkeeper", idx=0),
        player_factory(club, position="Center Back", idx=1),
        player_factory(club, position="Center Back", idx=2),
        player_factory(club, position="Center Forward", idx=3),
        player_factory(club, position="Right Midfielder", idx=4),
        player_factory(club, position="Central Midfielder", idx=5),
        player_factory(club, position="Left Midfielder", idx=6),
        player_factory(club, position="Center Back", idx=7),
        player_factory(club, position="Right Back", idx=8),
        player_factory(club, position="Left Back", idx=9),
        player_factory(club, position="Center Forward", idx=10),
    ]
    lineup = build_lineup(players)
    lineup["0"]["playerPosition"] = "Goalkeeper"
    club.lineup = {"lineup": lineup, "tactic": "balanced"}
    club.save()

    client.force_login(user)
    url = reverse("clubs:get_team_lineup", args=[club.id])
    response = client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["tactic"] == "balanced"
    assert payload["lineup"] == lineup
    assert str(players[0].id) in payload["players"]
    assert payload["players"][str(players[0].id)]["position"] == "Goalkeeper"


def test_get_team_lineup_denies_foreign_user(client, user_with_club, player_factory):
    owner, club = user_with_club(username="lineup-owner6", club_name="Privacy FC")
    visitor, _ = user_with_club(username="visitor", club_name="Visitor FC")
    gk = player_factory(club, position="Goalkeeper", idx=0)
    club.lineup = {
        "lineup": {
            "0": {
                "playerId": str(gk.id),
                "playerPosition": "Goalkeeper",
                "slotType": "manual",
                "slotLabel": "GK",
            }
        },
        "tactic": "defensive",
    }
    club.save()

    client.force_login(visitor)
    url = reverse("clubs:get_team_lineup", args=[club.id])
    response = client.get(url)
    assert response.status_code == 403
