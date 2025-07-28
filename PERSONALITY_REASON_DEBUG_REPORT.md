# Отчет по отладке передачи personality_reason

## Проблема
Данные `personality_reason` не отображались в интерфейсе для live-матчей, хотя генерировались в `match_simulation.py`.

## Найденные проблемы

### 1. Неполная передача через WebSocket
В файле `tournaments/tasks.py` основное событие передавало `personality_reason`, но дополнительные события (`additional_event`, `second_additional_event`, `third_additional_event`) - нет.

**Исправлено:**
- Строка 161: Добавлено `"personality_reason": add_event.personality_reason,`
- Строка 202: Добавлено `"personality_reason": add_event2.personality_reason,`
- Строка 243: Добавлено `"personality_reason": add_event3.personality_reason,`

### 2. Правильная обработка в JavaScript
JavaScript код в `live_match.js` уже корректно обрабатывал `personality_reason` (строки 281-283).

### 3. Правильная обработка для завершенных матчей
- `views.py` корректно извлекает `personality_reason` (строка 105)
- Шаблон `match_detail.html` корректно отображает (строки 202-206)

## Полная цепочка передачи данных

1. **match_simulation.py** → Генерирует `personality_reason` в результате `simulate_one_action()`
2. **tournaments/tasks.py** → Создает `MatchEvent` и передает через WebSocket
3. **live_match.js** → Получает из WebSocket и добавляет в HTML
4. **match_detail.html** → Отображает для завершенных матчей через `enriched_events`

## Тестирование

Создано два скрипта для отладки:
1. `debug_personality_reason.py` - Детальная проверка каждого этапа
2. `test_personality_reason_chain.py` - Полная проверка всей цепочки

## Важное замечание

Для работы `personality_reason` необходимо убедиться, что в `settings.py` установлено:
```python
USE_PERSONALITY_ENGINE = True
```

## Результат
После внесенных изменений `personality_reason` будет корректно отображаться как для live-матчей (через WebSocket), так и для завершенных матчей (через серверный рендеринг).