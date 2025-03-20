from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clubs.models import Club
from players.models import Player
from tournaments.models import Season, League
from transfers.models import TransferListing, TransferOffer, TransferHistory
from django_countries.fields import Country

User = get_user_model()

class TransferSystemTestCase(TestCase):
    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            tokens=1000
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123',
            tokens=1000
        )
        
        # Создаем сезон
        self.season = Season.objects.create(
            number=1,
            name='Season 1',
            start_date='2025-01-01',
            end_date='2025-01-31',
            is_active=True
        )
        
        # Создаем лиги
        self.league = League.objects.create(
            name='Premier League',
            country='GB',
            level=1,
            max_teams=16
        )
        
        # Создаем клубы
        self.club1 = Club.objects.create(
            name='Club 1',
            country='GB',
            owner=self.user1,
            league=self.league
        )
        self.club2 = Club.objects.create(
            name='Club 2',
            country='GB',
            owner=self.user2,
            league=self.league
        )
        
        # Создаем игроков
        self.player1 = Player.objects.create(
            first_name='John',
            last_name='Doe',
            age=25,
            club=self.club1,
            nationality='GB',
            position='Goalkeeper',
            player_class=2,
            strength=70,
            stamina=75,
            pace=65,
            positioning=80,
            reflexes=85,
            handling=80
        )
        self.player2 = Player.objects.create(
            first_name='Jane',
            last_name='Smith',
            age=23,
            club=self.club1,
            nationality='GB',
            position='Center Forward',
            player_class=2,
            strength=75,
            stamina=80,
            pace=85,
            positioning=75,
            finishing=85,
            heading=75
        )
        
        # Создаем клиент для тестирования
        self.client = Client()
    
    def test_create_transfer_listing(self):
        """Тест создания трансферного листинга"""
        # Авторизуемся как владелец клуба 1
        self.client.login(username='user1', password='password123')
        
        # Создаем трансферный листинг
        response = self.client.post(reverse('transfers:create_transfer_listing'), {
            'player': self.player1.id,
            'asking_price': 500,
            'description': 'Great goalkeeper'
        })
        
        # Проверяем, что листинг создан и перенаправление работает
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfers:club_transfers'))
        
        # Проверяем, что листинг существует в базе данных
        listing = TransferListing.objects.filter(player=self.player1).first()
        self.assertIsNotNone(listing)
        self.assertEqual(listing.asking_price, 500)
        self.assertEqual(listing.description, 'Great goalkeeper')
        self.assertEqual(listing.status, 'active')
    
    def test_make_transfer_offer(self):
        """Тест создания предложения по трансферу"""
        # Создаем трансферный листинг
        listing = TransferListing.objects.create(
            player=self.player1,
            club=self.club1,
            asking_price=500,
            description='Great goalkeeper',
            status='active'
        )
        
        # Авторизуемся как владелец клуба 2
        self.client.login(username='user2', password='password123')
        
        # Создаем предложение по трансферу
        response = self.client.post(reverse('transfers:transfer_listing_detail', args=[listing.id]), {
            'bid_amount': 600,
            'message': 'Interested in this player'
        })
        
        # Проверяем, что предложение создано и перенаправление работает
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfers:transfer_listing_detail', args=[listing.id]))
        
        # Проверяем, что предложение существует в базе данных
        offer = TransferOffer.objects.filter(transfer_listing=listing, bidding_club=self.club2).first()
        self.assertIsNotNone(offer)
        self.assertEqual(offer.bid_amount, 600)
        self.assertEqual(offer.message, 'Interested in this player')
        self.assertEqual(offer.status, 'pending')
    
    def test_accept_transfer_offer(self):
        """Тест принятия предложения по трансферу"""
        # Создаем трансферный листинг
        listing = TransferListing.objects.create(
            player=self.player1,
            club=self.club1,
            asking_price=500,
            description='Great goalkeeper',
            status='active'
        )
        
        # Создаем предложение по трансферу
        offer = TransferOffer.objects.create(
            transfer_listing=listing,
            bidding_club=self.club2,
            bid_amount=600,
            message='Interested in this player',
            status='pending'
        )
        
        # Запоминаем начальные балансы токенов
        initial_user1_tokens = self.user1.tokens
        initial_user2_tokens = self.user2.tokens
        
        # Авторизуемся как владелец клуба 1
        self.client.login(username='user1', password='password123')
        
        # Принимаем предложение
        response = self.client.get(reverse('transfers:accept_transfer_offer', args=[offer.id]))
        
        # Проверяем, что предложение принято и перенаправление работает
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfers:club_transfers'))
        
        # Обновляем объекты из базы данных
        listing.refresh_from_db()
        offer.refresh_from_db()
        self.player1.refresh_from_db()
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        
        # Проверяем, что статусы обновлены
        self.assertEqual(listing.status, 'completed')
        self.assertEqual(offer.status, 'accepted')
        
        # Проверяем, что игрок перешел в новый клуб
        self.assertEqual(self.player1.club, self.club2)
        
        # Проверяем, что токены переведены
        self.assertEqual(self.user1.tokens, initial_user1_tokens + 600)
        self.assertEqual(self.user2.tokens, initial_user2_tokens - 600)
        
        # Проверяем, что создана запись в истории трансферов
        history = TransferHistory.objects.filter(player=self.player1).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.from_club, self.club1)
        self.assertEqual(history.to_club, self.club2)
        self.assertEqual(history.transfer_fee, 600)
    
    def test_cancel_transfer_listing(self):
        """Тест отмены трансферного листинга"""
        # Создаем трансферный листинг
        listing = TransferListing.objects.create(
            player=self.player1,
            club=self.club1,
            asking_price=500,
            description='Great goalkeeper',
            status='active'
        )
        
        # Создаем предложение по трансферу
        offer = TransferOffer.objects.create(
            transfer_listing=listing,
            bidding_club=self.club2,
            bid_amount=600,
            message='Interested in this player',
            status='pending'
        )
        
        # Авторизуемся как владелец клуба 1
        self.client.login(username='user1', password='password123')
        
        # Отменяем листинг
        response = self.client.get(reverse('transfers:cancel_transfer_listing', args=[listing.id]))
        
        # Проверяем, что листинг отменен и перенаправление работает
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfers:club_transfers'))
        
        # Обновляем объекты из базы данных
        listing.refresh_from_db()
        offer.refresh_from_db()
        
        # Проверяем, что статусы обновлены
        self.assertEqual(listing.status, 'cancelled')
        self.assertEqual(offer.status, 'cancelled')
