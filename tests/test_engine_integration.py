import pytest
from matches.match_simulation import simulate_one_action

@pytest.mark.django_db
def test_simulate_one_action_changes_state(match_with_lineups):
    match = match_with_lineups

    # фиксируем исходные данные
    score_before = (match.home_score, match.away_score) \
                   if hasattr(match, "home_score") else (None, None)
    zone_before = getattr(match, "ball_zone", None)

    # вызываем один тик симуляции
    result = simulate_one_action(match)
    match.refresh_from_db()

    # 1. Функция должна вернуть dict с ключом "event" (пример)
    assert isinstance(result, dict)
    assert "event" in result

    # 2. После тика либо счёт, либо зона мяча, либо оба — должны измениться
    score_after = (match.home_score, match.away_score) \
                  if hasattr(match, "home_score") else (None, None)
    zone_after = getattr(match, "ball_zone", None)

    assert (score_after != score_before) or (zone_after != zone_before)
