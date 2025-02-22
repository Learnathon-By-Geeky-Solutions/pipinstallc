from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password2', 'is_email_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_email_verified': {'read_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user



class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("OTP must be 4 digits")
        return value

    def validate(self, data):
        # Check if user exists with this email
        try:
            user = CustomUser.objects.get(email=data['email'])
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already verified")
            if user.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email")
        return data

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("No user found with this email")
        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("No user found with this email")
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("OTP must be 4 digits")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.get(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    


