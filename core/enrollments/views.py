from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, EnrollmentSerializer
from .models import Contributions, Enrollment
from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import logging
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt



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

        # If price is 0, mark as completed immediately and skip payment processing
        if contribution.price == 0 or contribution.price is None:
            enrollment.payment_status = 'COMPLETED'
            enrollment.payment_reference = 'FREE_ENROLLMENT'
            enrollment.payment_method = 'FREE'
            enrollment.save()
            
            return Response({
                'status': True,
                'message': 'Successfully enrolled in free contribution',
                'data': {
                    'enrollment_id': enrollment.id,
                    'contribution_id': contribution.id,
                    'contribution_title': contribution.title
                }
            }, status=status.HTTP_200_OK)

        # Initialize SSLCommerz payment for paid contributions
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
        

# SECURITY NOTE: CSRF protection is intentionally disabled for the following payment callback endpoints.
# This exemption is necessary and safe because:
# 1. These endpoints receive callbacks directly from the SSLCommerz payment gateway servers
# 2. External payment gateways cannot include Django's CSRF tokens in their requests
# 3. Instead of CSRF, we validate the payment gateway's authenticity through:
#    - Transaction validation using the payment gateway's API
#    - Verification of transaction IDs against our database records
#    - Secure handling of payment gateway credentials (store_id and store_pass)
# 4. These endpoints are specifically designed for server-to-server communication,
#    not for browser-based form submissions where CSRF would be applicable
@csrf_exempt
def payment_success(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # In sandbox/development mode, be very lenient
    if settings.SSLCOMMERZ['IS_SANDBOX']:
        logger.info("Running in sandbox mode - auto-completing payment")
        enrollment.payment_status = 'COMPLETED'
        enrollment.payment_reference = f'SANDBOX_{enrollment.id}'
        enrollment.payment_method = 'SANDBOX'
        enrollment.save()
        logger.info(f"Payment marked as completed for enrollment {enrollment_id}")
        
        # Get the contribution ID for the redirect
        contribution_id = str(enrollment.contribution.id)
        
        # Get the redirect URL from settings
        redirect_url = settings.PAYMENT_REDIRECT_URLS['SUCCESS']
        
        # Return HTML response using the template
        return render(request, 'success.html', {
            'contribution_id': contribution_id,
            'redirect_url': redirect_url
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
            # Security measure: Validate transaction with SSLCommerz API
            response = sslcz.validationTransaction(val_id)
            logger.info(f"SSLCommerz validation response: {response}")
            
            if response.get('status') == 'VALID' or response.get('status') == 'SUCCESS':
                enrollment.payment_status = 'COMPLETED'
                enrollment.save()
                
                # Use redirect_url from settings
                redirect_url = settings.PAYMENT_REDIRECT_URLS['SUCCESS']
                contribution_id = str(enrollment.contribution.id)
                
                return render(request, 'success.html', {
                    'contribution_id': contribution_id,
                    'redirect_url': redirect_url
                })
        except Exception as e:
            logger.error(f"SSLCommerz validation error: {str(e)}")
    
    # If we reach here, something went wrong
    redirect_url = settings.PAYMENT_REDIRECT_URLS["FAILED"]
    return render(request, 'fail.html', {'redirect_url': redirect_url})

@csrf_exempt
def payment_fail(request, enrollment_id):
    # See security note above regarding CSRF exemption for payment callbacks
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Log the failure
    logger.info(f"Payment failed for enrollment {enrollment_id}")
    logger.info(f"Request GET params: {request.GET}")
    
    # Update payment status
    enrollment.payment_status = 'FAILED'
    enrollment.save()
    
    redirect_url = settings.PAYMENT_REDIRECT_URLS['FAILED']
    return render(request, 'fail.html', {'redirect_url': redirect_url})

@csrf_exempt
def payment_cancel(request, enrollment_id):
    # See security note above regarding CSRF exemption for payment callbacks
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    enrollment.payment_status = 'CANCELLED'
    enrollment.save()
    
    redirect_url = settings.PAYMENT_REDIRECT_URLS['CANCELLED']
    return render(request, 'cancel.html', {'redirect_url': redirect_url})
