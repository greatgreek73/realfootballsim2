# accounts/api_urls.py
from django.urls import path
from .api_views import csrf_view, login_view, logout_view, me_view

urlpatterns = [
    path("csrf/",  csrf_view,  name="csrf"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("me/",    me_view,    name="me"),
]
