# VITE NOTES — proxy и базовый путь

## Порты
- Vite dev: `5173`
- Django (ASGI): `8000`

## Proxy (dev)
- `/api` → `http://127.0.0.1:8000`
- `/admin` → `http://127.0.0.1:8000`
- `/static` → `http://127.0.0.1:8000`
- `/media` → `http://127.0.0.1:8000`
- `/ws` → `ws://127.0.0.1:8000` (ws: true)

## Base (prod build)
- На сборке `base = '/static/front/'`, чтобы Django/Nginx обслуживали из статики.
