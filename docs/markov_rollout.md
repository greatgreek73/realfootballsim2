# Markov Rollout Checklist

Переход на марковскую симуляцию затрагивает данные матчей, поэтому перед деплоем
нужно подготовить существующие записи и договориться о статусах «живых» игр.

## 1. Миграции

```bash
python manage.py migrate matches 0016
```

Убедитесь, что поля `markov_seed`, `markov_token`, `markov_coefficients`,
`markov_last_summary` появились в таблице `matches_match`.

## 2. Инициализация матчей

Используйте утилиту `bootstrap_markov`, чтобы выставить seed/token для старых игр
и, при необходимости, вернуть матчи в стартовое состояние.

Примеры:

```bash
# Проставить seed = match.id для всех матчей, у которых ещё нет Markov-состояния
python manage.py bootstrap_markov --status finished

# Для активных (in_progress) матчей сбросить состояние и вернуть их в scheduled
# (например, чтобы пересоздать расписание уже на новом движке)
python manage.py bootstrap_markov --status in_progress --reset-status scheduled --overwrite

# Ограничиться парой матчей и посмотреть, что бы изменилось
python manage.py bootstrap_markov --match-ids 120 121 --dry-run
```

Команда:
- устанавливает `markov_seed = match.id` (или переопределяет при `--overwrite`);
- очищает `markov_token`, `markov_last_summary`, `markov_coefficients`;
- снимает `waiting_for_next_minute`;
- опционально переводит статус (`--reset-status`) и сбрасывает `current_minute`.

## 3. Очистка зависших матчей

Если до перехода оставались матчи со статусом `in_progress`, лучше перевести их в
`scheduled` (см. `--reset-status`) и заново прогнать генерацию расписания
(`tournaments.start_scheduled_matches`). Это гарантирует, что Celery возьмёт матч
с чистым Markov-token и корректно пройдёт все 90 минут.

## 4. Проверка

1. Запустите `tournaments.simulate_active_matches` и убедитесь в логах, что матчи
   получают `markov_seed` и minute_summary.
2. Откройте live-страницу клиента и проверьте, что события типа `goal`/`foul`
   появляются в ленте, а MarkovPanel показывает данные, поступающие по WebSocket.

После выполнения шагов Celery полностью управляет матчами через Markov-движок, а
фронтенд получает тот же поток данных без дополнительных HTTP-запросов.
