from django.urls import path
from .views import RegisterView, LoginView, RefreshView, LogoutView, UserView
from .password_reset import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetValidateTokenView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api_register"),
    path("login/", LoginView.as_view(), name="api_login"),
    path("refresh/", RefreshView.as_view(), name="api_refresh"),
    path("logout/", LogoutView.as_view(), name="api_logout"),
    path("user/", UserView.as_view(), name="api_user"),
    
    # Password reset endpoints
    path("password-reset/", PasswordResetView.as_view(), name="api_password_reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="api_password_reset_confirm"),
    path("password-reset-validate/", PasswordResetValidateTokenView.as_view(), name="api_password_reset_validate"),
]
