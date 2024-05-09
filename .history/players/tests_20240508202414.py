# players/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from clubs.models import Club
from players.models import Player

class PlayerTests(TestCase):
    def setUp(self):
        # Устанавливаем начальные данные
        self.club = Club.objects.create(name='Test Club', country='Test Country')
        self.client = Client()
        self.create_player_url = reverse('create_player', kwargs={'pk': self.club.pk})

    def test_generate_player(self):
        """Тест генерации нового игрока"""
        response = self.client.get(self.create_player_url, {'position': 'Midfielder'})

        # Проверяем перенаправление на страницу игрока
        self.assertEqual(response.status_code, 302)
        player = Player.objects.first()
        self.assertIsNotNone(player)
        self.assertEqual(player.position, 'Midfielder')
        self.assertEqual(player.club, self.club)

    def test_player_detail_page(self):
        """Тест страницы деталей игрока, включая отображение характеристик"""
        player = Player.objects.create(
            club=self.club,
            first_name='Test',
            last_name='Player',
            nationality='Test Country',
            age=18,
            position='Midfielder',
            strength=80,
            stamina=75,
            pace=70
        )
        detail_url = reverse('players:player_detail', args=[player.pk])
        response = self.client.get(detail_url)

        # Проверяем корректность отображения страницы деталей игрока
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, player.first_name)
        self.assertContains(response, player.last_name)
        self.assertContains(response, 'Strength: 80')
        self.assertContains(response, 'Stamina: 75')
        self.assertContains(response, 'Pace: 70')
