from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ContributionSerializer, ContributionBasicAdsSerializer
from .models import Contributions


class ProfileView(APIView):
    """
    Get user profile data.
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


class UserInfoView(APIView):
    """
    Add user info.
    """
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'User info updated successfully',
                    'data':serializer.data
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(
            {
                'status': True,
                'message': 'User info fetched successfully',    
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
class UserContributionView(APIView):
    """
    Get all contributions that user have created.
    user must be authenticated to view their uploaded contribution

    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        contributions = Contributions.objects.filter(user=user)
        serializer = ContributionSerializer(contributions, many=True)
        return Response(
            {
                'status': True,
                'message': 'Contributions fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        try:
            serializer = ContributionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'status': True,
                        'message': 'Contribution created successfully',
                        'data': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'status': False,
                    'message': 'Invalid data',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        '''
        Update a contribution.
        '''
        try:
            user = request.user
            contribution = Contributions.objects.get(id=pk)
            
            # Check if user owns the contribution
            if contribution.user != user:
                return Response(
                    {
                        'status': False,
                        'message': 'You do not have permission to update this contribution'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ContributionSerializer(contribution, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'status': True,
                        'message': 'Contribution updated successfully',
                        'data': serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'status': False,
                    'message': 'Invalid data',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Contributions.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': f'Contribution with id {pk} does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        contribution = Contributions.objects.get(id=pk)
        contribution.delete()
        return Response(
            {
                'status': True,
                'message': 'Contribution deleted successfully',
            }, status=status.HTTP_200_OK)
    


class ContributionAdsView(APIView):
    def get(self,request):
        contributions = Contributions.objects.all()
        serializer = ContributionBasicAdsSerializer(contributions, many=True)
        return Response(
            {
                'status': True,
                'message': 'Contributions fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

class ContributionDetailsView(APIView):
    def get(self,request,pk):
        contribution = Contributions.objects.get(id=pk)
        serializer = ContributionSerializer(contribution)
        return Response(
            {
                'status': True,
                'message': 'Contribution details fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK 
        )
