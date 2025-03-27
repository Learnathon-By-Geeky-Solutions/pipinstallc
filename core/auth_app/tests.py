from django.test import TestCase
import pytest
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .utils import generate_otp
from .views import send_otp_via_email, send_otp_via_email_forgot_password

User = get_user_model()

class AuthenticationTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.user.is_email_verified = True
        self.user.save()

        # Define API endpoints
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.verify_email_url = reverse('verify-email')
        self.resend_otp_url = reverse('resend-otp')
        self.forgot_password_url = reverse('forgot-password')
        self.reset_password_url = reverse('reset-password')

    def test_register_user(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser1@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 
                        'Registration successful. Please check your email for OTP.')

    def test_login_success(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_unverified_email(self):
        """Test login with unverified email"""
        self.user.is_email_verified = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpassword1234'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['message'], 'Email is not verified')

    def test_resend_otp(self):
        """Test resend OTP functionality"""
        data = {
            'email': 'test@example1.com'
        }
        response = self.client.post(self.resend_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'OTP sent successfully')

    # def test_verify_email(self):
    #     """Test email verification"""
    #     self.user.otp = '123456'
    #     self.user.save()

    #     data = {
    #         'email': 'test@example.com',
    #         'otp': '123456'
    #     }
    #     response = self.client.post(self.verify_email_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(response.data['status'])
    #     self.assertEqual(response.data['message'], 'Email verified successfully')

    def test_forgot_password(self):
        """Test forgot password functionality"""
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 
                        'Password reset OTP sent successfully')

    # def test_reset_password(self):
    #     """Test password reset"""
    #     self.user.otp = '123456'
    #     self.user.save()

    #     data = {
    #         'email': 'test@example.com',
    #         'password': 'newpassword123',
    #         'password2': 'newpassword123',
    #         'otp': '123456'
    #     }
    #     response = self.client.post(self.reset_password_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(response.data['status'])
    #     self.assertEqual(response.data['message'], 'Password reset successful')

    def test_logout(self):
        """Test user logout"""
        # First login to get the refresh token
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Then try to logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'User logged out successfully')

    # def test_logout_without_token(self):
    #     """Test logout without providing refresh token"""
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer some-access-token')
    #     response = self.client.post(self.logout_url, {})
        
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertFalse(response.data['status'])
    #     self.assertEqual(response.data['message'], 'Refresh token is required')

    # @patch('django.core.mail.send_mail', side_effect=Exception('Email sending failed'))
    # def test_email_sending_failure(self, mock_send_mail):
    #     """Test handling of email sending failure"""
    #     data = {
    #         'username': 'newuser',
    #         'email': 'newuser@example.com',
    #         'password': 'newpassword123',
    #         'password2': 'newpassword123'
    #     }
    #     response = self.client.post(self.register_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.assertFalse(response.data['status'])
    #     self.assertEqual(response.data['message'], 
    #                     'Failed to send OTP email. Please try again.')