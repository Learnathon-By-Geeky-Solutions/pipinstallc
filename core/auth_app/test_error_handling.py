# from unittest.mock import patch
# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse

# class ErrorHandlingTest(APITestCase):
#     @patch('django.core.mail.send_mail', side_effect=Exception('Email sending failed'))
#     def test_email_sending_failure(self, mock_send_mail):
#         """Test handling of email sending failure"""
#         register_url = reverse('register')
#         data = {
#             'username': 'newuser',
#             'email': 'newuser@example.com',
#             'password': 'newpassword123',
#             'password2': 'newpassword123'
#         }
#         response = self.client.post(register_url, data)
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertFalse(response.data['status'])
#         self.assertEqual(response.data['message'], 
#                          'Failed to send OTP email. Please try again.')