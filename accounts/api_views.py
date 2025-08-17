# accounts/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout

@ensure_csrf_cookie
def csrf(request):
    # Ставит csrftoken cookie при GET; фронт прочитает его и пошлёт X-CSRFToken
    return JsonResponse({"detail": "ok"})

@require_POST
def login_view(request):
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=400)
    login(request, user)
    return JsonResponse({"detail": "ok", "user": {"id": user.id, "username": user.get_username()}})

@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "ok"})

@require_GET
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)
    return JsonResponse({"authenticated": True, "user": {"id": request.user.id, "username": request.user.get_username()}})
