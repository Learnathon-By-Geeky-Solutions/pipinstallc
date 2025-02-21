from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser

class RegisterView(APIView):
    """
    Register a new user.
    """
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'User registered successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Login a user.
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
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
