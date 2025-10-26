import io

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


pytestmark = pytest.mark.django_db


def test_create_test_user_creates_account():
    out = io.StringIO()
    call_command("create_test_user", stdout=out)

    user_model = get_user_model()
    user = user_model.objects.get(username="testuser")
    assert user.email == "test@example.com"
    assert user.tokens == 3000  # post_save signal assigns starter tokens
    assert user.money == 5000
    assert user.check_password("testpass123")
    assert "testuser" in out.getvalue()


def test_create_test_user_updates_existing_account():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="testuser",
        email="other@example.com",
        password="OldPass123!",
        tokens=5,
        money=10,
    )

    out = io.StringIO()
    call_command("create_test_user", stdout=out)

    user.refresh_from_db()
    assert user.email == "test@example.com"
    assert user.tokens == 100
    assert user.money == 5000
    assert user.check_password("testpass123")
    assert "testpass123" in out.getvalue()
