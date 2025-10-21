# players/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser  # Импортируем пользовательскую модель
from clubs.models import Club
from players.models import Player
from players.training_logic import conduct_player_training
from players.training import TrainingSettings

class PlayerTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя с использованием CustomUser
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123')

        # Создаем тестовый клуб и назначаем пользователя владельцем
        self.club = Club.objects.create(name='Test Club', country='Test Country', owner=self.user)

        # Создаем клиента для тестирования запросов
        self.client = Client()
        self.client.login(username='testuser', password='password123')

        # URL для создания игрока
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

    def test_simple_player_training(self):
        """Проверяем базовую тренировку полевого игрока."""
        player = Player.objects.create(
            club=self.club,
            first_name='Train',
            last_name='Me',
            age=17,  # до возраста начала расцвета
            position='Central Midfielder'
        )

        result = conduct_player_training(player)

        # настройки тренировок должны быть созданы
        self.assertTrue(TrainingSettings.objects.filter(player=player).exists())

        # хотя бы одна характеристика должна измениться
        self.assertGreater(result['attributes_improved'], 0)
        self.assertTrue(result['changes'])
        for attr, (old, new) in result['changes'].items():
            self.assertEqual(getattr(player, attr), new)
            self.assertGreaterEqual(new, old)
