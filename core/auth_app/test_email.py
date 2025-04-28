from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.user.is_email_verified = True
        self.user.save()

        self.resend_otp_url = reverse('resend-otp')
        self.verify_email_url = reverse('verify-email')

    def test_resend_otp(self):
        """Test resend OTP functionality"""
        data = {'email': 'test@example.com'}
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