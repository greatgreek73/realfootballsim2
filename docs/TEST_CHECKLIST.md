# TEST CHECKLIST — ручные проверки (dev)

## Параллельные консоли
1) Бэкенд (ASGI):
   - Активировать venv
   - `python manage.py migrate`
   - `daphne realfootballsim.asgi:application -p 8000`
2) Celery worker (если нужен для сценария):
   - `celery -A realfootballsim worker -l info`
3) Фронт:
   - `cd frontend`
   - `npm i` (первый раз), затем `npm run dev` (порт 5173)

## Smoke-проверки
- Открыть http://127.0.0.1:5173/ — нет CORS-ошибок в консоли.
- Запросы `/api/...` уходят через proxy на :8000 и отвечают 2xx/4xx по логике API.
- Если есть WS: подключение к `ws://127.0.0.1:8000/ws/...` успешно, ошибок в браузерной консоли нет.

## Продакшн-сборка (когда дойдём)
- `npm run build` → артефакты в `frontend/dist`
- Бандл ссылается на ресурсы с префиксом `/static/front/`
