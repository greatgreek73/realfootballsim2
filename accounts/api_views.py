# accounts/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth import authenticate, login, logout

@ensure_csrf_cookie
@require_GET
def csrf_view(request):
    """
    Выдаёт CSRF-cookie (csrftoken). Тело ответа можно игнорировать.
    """
    from django.middleware.csrf import get_token
    return JsonResponse({"csrfToken": get_token(request)})

@csrf_protect
@require_POST
def login_view(request):
    """
    Логин по username/password. Создаёт сессию (как админка).
    Ожидает JSON: {"username": "...", "password": "..."}.
    """
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse({"detail": "username and password required"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=400)

    login(request, user)
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "authenticated": True,
    })

@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"ok": True})

@require_GET
def me_view(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"authenticated": False})
    return JsonResponse({
        "authenticated": True,
        "id": user.id,
        "username": user.username,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    })
