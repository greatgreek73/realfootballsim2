import datetime

import pytest
import pytz
from django.utils import timezone

from players.tasks import is_training_day


@pytest.mark.parametrize(
    "weekday, expected",
    [
        (0, True),   # Monday
        (2, True),   # Wednesday
        (4, True),   # Friday
        (1, False),  # Tuesday
        (5, False),  # Saturday
        (6, False),  # Sunday
    ],
)
def test_is_training_day(monkeypatch, weekday, expected):
    cet = pytz.timezone("CET")
    base = datetime.datetime(2025, 1, 6)  # Monday
    target = base + datetime.timedelta(days=weekday)
    aware_dt = cet.localize(datetime.datetime.combine(target, datetime.time(12, 0)))

    monkeypatch.setattr(timezone, "now", lambda: aware_dt)

    assert is_training_day() is expected
