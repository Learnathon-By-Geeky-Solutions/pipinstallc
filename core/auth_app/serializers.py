from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Enhanced with validation and security measures.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': 'Password must be at least 8 characters long.',
            'max_length': 'Password must be less than 128 characters long.',
            'blank': 'Password cannot be blank.',
            'required': 'Password is required.'
        }
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        error_messages={
            'min_length': 'Password confirmation must be at least 8 characters long.',
            'max_length': 'Password confirmation must be less than 128 characters long.',
            'blank': 'Password confirmation cannot be blank.',
            'required': 'Password confirmation is required.'
        }
    )
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank.',
            'max_length': 'Email must be less than 255 characters.'
        }
    )
    username = serializers.CharField(
        max_length=255,
        error_messages={
            'required': 'Username is required.',
            'blank': 'Username cannot be blank.',
            'max_length': 'Username must be less than 255 characters.'
        }
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password2', 'is_email_verified']
        extra_kwargs = {
            'is_email_verified': {'read_only': True}
        }

    def validate_email(self, value):
        """
        Normalize and validate email address.
        """
        normalized_email = value.lower().strip()
        
        # Check if email is already in use
        if CustomUser.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
            
        return normalized_email
        
    def validate_username(self, value):
        """
        Normalize and validate username.
        """
        normalized_username = value.strip()
        
        # Check if username is already in use
        if CustomUser.objects.filter(username=normalized_username).exists():
            raise serializers.ValidationError("This username is already taken.")
            
        # Check for valid characters - customize as needed
        if not all(c.isalnum() or c in '-_.' for c in normalized_username):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and the characters '-', '_', '.'"
            )
            
        return normalized_username

    def validate(self, data):
        """
        Check that the two password entries match and meet security requirements.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
            
        # Basic password strength check - customize as needed
        password = data['password']
        if password.isdigit():
            raise serializers.ValidationError({"password": "Password cannot be entirely numeric."})
            
        if password.islower() or password.isupper():
            raise serializers.ValidationError({"password": "Password must contain both uppercase and lowercase letters."})
            
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({"password": "Password must contain at least one number."})
            
        return data
    
    def create(self, validated_data):
        """
        Create and return a new user, removing the password2 field.
        """
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login using email.
    Enhanced with validation and security measures.
    """
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address',
            'blank': 'Email cannot be blank',
            'max_length': 'Email must be less than 255 characters'
        }
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8,
        max_length=128,
        error_messages={
            'required': 'Password is required',
            'blank': 'Password cannot be blank',
            'min_length': 'Password must be at least 8 characters',
            'max_length': 'Password must be less than 128 characters'
        }
    )
    
    def validate_email(self, value):
        """
        Additional validation for email to prevent common attacks
        """
        # Convert to lowercase for case-insensitive comparison
        return value.lower().strip()
    
    def validate(self, attrs):
        # Additional validation can be added here if needed
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for verifying a user's email.
    """
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
    """
    Serializer for resending OTP for email verification.

    """
    email = serializers.EmailField()

    def validate(self, data):
        if not CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("No user found")
        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for sending OTP for password reset.

    """
    email = serializers.EmailField()

    def validate(self, data):
        if not CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("No user found registered with this email")
        return data

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting a user's password.
    """
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
    


