from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,VerifyEmailSerializer,ResendOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .emails import send_otp_via_email,send_otp_via_email_forgot_password


class RegisterView(APIView):
    """
    Register a new user.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send OTP
            otp = send_otp_via_email(user.email)
            if otp:
                user.otp = otp
                user.save()
                return Response(
                    {
                        'status': True,
                        'message': 'Registration successful. Please check your email for OTP.',
                        'data': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'status': False,
                    'message': 'Failed to send OTP email. Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Login a user.

    This view handles user login requests. It expects a POST request with 
    the username and password in the request body. If the credentials are 
    valid, it generates a JWT refresh token for the user and returns it 
    along with the user's details. If the credentials are invalid, it 
    returns an unauthorized response.
    """
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        user = CustomUser.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
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
        return Response(
            {
                'status': False,
                'message': 'Invalid credentials',
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
class LogoutView(APIView):
    """
    Logout a user by blacklisting their refresh token.
    Requires the refresh token in the request body.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
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
        except Exception:
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
    If the OTP is valid, the user's email is marked as verified, and the stored OTP is cleared.
    If the OTP is invalid or the user does not exist, appropriate error messages are returned.
    """
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email=serializer.validated_data['email'])
                stored_otp = user.otp
                received_otp = serializer.validated_data['otp']
                
                print(f"Stored OTP: {stored_otp}")  # For debugging
                print(f"Received OTP: {received_otp}")  # For debugging
                
                if stored_otp != received_otp:
                    return Response(
                        {
                            'status': False,
                            'message': 'Invalid OTP. Please check and try again.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user.is_email_verified = True
                user.otp = None  # Clear OTP after verification
                user.save()
                
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
        return Response(
            {
                'status': False,
                'message': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
class ResendOTPView(APIView):
    """
    Resend OTP to user's email.
    """
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            otp = send_otp_via_email(user.email)
            if otp:
                user.otp = otp
                user.save()
                return Response(
                    {
                        'status': True,
                        'message': 'OTP sent successfully',
                        'data': {
                            'email': user.email,
                            'otp': otp
                        }
                    },
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ForgotPasswordView(APIView):
    """
    View to handle forgot password requests.
    This view allows users to request a One-Time Password (OTP) 
    to be sent to their email for the purpose of resetting their password.
    """

    def post(self, request):
        """
        Handle POST requests for forgot password.
        
        Args:
            request: The HTTP request object containing the email for password reset.
        
        Returns:
            Response: A response object indicating the success or failure of the OTP sending process.
        """
        # Initialize the serializer with the request data
        serializer = ForgotPasswordSerializer(data=request.data)
        
        # Check if the provided data is valid
        if serializer.is_valid():
            # Extract the email from the validated data
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            otp = send_otp_via_email_forgot_password(user.email)
            
            if otp:
                # Save the OTP to the user's record if sent succesfully
                user.otp = otp
                user.save()
                
                return Response(
                    {
                        'status': True,
                        'message': 'Password reset OTP sent successfully',
                        'data': {
                            'email': user.email,
                            'otp': otp
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

class ResetPasswordView(APIView):
    """
    View to handle password reset requests.
    This view allows users to reset their password using a One-Time Password (OTP).
    """
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(
                {
                    'status': True,
                    'message': 'Password reset successful'
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
