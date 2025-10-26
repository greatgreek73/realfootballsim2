from datetime import date

import pytest
from django.core.exceptions import ValidationError

from tournaments import models as tournaments_models
from tournaments.models import Season


pytestmark = pytest.mark.django_db


def test_season_clean_requires_first_day_of_month():
    season = Season(
        number=1,
        name="Wrong start",
        start_date=date(2025, 2, 2),
        end_date=date(2025, 2, 28),
    )

    with pytest.raises(ValidationError) as excinfo:
        season.clean()

    assert "start_date" in excinfo.value.message_dict


def test_season_clean_requires_month_end():
    season = Season(
        number=2,
        name="Wrong end",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 30),
    )

    with pytest.raises(ValidationError) as excinfo:
        season.clean()

    assert "end_date" in excinfo.value.message_dict


def test_season_clean_passes_for_valid_dates():
    season = Season(
        number=3,
        name="Valid",
        start_date=date(2025, 4, 1),
        end_date=date(2025, 4, 30),
    )
    season.clean()  # should not raise


def test_season_february_helpers():
    february_season = Season(
        number=4,
        name="February",
        start_date=date(2025, 2, 1),
        end_date=date(2025, 2, 28),
    )
    march_season = Season(
        number=5,
        name="March",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 31),
    )

    assert february_season.is_february is True
    assert february_season.needs_double_matchday is True
    assert march_season.is_february is False
    assert march_season.needs_double_matchday is False


def test_season_get_double_matchday_dates_returns_expected_values():
    season = Season(
        number=6,
        name="Leap",
        start_date=date(2025, 2, 1),
        end_date=date(2025, 2, 28),
    )
    dates = season.get_double_matchday_dates()
    assert dates == [date(2025, 2, 15), date(2025, 2, 16)]

    non_february = Season(
        number=7,
        name="No double",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 31),
    )
    assert non_february.get_double_matchday_dates() == []


def test_season_save_assigns_name_if_missing():
    season = Season(
        number=8,
        name="",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 30),
    )
    season.save()
    assert season.name
    assert str(season.number) in season.name


def test_create_next_season_increments_number_and_uses_date_provider(monkeypatch):
    Season.objects.create(
        number=10,
        name="Season 10",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 31),
        is_active=True,
    )

    expected_start = date(2025, 11, 1)
    expected_end = date(2025, 11, 30)
    calls = {"count": 0}

    def fake_get_next_season_dates():
        calls["count"] += 1
        return expected_start, expected_end

    original_full_clean = Season.full_clean

    def fake_full_clean(self, *args, **kwargs):
        if not self.name:
            self.name = f"Season {self.number}"
        return original_full_clean(self, *args, **kwargs)

    monkeypatch.setattr(Season, "full_clean", fake_full_clean)
    monkeypatch.setattr(
        tournaments_models,
        "get_next_season_dates",
        fake_get_next_season_dates,
        raising=False,
    )

    new_season = Season.create_next_season()

    assert calls["count"] == 1
    assert new_season.number == 11
    assert new_season.start_date == expected_start
    assert new_season.end_date == expected_end
    assert new_season.is_active is True
    assert Season.objects.filter(number=11).exists()
