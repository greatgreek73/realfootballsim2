# accounts/api_views.py
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .forms import CustomUserCreationForm


@ensure_csrf_cookie
def csrf(request):
    # �⠢�� csrftoken cookie �� GET; �஭� ���⠥� ��� � ����� X-CSRFToken
    return JsonResponse({"detail": "ok"})


@require_POST
def signup_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}

    form = CustomUserCreationForm(data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse(
            {
                "detail": "ok",
                "user": {
                    "id": user.id,
                    "username": user.get_username(),
                    "email": user.email,
                },
            }
        )

    return JsonResponse(
        {"detail": "invalid", "errors": form.errors},
        status=400,
    )


@require_POST
def login_view(request):
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
    return JsonResponse(
        {"detail": "ok", "user": {"id": user.id, "username": user.get_username()}}
    )


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "ok"})


@require_GET
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)
    return JsonResponse(
        {
            "authenticated": True,
            "user": {"id": request.user.id, "username": request.user.get_username()},
        }
    )
