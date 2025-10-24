import pytest

from types import SimpleNamespace

from players.models import get_player_line


@pytest.mark.parametrize(
    "position, expected",
    [
        ("Goalkeeper", "GK"),
        ("Right Back", "DEF"),
        ("Left Back", "DEF"),
        ("Center Back", "DEF"),
        ("Defensive Midfielder", "DEF"),
        ("Right Midfielder", "MID"),
        ("Central Midfielder", "MID"),
        ("Left Midfielder", "MID"),
        ("Attacking Midfielder", "MID"),
        ("Center Forward", "FWD"),
        ("Shadow Forward", "FWD"),
        ("Unknown Role", "MID"),
    ],
)
def test_get_player_line(position, expected):
    player = SimpleNamespace(position=position)
    assert get_player_line(player) == expected
