from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.user.is_email_verified = True
        self.user.save()

        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def test_register_user(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
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

    def test_logout(self):
        """Test user logout"""
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, logout_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'User logged out successfully')


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


from django.test import TestCase
from auth_app.models import CustomUser

class CustomUserManagerTest(TestCase):
    def test_create_user_success(self):
        """Test creating a user with valid data"""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email(self):
        """Test creating a user without an email raises an error"""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username='testuser',
                email=None,
                password='testpassword123'
            )
        self.assertEqual(str(context.exception), 'The Email field must be set')

    def test_create_superuser_success(self):
        """Test creating a superuser with valid data"""
        superuser = CustomUser.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.assertEqual(superuser.username, 'adminuser')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password('adminpassword123'))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_missing_is_staff(self):
        """Test creating a superuser without is_staff=True raises an error"""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_superuser(
                username='adminuser',
                email='admin@example.com',
                password='adminpassword123',
                is_staff=False
            )
        self.assertEqual(str(context.exception), 'Superuser must have is_staff=True.')

    def test_create_superuser_missing_is_superuser(self):
        """Test creating a superuser without is_superuser=True raises an error"""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_superuser(
                username='adminuser',
                email='admin@example.com',
                password='adminpassword123',
                is_superuser=False
            )
        self.assertEqual(str(context.exception), 'Superuser must have is_superuser=True.')


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



from django.test import TestCase
from django.contrib.admin.sites import site
from auth_app.admin import CustomUserAdmin
from auth_app.models import CustomUser

class CustomUserAdminTest(TestCase):
    def test_custom_user_admin_registered(self):
        """Test that CustomUser is registered in the admin site."""
        self.assertIn(CustomUser, site._registry)
        self.assertIsInstance(site._registry[CustomUser], CustomUserAdmin)

    def test_custom_user_admin_list_display(self):
        """Test that list_display is set correctly in CustomUserAdmin."""
        admin_instance = site._registry[CustomUser]
        self.assertEqual(admin_instance.list_display, ('username', 'email', 'is_staff', 'is_active',))

    def test_custom_user_admin_fieldsets(self):
        """Test that fieldsets are configured correctly in CustomUserAdmin."""
        admin_instance = site._registry[CustomUser]
        self.assertIn(('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 
                                                  'is_email_verified', 'is_profile_verified')}), 
                      admin_instance.fieldsets)
