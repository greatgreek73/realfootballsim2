# CODEBASE MAP — карта проекта (черновик, дополняем по ходу)

## Корень
- backend: `realfootballsim/` (Django, ASGI)
- frontend: `frontend/` (Vite)
- docs: `docs/` (эта папка)

## Бэкенд (Django)
- ASGI: `realfootballsim/asgi.py`
- URLs: `realfootballsim/urls.py`
- Настройки: `realfootballsim/settings.py`
- Приложения: `matches/`, `players/`, `accounts/` (пример)
- Channels (WebSocket): ws-пути вида `/ws/...`
- Celery: фоновые задачи (worker/beat)

## Фронтенд (Vite)
- Конфиг: `frontend/vite.config.ts`
- Точка входа: `frontend/src/main.ts[x]` (или main.ts)
- API-обёртка: `frontend/src/api/http.ts` (axios)
- Дев-сервер: порт 5173, proxy на Django:8000
