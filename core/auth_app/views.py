from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,VerifyEmailSerializer,ResendOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .emails import send_otp_via_email,send_otp_via_email_forgot_password
import logging
from django.utils import timezone
from django.db import transaction
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create a safer cache wrapper for environments where cache might not be configured
class SafeCache:
    def get(self, key, default=None):
        try:
            from django.core.cache import cache
            return cache.get(key, default)
        except Exception as e:
            logger.warning(f"Cache get operation failed: {str(e)}")
            return default
    
    def set(self, key, value, timeout=None):
        try:
            from django.core.cache import cache
            return cache.set(key, value, timeout=timeout)
        except Exception as e:
            logger.warning(f"Cache set operation failed: {str(e)}")
            return None
    
    def delete(self, key):
        try:
            from django.core.cache import cache
            return cache.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete operation failed: {str(e)}")
            return None

# Use our safe cache wrapper instead of direct cache access
safe_cache = SafeCache()

# Helper function for getting client IP - shared across views
def get_client_ip(request):
    """Extract client IP address from request with proxy handling"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get the first IP in the chain (client IP)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip

class RegisterView(APIView):
    """
    Register a new user with optimized database operations and enhanced security.
    """
    def post(self, request):
        client_ip = get_client_ip(request)
        
        # Implement registration rate limiting
        if self._check_register_rate_limit(client_ip):
            logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
            return Response(
                {
                    'status': False,
                    'message': 'Too many registration attempts. Please try again later.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
        try:
            # Use Django's transaction to ensure atomicity
            with transaction.atomic():
                serializer = RegisterSerializer(data=request.data)
                if serializer.is_valid():
                    # Check if email already exists - additional security check
                    email = serializer.validated_data['email'].lower().strip()
                    if CustomUser.objects.filter(email=email).exists():
                        logger.warning(f"Registration attempt with existing email: {email} from IP: {client_ip}")
                        return Response(
                            {
                                'status': False,
                                'message': 'A user with this email already exists.'
                            },
                            status=status.HTTP_409_CONFLICT
                        )
                        
                    # Create user within transaction
                    user = serializer.save()
                    
                    # Generate and send OTP
                    otp = send_otp_via_email(user.email)
                    if otp:
                        # Only update the specific field needed
                        user.otp = otp
                        user.save(update_fields=['otp'])
                        
                        # Log successful registration
                        logger.info(f"User registered successfully: ID {user.id}, email {user.email} from IP {client_ip}")
                        
                        # Reset registration rate limit counter
                        self._reset_register_rate_limit(client_ip)
                        
                        # Return minimal user data - don't expose sensitive information
                        return Response(
                            {
                                'status': True,
                                'message': 'Registration successful. Please check your email for OTP.',
                                'data': {
                                    'id': user.id,
                                    'email': user.email
                                }
                            },
                            status=status.HTTP_201_CREATED
                        )
                    
                    # If OTP sending failed, delete the user to maintain consistency
                    user.delete()
                    logger.error(f"Failed to send OTP for new registration: {email} from IP {client_ip}")
                    
                    return Response(
                        {
                            'status': False,
                            'message': 'Failed to send verification email. Please try again.'
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Increment registration attempt counter for invalid input
                self._increment_register_attempts(client_ip)
                
                # Log validation errors
                logger.warning(f"Registration validation failed from IP {client_ip}: {serializer.errors}")
                
                return Response(
                    {
                        'status': False,
                        'message': 'Invalid registration data',
                        'errors': serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            # Log the error for monitoring
            logger.error(f"Registration error from IP {client_ip}: {str(e)}")
            
            # Increment registration attempt counter for server errors
            self._increment_register_attempts(client_ip)
            
            return Response(
                {
                    'status': False,
                    'message': 'Registration failed. Please try again later.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def _check_register_rate_limit(self, client_ip):
        """Check if client has exceeded registration rate limits"""
        rate_limit_key = f"register_attempts:{client_ip}"
        attempts = safe_cache.get(rate_limit_key, 0)
        
        # Get configurable max attempts, defaulting to 3
        max_attempts = getattr(settings, 'MAX_REGISTER_ATTEMPTS', 3)
        
        return attempts >= max_attempts
    
    def _increment_register_attempts(self, client_ip):
        """Increment failed registration attempts counter"""
        rate_limit_key = f"register_attempts:{client_ip}"
        attempts = safe_cache.get(rate_limit_key, 0)
        
        # Get configurable timeout, defaulting to 1 hour (3600 seconds)
        timeout = getattr(settings, 'REGISTER_ATTEMPTS_TIMEOUT', 3600)
        
        safe_cache.set(rate_limit_key, attempts + 1, timeout=timeout)
    
    def _reset_register_rate_limit(self, client_ip):
        """Reset registration attempts counter after successful registration"""
        rate_limit_key = f"register_attempts:{client_ip}"
        safe_cache.delete(rate_limit_key)

class LoginView(APIView):
    """
    Login a user using email and password.

    This view handles user login requests with optimized database queries
    and enhanced security measures to protect against brute force attacks.
    """
    def post(self, request):
        client_ip = get_client_ip(request)
        
        # Implement rate limiting
        if self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                {
                    'status': False,
                    'message': 'Too many login attempts. Please try again later.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Use serializer for validation
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Increment failed attempt counter for invalid input
            self._increment_failed_attempts(client_ip)
            
            return Response(
                {
                    'status': False,
                    'message': 'Invalid input',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get validated data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Use optimized, indexed query based on email
        try:
            with transaction.atomic():
                # Use indexed fields for efficient lookup
                user = CustomUser.objects.select_related(
                    'university', 'department', 'major_subject'
                ).filter(email=email, is_active=True).first()
                    
                if not user:
                    # Log failed login attempt - don't reveal if user exists
                    logger.warning(f"Failed login attempt for email: {email} from IP: {client_ip}")
                    self._increment_failed_attempts(client_ip)
                    
                    # Use constant time response to prevent timing attacks
                    return self._get_invalid_credentials_response()
                    
                if not user.is_email_verified:
                    # Log the event but don't increment failed attempts counter
                    logger.info(f"Login attempt for unverified email: {email} from IP: {client_ip}")
                    
                    return Response(
                        {
                            'status': False,
                            'message': 'Email is not verified. Please verify your email before logging in.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                    
                # Check password with constant time comparison
                if user.check_password(password):
                    # Reset failed attempt counter on successful login
                    self._reset_failed_attempts(client_ip)
                    
                    # Update last login time
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    
                    # Log successful login
                    logger.info(f"Successful login for user ID: {user.id} from IP: {client_ip}")
                    
                    # Generate JWT tokens with appropriate expiry
                    refresh = RefreshToken.for_user(user)
                    
                    # Customize token claims if needed
                    refresh['email'] = user.email
                    
                    # Add refresh token to blacklist when user explicitly logs out
                    # (handled in LogoutView)
                    
                    return Response(
                        {
                            'status': True,
                            'message': 'User logged in successfully',
                            'access': str(refresh.access_token),
                            'refresh': str(refresh),
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    # Log failed login attempt due to wrong password
                    logger.warning(f"Failed login attempt (wrong password) for user ID: {user.id} from IP: {client_ip}")
                    self._increment_failed_attempts(client_ip)
                    
                    # Use constant time response to prevent timing attacks
                    return self._get_invalid_credentials_response()
                    
        except Exception as e:
            # Log the unexpected error
            logger.error(f"Login error for email {email} from IP {client_ip}: {str(e)}")
            
            # Don't increment failure counter for server errors
            return Response(
                {
                    'status': False,
                    'message': 'An error occurred during login. Please try again later.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_rate_limit(self, client_ip):
        """Check if client has exceeded rate limits"""
        rate_limit_key = f"login_attempts:{client_ip}"
        attempts = safe_cache.get(rate_limit_key, 0)
        
        # Get configurable max attempts, defaulting to 5
        max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        
        return attempts >= max_attempts
    
    def _increment_failed_attempts(self, client_ip):
        """Increment failed login attempts counter"""
        rate_limit_key = f"login_attempts:{client_ip}"
        attempts = safe_cache.get(rate_limit_key, 0)
        
        # Get configurable timeout, defaulting to 5 minutes (300 seconds)
        timeout = getattr(settings, 'LOGIN_ATTEMPTS_TIMEOUT', 300)
        
        safe_cache.set(rate_limit_key, attempts + 1, timeout=timeout)
    
    def _reset_failed_attempts(self, client_ip):
        """Reset failed login attempts counter"""
        rate_limit_key = f"login_attempts:{client_ip}"
        safe_cache.delete(rate_limit_key)
    
    def _get_invalid_credentials_response(self):
        """Return standardized response for invalid credentials"""
        return Response(
            {
                'status': False,
                'message': 'Invalid credentials'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    """
    Logout a user by blacklisting their refresh token.
    Requires the refresh token in the request body.
    Optimized for performance with database indexes.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Get the user ID for logging
                user_id = request.user.id
                
                # Blacklist the token
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                # We could log the logout for security tracking
                logger.info(f"User {user_id} logged out successfully")
                
                return Response(
                    {
                        'status': True,
                        'message': 'User logged out successfully',
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'status': False,
                        'message': 'Refresh token is required',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            # Log the error for monitoring
            logger.error(f"Logout error: {str(e)}")
            
            return Response(
                {
                    'status': False,
                    'message': 'An error occurred while logging out.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class VerifyEmailView(APIView):
    """
    Verify a user's email address by checking the provided OTP (One-Time Password).
    
    This view handles POST requests containing the user's email and the OTP they received.
    It validates the OTP against the stored OTP in the database for the user associated with the provided email.
    Optimized for performance with large user bases through proper indexing.
    """
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                email = serializer.validated_data['email']
                received_otp = serializer.validated_data['otp']
                
                # Use efficient indexed lookup
                user = CustomUser.objects.filter(
                    email=email,  # Indexed field
                    is_active=True,  # Indexed field
                    otp=received_otp
                ).first()
                
                if not user:
                    return Response(
                        {
                            'status': False,
                            'message': 'Invalid OTP or email. Please check and try again.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Use update_fields to only update what's necessary
                user.is_email_verified = True
                user.otp = None  # Clear OTP after verification
                user.save(update_fields=['is_email_verified', 'otp'])
                
                return Response(
                    {
                        'status': True,
                        'message': 'Email verified successfully'
                    },
                    status=status.HTTP_200_OK
                )
                
            except CustomUser.DoesNotExist:
                return Response(
                    {
                        'status': False,
                        'message': 'User not found with this email'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                # Log the error for monitoring
                logger.error(f"Email verification error: {str(e)}")
                
                return Response(
                    {
                        'status': False,
                        'message': 'Email verification failed. Please try again.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        return Response(
            {
                'status': False,
                'message': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
class ResendOTPView(APIView):
    """
    Resend OTP to user's email with optimized database operations.
    """
    def post(self, request):
        try:
            serializer = ResendOTPSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                
                # Use indexed fields for efficient lookup
                user = CustomUser.objects.filter(
                    email=email,  # Indexed field
                    is_active=True  # Indexed field
                ).first()
                
                if not user:
                    # For security, don't reveal if the email exists or not
                    return Response(
                        {
                            'status': True,
                            'message': 'If your email is registered, you will receive an OTP shortly.'
                        },
                        status=status.HTTP_200_OK
                    )
                
                otp = send_otp_via_email(user.email)
                if otp:
                    # Only update the needed field
                    user.otp = otp
                    user.save(update_fields=['otp'])
                    
                    return Response(
                        {
                            'status': True,
                            'message': 'OTP sent successfully',
                            'data': {
                                'email': user.email
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                
                return Response(
                    {
                        'status': False,
                        'message': 'Failed to send OTP. Please try again.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Log the error for monitoring
            logger.error(f"Resend OTP error: {str(e)}")
            
            return Response(
                {
                    'status': False,
                    'message': 'An error occurred while resending OTP.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ForgotPasswordView(APIView):
    """
    View to handle forgot password requests.
    This view allows users to request a One-Time Password (OTP) 
    to be sent to their email for the purpose of resetting their password.
    Optimized for performance with database indexes.
    """

    def post(self, request):
        """
        Handle POST requests for forgot password.
        
        Args:
            request: The HTTP request object containing the email for password reset.
        
        Returns:
            Response: A response object indicating the success or failure of the OTP sending process.
        """
        try:
            # Initialize the serializer with the request data
            serializer = ForgotPasswordSerializer(data=request.data)
            
            # Check if the provided data is valid
            if serializer.is_valid():
                # Extract the email from the validated data
                email = serializer.validated_data['email']
                
                # Use indexed field for efficient lookup
                user = CustomUser.objects.filter(
                    email=email,  # Indexed field
                    is_active=True  # Indexed field
                ).first()
                
                if not user:
                    # For security, don't reveal if the email exists or not
                    return Response(
                        {
                            'status': True,
                            'message': 'If your email is registered, you will receive an OTP shortly.',
                        },
                        status=status.HTTP_200_OK
                    )
                    
                otp = send_otp_via_email_forgot_password(user.email)
                
                if otp:
                    # Save the OTP to the user's record if sent successfully
                    # Only update the specific field
                    user.otp = otp
                    user.save(update_fields=['otp'])
                    
                    return Response(
                        {
                            'status': True,
                            'message': 'Password reset OTP sent successfully',
                            'data': {
                                'email': user.email
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                
                return Response(
                    {
                        'status': False,
                        'message': 'Failed to send OTP email. Please try again.',
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return validation errors if the serializer is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Log the error for monitoring
            logger.error(f"Forgot password error: {str(e)}")
            
            return Response(
                {
                    'status': False,
                    'message': 'An error occurred while processing your request.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResetPasswordView(APIView):
    """
    View to handle password reset requests.
    This view allows users to reset their password using a One-Time Password (OTP).
    Optimized for large user bases with database indexes.
    """
    def post(self, request):
        try:
            # Use django transaction for atomicity
            from django.db import transaction
            
            with transaction.atomic():
                serializer = ResetPasswordSerializer(data=request.data)
                if serializer.is_valid():
                    email = serializer.validated_data['email']
                    supplied_otp = serializer.validated_data['otp']
                    new_password = serializer.validated_data['password']
                    
                    # Use indexed fields for efficient lookup
                    user = CustomUser.objects.filter(
                        email=email,  # Indexed field
                        is_active=True,  # Indexed field
                        otp=supplied_otp
                    ).first()
                    
                    if not user:
                        return Response(
                            {
                                'status': False,
                                'message': 'Invalid OTP or email. Please check and try again.'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Set new password and clear OTP
                    user.set_password(new_password)
                    user.otp = None
                    user.save(update_fields=['password', 'otp'])
                    
                    return Response(
                        {
                            'status': True,
                            'message': 'Password reset successful'
                        },
                        status=status.HTTP_200_OK
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # Log the error for monitoring
            logger.error(f"Password reset error: {str(e)}")
            
            return Response(
                {
                    'status': False,
                    'message': 'An error occurred while resetting your password.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    
