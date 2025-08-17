# accounts/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path("csrf/", api_views.csrf, name="api-auth-csrf"),
    path("login/", api_views.login_view, name="api-auth-login"),
    path("logout/", api_views.logout_view, name="api-auth-logout"),
    path("me/", api_views.me, name="api-auth-me"),
]
