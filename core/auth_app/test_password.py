from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.user.is_email_verified = True
        self.user.save()

        self.forgot_password_url = reverse('forgot-password')
        self.reset_password_url = reverse('reset-password')

    def test_forgot_password(self):
        """Test forgot password functionality"""
        data = {'email': 'test@example.com'}
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