import pytest
from django.utils import timezone
from django.test import Client

from players.models import Player


@pytest.mark.django_db
def test_player_detail_includes_last_trained_at():
    player = Player.objects.create(
        first_name="John",
        last_name="Doe",
        position="Goalkeeper",
        overall_rating=50,
        last_trained_at=timezone.now(),
    )

    client = Client()
    resp = client.get(f"/api/players/{player.id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("id") == player.id
    assert "last_trained_at" in data
    assert data["last_trained_at"] is not None
