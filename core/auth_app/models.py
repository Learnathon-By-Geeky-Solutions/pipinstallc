from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .manager import CustomUserManager
from django.apps import apps

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_profile_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    university = models.ForeignKey('api.University', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('api.Department', on_delete=models.SET_NULL, null=True, blank=True)
    major_subject = models.ForeignKey('api.MajorSubject', on_delete=models.SET_NULL, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    

