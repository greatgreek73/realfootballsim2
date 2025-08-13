from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_signup_page_accessible(self):
        """Test that signup page is accessible"""
        response = self.client.get('/auth/sign-up/')
        self.assertEqual(response.status_code, 200)
        
    def test_signup_creates_user(self):
        """Test that form submission creates new user"""
        data = {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        response = self.client.post('/auth/sign-up/', data, follow=True)
        
        # Debug: print form errors if any
        if response.status_code == 200 and 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check user is logged in (redirected to home)
        self.assertRedirects(response, reverse('core:home'))
        
        # Check user is authenticated
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'newuser')
        
    def test_signup_with_mismatched_passwords(self):
        """Test that mismatched passwords show error"""
        data = {
            'username': 'testuser',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        
        response = self.client.post('/auth/sign-up/', data)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())
        
        # Should stay on signup page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password')