
from rest_framework import serializers
from auth_app.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'is_email_verified', 'phone_number', 'is_profile_verified', 'date_of_birth', 'university', 'department', 'major_subject']



