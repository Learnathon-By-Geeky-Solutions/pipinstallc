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
from django.shortcuts import get_object_or_404



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
        
        # Return HTML response with redirect button and embedded data
        html_content = f"""
        <html>
        <head>
            <title>Payment Success</title>
            <style>
                .container {{
                    text-align: center;
                    margin-top: 50px;
                }}
                .redirect-btn {{
                    padding: 10px 20px;
                    background-color: #6c2bb3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 20px;
                }}
                .hidden-data {{
                    display: none;
                }}
            </style>
            <script>
                // Auto-redirect after 3 seconds
                window.onload = function() {{
                    setTimeout(function() {{
                        window.location.href = "{redirect_url}";
                    }}, 3000);
                }};
            </script>
        </head>
        <body>
            <div class="container">
                <h2>Payment Completed Successfully!</h2>
                <p>You will be redirected in a few seconds...</p>
                <a href="{redirect_url}" class="redirect-btn">
                    Continue Now
                </a>
                <div id="payment-data" class="hidden-data" data-contribution-id="{contribution_id}" data-redirect-url="{redirect_url}"></div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content)
    
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
