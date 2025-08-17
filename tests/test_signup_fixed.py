from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpFixedTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = '/auth/sign-up/'
        
    def test_signup_page_accessible(self):
        """Test that signup page is accessible"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        
    def test_signup_creates_user_and_redirects(self):
        """Test successful signup creates user and redirects to home"""
        data = {
            'username': 'testuser123',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        
        # Check user doesn't exist yet
        self.assertFalse(User.objects.filter(username='testuser123').exists())
        
        # Submit form
        response = self.client.post(self.signup_url, data)
        
        # Should redirect to home (302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:home'))
        
        # User should be created
        self.assertTrue(User.objects.filter(username='testuser123').exists())
        
        # User should be logged in
        user = User.objects.get(username='testuser123')
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        
    def test_signup_with_mismatched_passwords(self):
        """Test that mismatched passwords show error"""
        data = {
            'username': 'testuser456',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!'
        }
        
        response = self.client.post(self.signup_url, data)
        
        # Should not redirect (200)
        self.assertEqual(response.status_code, 200)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser456').exists())
        
        # Error message should be present
        self.assertContains(response, 'password')
        
    def test_signup_with_existing_username(self):
        """Test that duplicate username shows error"""
        # Create existing user
        User.objects.create_user(username='existinguser', password='password')
        
        data = {
            'username': 'existinguser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        
        response = self.client.post(self.signup_url, data)
        
        # Should not redirect (200)
        self.assertEqual(response.status_code, 200)
        
        # Should contain error message
        self.assertContains(response, 'username')
        
    def test_signup_with_weak_password(self):
        """Test that weak password shows error"""
        data = {
            'username': 'testuser789',
            'password1': '123',  # Too weak
            'password2': '123'
        }
        
        response = self.client.post(self.signup_url, data)
        
        # Should not redirect (200)
        self.assertEqual(response.status_code, 200)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser789').exists())
        
        # Should contain error about password
        self.assertContains(response, 'password')