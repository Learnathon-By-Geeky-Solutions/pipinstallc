from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


class ProfileView(APIView):
    """
    Get user profile.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)

        return Response(
            {
                'status': True,
                'message': 'User profile fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
