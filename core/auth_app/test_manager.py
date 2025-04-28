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
