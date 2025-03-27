from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ContributionSerializer, EnrollmentSerializer, ContributionCommentSerializer, AllContributionSerializer
from .models import Contributions, Enrollment, Contributions_comments

from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
from django.http import JsonResponse
import logging



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
    if pk is provided, get a single contribution by id
    if no pk is provided, get all contributions

    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            user = request.user
            contribution = Contributions.objects.get(id=pk)
            serializer = ContributionSerializer(contribution)
        else:
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
    
class AllContributionView(APIView):
    """
    get all contributions
    show only title, description, price, thumbnail_image, tags, origine, rating, comments
    if user is authenticated, show the enrollment status and if enrolled show with all the elements available
    if user is not authenticated, show only the basic elements

    """
    def get(self, request, pk=None):
        if pk:
            contribution = Contributions.objects.get(id=pk)
            serializer = AllContributionSerializer(contribution, context={'request': request})
        else:
            contributions = Contributions.objects.all()
            serializer = AllContributionSerializer(contributions, many=True, context={'request': request})
        return Response(
            {
                'status': True,
                'message': 'Contributions fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
    






"""
payment integration
"""

logger = logging.getLogger(__name__)

class EnrollmentView(APIView):
    """
    Handle contribution enrollments and payment integration
    user can view their enrollments and create new enrollments
    user must be authenticated to enroll in a contribution
    user can view a single enrollment by id
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id=None):
        if enrollment_id:
            enrollment = get_object_or_404(
                Enrollment.objects.select_related('contribution'), 
                user=request.user, 
                id=enrollment_id  # Using id since enrollment_id is the URL parameter
            )
            serializer = EnrollmentSerializer(enrollment, context={'request': request})
            return Response({
                'status': True,
                'message': 'Enrollment details fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            enrollments = Enrollment.objects.select_related('contribution').filter(
                user=request.user, 
                payment_status='COMPLETED'
            )
            serializer = EnrollmentSerializer(enrollments, many=True, context={'request': request})
            return Response({
                'status': True,
                'message': 'Enrollments fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)



class CreateEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contribution_id):
        contribution = get_object_or_404(Contributions, id=contribution_id)

        # Check if already enrolled or has pending enrollment
        existing_enrollment = Enrollment.objects.filter(
            user=request.user, 
            contribution=contribution
        ).first()

        if existing_enrollment:
            if existing_enrollment.payment_status == 'COMPLETED':
                return Response({
                    'status': False,
                    'message': 'Already enrolled in this contribution'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif existing_enrollment.payment_status == 'PENDING':
                # Reuse existing pending enrollment
                enrollment = existing_enrollment
            else:
                # If failed or cancelled, update the existing enrollment
                existing_enrollment.payment_status = 'PENDING'
                existing_enrollment.save()
                enrollment = existing_enrollment
        else:
            # Create new enrollment if none exists
            enrollment = Enrollment.objects.create(
                user=request.user,
                contribution=contribution,
                amount_paid=contribution.price,
                payment_status='PENDING'
            )

        # Initialize SSLCommerz payment
        sslcommerz_settings = {
            'store_id': settings.SSLCOMMERZ['STORE_ID'],
            'store_pass': settings.SSLCOMMERZ['STORE_PASSWORD'],
            'issandbox': settings.SSLCOMMERZ['IS_SANDBOX']
        }
        sslcz = SSLCOMMERZ(sslcommerz_settings)

        payment_data = {
            'total_amount': str(enrollment.amount_paid),
            'currency': 'BDT',
            'tran_id': str(enrollment.id),
            'success_url': request.build_absolute_uri(f'/api/payment/success/{enrollment.id}/'),
            'fail_url': request.build_absolute_uri(f'/api/payment/fail/{enrollment.id}/'),
            'cancel_url': request.build_absolute_uri(f'/api/payment/cancel/{enrollment.id}/'),
            'cus_name': request.user.username,
            'cus_email': request.user.email,
            'cus_phone': '01700000000',
            'cus_add1': 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'num_of_item': 1,
            'product_name': contribution.title,
            'product_category': 'Education',
            'product_profile': 'general',
            'emi_option': 0,
            'multi_card_name': '',
            'value_a': str(enrollment.id),  # Additional reference
            'value_b': request.user.username,
            'value_c': contribution.title,
            'value_d': ''
        }

        response = sslcz.createSession(payment_data)
        if response.get('status') == 'SUCCESS':
            return Response({
                'status': True,
                'message': 'Payment initiated successfully',
                'payment_url': response['GatewayPageURL']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': False,
                'message': 'Payment initiation failed',
                'error': response.get('failedreason', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
        

def payment_success(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Log all received parameters for debugging
    # logger.info(f"Payment callback received for enrollment {enrollment_id}")
    # logger.info(f"Request GET params: {request.GET}")
    # logger.info(f"Request POST params: {request.POST}")
    
    # In sandbox/development mode, be very lenient
    if settings.SSLCOMMERZ['IS_SANDBOX']:
        logger.info("Running in sandbox mode - auto-completing payment")
        enrollment.payment_status = 'COMPLETED'
        enrollment.payment_reference = f'SANDBOX_{enrollment.id}'
        enrollment.payment_method = 'SANDBOX'
        enrollment.save()
        logger.info(f"Payment marked as completed for enrollment {enrollment_id}")
        return JsonResponse({
            'status': 'success',
            'message': 'Payment completed successfully',
            'redirect_url': settings.PAYMENT_REDIRECT_URLS['SUCCESS']
        })
    
    # Production mode validation
    val_id = request.GET.get('val_id', '') or request.POST.get('val_id', '')
    tran_id = request.GET.get('tran_id', '') or request.POST.get('tran_id', '')
    amount = request.GET.get('amount', '') or request.POST.get('amount', '')
    status = request.GET.get('status', '') or request.POST.get('status', '')
    
    logger.info(f"Payment Status from SSLCommerz: {status}")
    logger.info(f"Transaction ID: {tran_id}")
    logger.info(f"Validation ID: {val_id}")
    logger.info(f"Amount: {amount}")
    
    if val_id:
        sslcommerz_settings = {
            'store_id': settings.SSLCOMMERZ['STORE_ID'],
            'store_pass': settings.SSLCOMMERZ['STORE_PASSWORD'],
            'issandbox': settings.SSLCOMMERZ['IS_SANDBOX']
        }
        sslcz = SSLCOMMERZ(sslcommerz_settings)
        
        try:
            response = sslcz.validationTransaction(val_id)
            logger.info(f"SSLCommerz validation response: {response}")
            
            if response.get('status') == 'VALID' or response.get('status') == 'SUCCESS':
                enrollment.payment_status = 'COMPLETED'
                enrollment.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment completed successfully',
                    'redirect_url': '/dashboard/my-courses/'
                })
        except Exception as e:
            logger.error(f"SSLCommerz validation error: {str(e)}")
    
    # If we reach here, something went wrong
    # logger.error(f"Payment validation failed for enrollment {enrollment_id}")
    # logger.error(f"Status: {status}, val_id: {val_id}, tran_id: {tran_id}")
    return JsonResponse({
        'status': 'error',
        'message': 'Payment validation failed',
        'debug_info': {
            'status': status,
            'val_id': val_id,
            'tran_id': tran_id,
            'amount': amount,
            'get_params': dict(request.GET),
            'post_params': dict(request.POST)
        }
    }, status=400)

def payment_fail(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Log the failure
    logger.info(f"Payment failed for enrollment {enrollment_id}")
    logger.info(f"Request GET params: {request.GET}")
    
    # Update payment status
    enrollment.payment_status = 'FAILED'
    enrollment.save()
    
    return JsonResponse({
        'status': 'fail',
        'message': 'Payment failed',
        'redirect_url': '/dashboard/payment-failed/'
    })

def payment_cancel(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Log the cancellation
    # logger.info(f"Payment cancelled for enrollment {enrollment_id}")
    # logger.info(f"Request GET params: {request.GET}")
    
    # Update payment status
    enrollment.payment_status = 'CANCELLED'
    enrollment.save()
    
    return JsonResponse({
        'status': 'cancel',
        'message': 'Payment canceled',
        'redirect_url': '/dashboard/payment-cancelled/'
    })


class ContributionCommentView(APIView):
    """
    Handle contribution comments
    user can add comments to a contribution
    user can view comments of a contribution
    user can delete comments of a contribution
    user can update comments of a contribution

    """
    permission_classes = [IsAuthenticated]

    def get(self, request, contribution_id=None):
        """
        if contribution_id is provided, get all comments of a contribution
        if no contribution_id is provided, get all comments
        """
        if contribution_id:
            contribution = get_object_or_404(Contributions, id=contribution_id)
            comments = Contributions_comments.objects.filter(contribution=contribution)
            serializer = ContributionCommentSerializer(comments, many=True)
        else:
            comments = Contributions_comments.objects.all()
            serializer = ContributionCommentSerializer(comments, many=True)
        return Response(
            {
                'status': True,
                'message': 'Comments fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        create a new comment
        """
        serializer = ContributionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Comment Posted successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(
            {
                'status': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, contribution_id, comment_id):
        """
        delete a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(Contributions_comments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            comment.delete()
            return Response(
                {
                    'status': True,
                    'message': 'Comment deleted successfully',
                }, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'status': False,
                    'message': 'You do not have permission to delete this comment',
                }, status=status.HTTP_403_FORBIDDEN)
        
    def put(self, request, contribution_id, comment_id):
        """
        update a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(Contributions_comments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            serializer = ContributionCommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'status': True,
                        'message': 'Comment updated successfully',
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'status': False,
                    'message': 'You do not have permission to update this comment',
                }, status=status.HTTP_403_FORBIDDEN)
        




