import pytest

from matches.utils import extract_player_id


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"playerId": "8012"}, "8012"),
        ({"playerId": 55}, "55"),
        ("1001", "1001"),
        (1002, "1002"),
    ],
)
def test_extract_player_id_supported_inputs(value, expected):
    assert extract_player_id(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        {"not": "here"},
        None,
        ["unexpected"],
    ],
)
def test_extract_player_id_handles_bad_data(value):
    assert extract_player_id(value) is None
