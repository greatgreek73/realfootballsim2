import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.api.password_reset import (
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetValidateTokenView,
)
from accounts.api.serializers import RegisterSerializer, UserSerializer
from accounts.api.views import (
    CustomTokenObtainPairSerializer,
    RegisterView,
    LogoutView,
    UserView,
)
from clubs.models import Club


pytestmark = pytest.mark.django_db


def _factory():
    return APIRequestFactory()


def test_password_reset_serializer_requires_existing_email():
    user_model = get_user_model()
    user_model.objects.create_user(
        username="reset-user",
        email="reset@example.com",
        password="StrongPass123!",
    )

    serializer = PasswordResetSerializer(data={"email": "reset@example.com"})
    assert serializer.is_valid()

    missing = PasswordResetSerializer(data={"email": "unknown@example.com"})
    with pytest.raises(serializers.ValidationError):
        missing.is_valid(raise_exception=True)


def test_password_reset_confirm_serializer_validates_token():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="confirm-user",
        email="confirm@example.com",
        password="StrongPass123!",
    )
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    serializer = PasswordResetConfirmSerializer(
        data={
            "uid": uid,
            "token": token,
            "new_password1": "NewPass123!",
            "new_password2": "NewPass123!",
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"] == user


def test_password_reset_confirm_serializer_rejects_invalid_data():
    serializer = PasswordResetConfirmSerializer(
        data={
            "uid": urlsafe_base64_encode(force_bytes(1)),
            "token": "irrelevant",
            "new_password1": "Mismatch123!",
            "new_password2": "Other123!",
        }
    )
    with pytest.raises(serializers.ValidationError):
        serializer.is_valid(raise_exception=True)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="support@example.com",
    ALLOWED_HOSTS=["testserver", "api.local"],
)
def test_password_reset_view_sends_email():
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="email-user",
        email="email-user@example.com",
        password="StrongPass123!",
    )

    mail.outbox.clear()
    request = factory.post(
        "/api/auth/password-reset/",
        {"email": user.email},
        format="json",
        HTTP_HOST="api.local",
    )
    response = PasswordResetView.as_view()(request)
    response.render()

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="support@example.com",
    DEBUG=True,
    ALLOWED_HOSTS=["testserver", "api.local"],
)
def test_password_reset_view_returns_reset_url_in_debug(monkeypatch):
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="email-fail-user",
        email="email-fail@example.com",
        password="StrongPass123!",
    )

    def failing_send_mail(*args, **kwargs):
        raise RuntimeError("SMTP is down")

    monkeypatch.setattr("accounts.api.password_reset.send_mail", failing_send_mail)

    request = factory.post(
        "/api/auth/password-reset/",
        {"email": user.email},
        format="json",
        HTTP_HOST="api.local",
    )
    response = PasswordResetView.as_view()(request)
    response.render()

    assert response.status_code == status.HTTP_200_OK
    assert "reset_url" in response.data


def test_password_reset_confirm_view_updates_password():
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="confirm-view-user",
        email="confirm-view@example.com",
        password="OldPass123!",
    )
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    request = factory.post(
        "/api/auth/password-reset-confirm/",
        {
            "uid": uid,
            "token": token,
            "new_password1": "NewPass123!",
            "new_password2": "NewPass123!",
        },
        format="json",
    )
    response = PasswordResetConfirmView.as_view()(request)
    response.render()

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NewPass123!")


def test_password_reset_validate_token_endpoint():
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="validate-user",
        email="validate@example.com",
        password="StrongPass123!",
    )
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    valid_request = factory.post(
        "/api/auth/password-reset-validate/",
        {"uid": uid, "token": token},
        format="json",
    )
    valid_response = PasswordResetValidateTokenView.as_view()(valid_request)
    valid_response.render()
    assert valid_response.status_code == status.HTTP_200_OK
    assert valid_response.data["valid"] is True
    assert valid_response.data["username"] == user.username

    invalid_request = factory.post(
        "/api/auth/password-reset-validate/",
        {"uid": uid, "token": "bad-token"},
        format="json",
    )
    invalid_response = PasswordResetValidateTokenView.as_view()(invalid_request)
    invalid_response.render()
    assert invalid_response.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_response.data["valid"] is False


def test_user_serializer_has_club_flag():
    user_model = get_user_model()
    without_club = user_model.objects.create_user(
        username="no-club",
        email="no-club@example.com",
        password="StrongPass123!",
    )
    assert UserSerializer(without_club).data["has_club"] is False

    with_club = user_model.objects.create_user(
        username="with-club",
        email="with-club@example.com",
        password="StrongPass123!",
    )
    Club.objects.create(name="Owned FC", country="GB", owner=with_club)
    assert UserSerializer(with_club).data["has_club"] is True


def test_register_serializer_rejects_duplicate_email():
    user_model = get_user_model()
    user_model.objects.create_user(
        username="existing",
        email="existing@example.com",
        password="StrongPass123!",
    )
    serializer = RegisterSerializer(
        data={
            "username": "new-user",
            "email": "existing@example.com",
            "password": "AnotherPass123!",
            "password2": "AnotherPass123!",
        }
    )
    assert serializer.is_valid() is False
    assert "email" in serializer.errors


def test_register_serializer_rejects_mismatched_passwords():
    serializer = RegisterSerializer(
        data={
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "StrongPass123!",
            "password2": "OtherPass123!",
        }
    )
    assert serializer.is_valid() is False
    assert "password2" in serializer.errors


def test_register_serializer_create_hashes_password():
    serializer = RegisterSerializer(
        data={
            "username": "create-user",
            "email": "create@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
    )
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.username == "create-user"
    assert user.check_password("StrongPass123!")


def test_token_serializer_accepts_email_and_returns_payload():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="login-user",
        email="login@example.com",
        password="StrongPass123!",
    )

    serializer = CustomTokenObtainPairSerializer(
        data={"username": user.email, "password": "StrongPass123!"}
    )
    assert serializer.is_valid(), serializer.errors
    tokens = serializer.validated_data
    assert "access" in tokens
    assert "refresh" in tokens
    assert tokens["user"]["email"] == user.email


def test_register_view_creates_user():
    factory = _factory()
    data = {
        "username": "register-view",
        "email": "register-view@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    request = factory.post("/api/auth/register/", data, format="json")
    response = RegisterView.as_view()(request)
    response.render()

    assert response.status_code == status.HTTP_201_CREATED
    user_model = get_user_model()
    assert user_model.objects.filter(username="register-view").exists()


def test_register_view_returns_errors_for_invalid_payload():
    factory = _factory()
    request = factory.post(
        "/api/auth/register/",
        {
            "username": "bad-register",
            "email": "bad-register@example.com",
            "password": "StrongPass123!",
            "password2": "Mismatch123!",
        },
        format="json",
    )
    response = RegisterView.as_view()(request)
    response.render()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password2" in response.data


def test_logout_view_handles_missing_invalid_and_valid_refresh(monkeypatch):
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="logout-user",
        email="logout@example.com",
        password="StrongPass123!",
    )
    view = LogoutView.as_view()

    request_missing = factory.post("/api/auth/logout/", {}, format="json")
    force_authenticate(request_missing, user=user)
    resp_missing = view(request_missing)
    resp_missing.render()
    assert resp_missing.status_code == status.HTTP_400_BAD_REQUEST

    request_invalid = factory.post(
        "/api/auth/logout/",
        {"refresh": "not-a-token"},
        format="json",
    )
    force_authenticate(request_invalid, user=user)
    resp_invalid = view(request_invalid)
    resp_invalid.render()
    assert resp_invalid.status_code == status.HTTP_400_BAD_REQUEST

    refresh = RefreshToken.for_user(user)

    blacklist_called = {"value": False}

    def fake_blacklist(self):
        blacklist_called["value"] = True

    monkeypatch.setattr("accounts.api.views.RefreshToken.blacklist", fake_blacklist, raising=False)

    request_valid = factory.post(
        "/api/auth/logout/",
        {"refresh": str(refresh)},
        format="json",
    )
    force_authenticate(request_valid, user=user)
    resp_valid = view(request_valid)
    resp_valid.render()
    assert resp_valid.status_code == status.HTTP_205_RESET_CONTENT
    assert blacklist_called["value"] is True


def test_user_view_returns_current_user_data():
    factory = _factory()
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="profile-user",
        email="profile@example.com",
        password="StrongPass123!",
    )
    request = factory.get("/api/auth/user/")
    force_authenticate(request, user=user)
    response = UserView.as_view()(request)
    response.render()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email
