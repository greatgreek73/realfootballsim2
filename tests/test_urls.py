from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tournaments.models import Championship, League, Season
from django_countries.fields import Country
from datetime import date

User = get_user_model()


class URLTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_reverse_core_home(self):
        """Test that reverse('core:home') works and returns '/'"""
        url = reverse('core:home')
        self.assertEqual(url, '/')
        
    def test_home_page_renders(self):
        """Test that GET / doesn't crash"""
        # Create test data
        season = Season.objects.create(
            number=1,
            name="Test Season",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            is_active=True
        )
        
        league = League.objects.create(
            name="Test League",
            country=Country('GB'),
            level=1,
            max_teams=16
        )
        
        championship = Championship.objects.create(
            season=season,
            league=league,
            status='in_progress',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_login_redirect(self):
        """Test that after login redirects to core:home"""
        User.objects.create_user(username='testuser', password='testpass123')
        
        response = self.client.post('/auth/sign-in/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        
        # Check that we're redirected to home after login
        self.assertRedirects(response, reverse('core:home'))
        
    def test_protected_page_redirect(self):
        """Test that protected pages redirect to login"""
        response = self.client.get('/home/sub/')
        expected_url = '/auth/sign-in/?next=/home/sub/'
        self.assertRedirects(response, expected_url)