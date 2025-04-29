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
