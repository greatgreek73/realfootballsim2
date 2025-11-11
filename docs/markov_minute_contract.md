# Markov Minute ↔ Match Contract

> Цель: зафиксировать какие данные из ответа `simulate_markov_minute` мы сохраняем
> в `matches.models.Match` и связанные модели. Этот документ — справочник для
> разработчиков бэкенда/Celery и фронтенда, чтобы не держать контракт в голове.

## Основные структуры

- **Markov runtime** (`matches.engines.markov_runtime.simulate_markov_minute`) возвращает словарь:
  - `tick_seconds`, `regulation_minutes`, `spec_version` — мета‑инфа.
  - `minute_summary` — детализированная минута:
    ```json
    {
      "minute": 17,
      "end_state": "OPEN_PLAY_FINAL",
      "possession_end": "home",
      "zone_end": "FINAL",
      "score": {"home": 1, "away": 0},
      "score_total": {"home": 2, "away": 0},
      "counts": {"shot": 1, "foul": 0, "out": 0, "gk": 0},
      "entries_final": {"home": 3, "away": 1},
      "possession_seconds": {"home": 32, "away": 28},
      "swings": 2,
      "events": [...],
      "narrative": [...],
      "coefficients": {"attack": {...}, "defense": {...}},
      "token": {...}
    }
    ```

- **Match state**: дополнительные поля в `matches.models.Match`
  ```py
  markov_seed: BigIntegerField        # фиксированный seed конкретного матча
  markov_token: JSONField             # opaque токен для следующей минуты
  markov_coefficients: JSONField      # snapshot attack/defense на момент минуты
  markov_last_summary: JSONField      # хранит последний minute_summary как есть
  ```

## Маппинг minute_summary → Match

| minute_summary поле | Назначение | Поле модели / действие |
|---------------------|------------|-------------------------|
| `score_total.home` / `score_total.away` | Текущий счёт | `match.home_score`, `match.away_score` |
| `counts.shot`       | Количество ударов за минуту | `match.st_shoots += counts["shot"]` |
| `counts.foul`       | Количество фолов | `match.st_fouls += counts["foul"]` |
| Минуты владения     | Пока не агрегируются в отдельное поле, но остаются в `markov_last_summary` для аналитики/фронта |
| `possession_end`    | Кто владеет мячом к концу минуты (`"home"`, `"away"`, `None`) | `match.possession_indicator = 1/2/0` |
| `zone_end`          | Где находится мяч (`"DEF"`, `"MID"`, `"FINAL"`) | `match.current_zone` через маппинг `ZONE_HINT_TO_FIELD` (`DEF → DEF-C`, `MID → MID-C`, `FINAL → AM-C`) |
| `minute`            | Номер минуты, на которую отчитался движок | Используется для `match.current_minute`/`waiting_for_next_minute` и `MatchEvent.minute` |
| `token`             | Оpaque состояние цепи | `match.markov_token` для следующего вызова |
| `coefficients`      | Снапшоты коэффициентов | `match.markov_coefficients` (для отладки и возможного UI) |
| `narrative[]`       | Текстовые описания | Каждая строка превращается в `MatchEvent(event_type="info")`, чтобы фронт видел live-ленту |
| `events[]`          | Сырые переходы | Пока не сохраняем отдельно; храним в `markov_last_summary` и передаем на фронт через поле `markov_minute` в WS |

## Хранение токена / seed

- `markov_seed` по умолчанию = `match.id`, но может быть задран заранее (например, сценарием плей-офф). Важно **не** менять seed после старта, иначе минутные токены перестанут совпадать.
- `markov_token` всегда берётся из предыдущего `minute_summary["token"]`. Если токен `None`, движок начинает с `minute=1`, `state="KICKOFF"`.
- `markov_last_summary` хранит весь JSON последние минуты, чтобы:
  - повторно отправить его в websocket (например, после reconnect);
  - отдать через REST/графики;
  - проинспектировать при дебаге без повторного прогона.

## Использование на фронте

- WebSocket `match_update` теперь содержит `markov_minute` — это ровно `minute_summary`, который можно визуализировать (например, в `MarkovPanel`).
- `MatchEvent` с `event_type="info"` продолжают подпитывать существующий `EventMinutes.tsx`; этим достигается совместимость с прежним UI без тотального переписывания.

## Дальнейшие шаги

1. Научиться генерировать "богатые" события из `minute_summary["events"]` (shots/fouls/turnovers) и маппить их на типы `MatchEvent`. Пока это делаем текстовыми `info`, чтобы MVP работал.
2. Хранить агрегаты `possession_seconds`, `swings`, `entries_final` в статистических полях или отдельной модели, если понадобятся в UI/аналитике.

Документ нужно обновлять по мере эволюции контракта, чтобы frontend/backend не расходились.
