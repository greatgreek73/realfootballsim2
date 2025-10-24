import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.urls import reverse

from clubs.models import Club
from tournaments.models import League


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_signup_creates_user_with_email():
    client = Client()
    user_model = get_user_model()

    username = "signup_case_user"
    email = "signup_case_user@example.com"

    user_model.objects.filter(username=username).delete()

    response = client.post(
        reverse("signup"),
        {
            "username": username,
            "email": email,
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        },
        follow=True,
    )

    assert response.status_code == 200
    created_user = user_model.objects.get(username=username)
    assert created_user.email == email
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_api_signup_creates_user_via_json():
    client = Client()
    user_model = get_user_model()

    username = "signup_api_user"
    email = "signup_api_user@example.com"

    user_model.objects.filter(username=username).delete()

    client.get("/api/auth/csrf/")
    csrftoken = client.cookies.get("csrftoken")
    token_value = csrftoken.value if csrftoken else ""

    response = client.post(
        "/api/auth/signup/",
        data=json.dumps(
            {
                "username": username,
                "email": email,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        ),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token_value,
    )

    assert response.status_code == 200
    created_user = user_model.objects.get(username=username)
    assert created_user.email == email
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_api_create_club_generates_club():
    client = Client()
    user = get_user_model().objects.create_user(
        username="club_creator", email="club@example.com", password="StrongPass123!"
    )
    client.force_login(user)

    League.objects.create(name="Test League", country="GB", level=1)

    response = client.post(
        "/api/clubs/create/",
        data=json.dumps({"name": "Test FC", "country": "GB"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    club = Club.objects.get(owner=user)
    assert club.name == "Test FC"
    assert club.player_set.count() == 16
