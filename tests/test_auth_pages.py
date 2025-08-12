import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_login_endpoint(self):
        """Test that login endpoint works correctly"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_register_endpoint(self):
        """Test user registration"""
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'password2': 'NewPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'newuser@example.com')
        
        # Verify user was created
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
    
    def test_register_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'password2': 'DifferentPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_request(self):
        """Test password reset request"""
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
    
    def test_password_reset_with_invalid_email(self):
        """Test password reset with non-existent email"""
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'nonexistent@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Generate valid token and uid
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post('/api/auth/password-reset-confirm/', {
            'uid': uid,
            'token': token,
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass123!'))
    
    def test_password_reset_confirm_with_invalid_token(self):
        """Test password reset with invalid token"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post('/api/auth/password-reset-confirm/', {
            'uid': uid,
            'token': 'invalid-token',
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_validate_token(self):
        """Test token validation endpoint"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post('/api/auth/password-reset-validate/', {
            'uid': uid,
            'token': token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_endpoint_authenticated(self):
        """Test user endpoint with authentication"""
        # Login first
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        
        response = self.client.get('/api/auth/user/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_user_endpoint_unauthenticated(self):
        """Test user endpoint without authentication"""
        response = self.client.get('/api/auth/user/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FrontendPageTests(TestCase):
    """Test that frontend pages are served correctly"""
    
    def setUp(self):
        self.client = Client()
    
    def test_auth_pages_accessible(self):
        """Test that auth pages are accessible"""
        auth_urls = [
            '/auth/sign-in',
            '/auth/sign-up',
            '/auth/password-reset',
            '/auth/password-new',
            '/auth/password-sent',
        ]
        
        for url in auth_urls:
            response = self.client.get(url)
            # Should return the SPA index.html
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<!DOCTYPE html>', response.content)