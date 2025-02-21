
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import User_Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = ['id', 'user', 'profile_picture', 'is_email_verified', 'is_profile_verified', 'is_active', 'created_at', 'updated_at', 'date_of_birth', 'university', 'department', 'major_subject']


