from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.models import University, Department, MajorSubject, Contributions, ContributionTags
from .models import Enrollment
from uuid import uuid4
from django.conf import settings
from unittest.mock import patch, MagicMock
import json

User = get_user_model()

class EnrollmentModelTest(TestCase):
    """Test cases for the Enrollment model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        # Create test university, department, and major subject
        self.university = University.objects.create(name='Test University')
        self.department = Department.objects.create(name='Test Department')
        self.major_subject = MajorSubject.objects.create(name='Test Major')
        
        # Create test contribution
        self.contribution = Contributions.objects.create(
            title='Test Contribution',
            description='Test Description',
            price=100.00,
            user=self.user,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )
    
    def test_enrollment_creation(self):
        """Test creating an enrollment record."""
        enrollment = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='PENDING'
        )
        
        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.contribution, self.contribution)
        self.assertEqual(enrollment.amount_paid, self.contribution.price)
        self.assertEqual(enrollment.payment_status, 'PENDING')
    
    def test_enrollment_unique_constraint(self):
        """Test that a user cannot enroll in the same contribution twice."""
        # Create first enrollment
        Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='COMPLETED'
        )
        
        # Attempt to create a duplicate enrollment - should raise IntegrityError
        with self.assertRaises(Exception):
            Enrollment.objects.create(
                user=self.user,
                contribution=self.contribution,
                amount_paid=self.contribution.price,
                payment_status='PENDING'
            )
    
    def test_payment_status_choices(self):
        """Test the different payment status choices."""
        # Test each status value
        for status_choice in ['PENDING', 'COMPLETED', 'FAILED', 'CANCELLED']:
            enrollment = Enrollment.objects.create(
                user=self.user,
                contribution=Contributions.objects.create(
                    title=f'Test Contribution {status_choice}',
                    price=100.00,
                    user=self.user
                ),
                amount_paid=100.00,
                payment_status=status_choice
            )
            self.assertEqual(enrollment.payment_status, status_choice)


class EnrollmentViewTest(APITestCase):
    """Test cases for EnrollmentView."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        # Create test university, department, and major subject
        self.university = University.objects.create(name='Test University')
        self.department = Department.objects.create(name='Test Department')
        self.major_subject = MajorSubject.objects.create(name='Test Major')
        
        # Create test contributions
        self.contribution1 = Contributions.objects.create(
            title='Test Contribution 1',
            description='Test Description 1',
            price=100.00,
            user=self.user,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )
        
        self.contribution2 = Contributions.objects.create(
            title='Test Contribution 2',
            description='Test Description 2',
            price=200.00,
            user=self.user,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )
        
        # Create enrollments
        self.enrollment1 = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution1,
            amount_paid=self.contribution1.price,
            payment_status='COMPLETED'
        )
        
        self.enrollment2 = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution2,
            amount_paid=self.contribution2.price,
            payment_status='PENDING'
        )
        
        # Set up URLs for testing
        try:
            self.enrollments_url = reverse('user-enrollments')
        except:
            self.enrollments_url = '/api/enrollments/'
        
        try:
            self.enrollment_detail_url = reverse('enrollment-detail', kwargs={'enrollment_id': self.enrollment1.id})
        except:
            self.enrollment_detail_url = f'/api/enrollments/{self.enrollment1.id}/'
        
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
    
    def test_get_all_enrollments(self):
        """Test retrieving all completed enrollments for a user."""
        response = self.client.get(self.enrollments_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Enrollments fetched successfully')
        
        # Only completed enrollments should be returned
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['id'], str(self.enrollment1.id))
        self.assertEqual(response.data['data'][0]['payment_status'], 'COMPLETED')
    
    def test_get_enrollment_detail(self):
        """Test retrieving a specific enrollment."""
        response = self.client.get(self.enrollment_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Enrollment details fetched successfully')
        self.assertEqual(response.data['data']['id'], str(self.enrollment1.id))
        self.assertEqual(response.data['data']['payment_status'], 'COMPLETED')
    
    def test_get_enrollment_detail_unauthorized(self):
        """Test that unauthenticated users cannot access enrollments."""
        # Log out the user
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.enrollment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_nonexistent_enrollment(self):
        """Test retrieving a non-existent enrollment."""
        nonexistent_uuid = uuid4()
        nonexistent_url = f'/api/enrollments/{nonexistent_uuid}/'
        response = self.client.get(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateEnrollmentViewTest(APITestCase):
    """Test cases for CreateEnrollmentView."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        # Create test university, department, and major subject
        self.university = University.objects.create(name='Test University')
        self.department = Department.objects.create(name='Test Department')
        self.major_subject = MajorSubject.objects.create(name='Test Major')
        
        # Create test contribution
        self.contribution = Contributions.objects.create(
            title='Test Contribution',
            description='Test Description',
            price=100.00,
            user=self.user,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )
        
        # Set up URL for testing
        try:
            self.create_enrollment_url = reverse('create-enrollment', kwargs={'contribution_id': self.contribution.id})
        except:
            self.create_enrollment_url = f'/api/create-enrollments/{self.contribution.id}/'
        
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
    
    @patch('enrollments.views.SSLCOMMERZ')
    def test_create_enrollment_success(self, mock_sslcommerz):
        """Test creating a new enrollment with successful payment initiation."""
        # Mock the SSLCommerz response
        mock_instance = MagicMock()
        mock_instance.createSession.return_value = {
            'status': 'SUCCESS',
            'GatewayPageURL': 'https://sandbox.sslcommerz.com/payment/page'
        }
        mock_sslcommerz.return_value = mock_instance
        
        response = self.client.post(self.create_enrollment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Payment initiated successfully')
        self.assertIn('payment_url', response.data)
        
        # Check that an enrollment was created
        self.assertEqual(Enrollment.objects.filter(
            user=self.user,
            contribution=self.contribution,
            payment_status='PENDING'
        ).count(), 1)
    
    @patch('enrollments.views.SSLCOMMERZ')
    def test_create_enrollment_failure(self, mock_sslcommerz):
        """Test creating a new enrollment with failed payment initiation."""
        # Mock the SSLCommerz response
        mock_instance = MagicMock()
        mock_instance.createSession.return_value = {
            'status': 'FAILED',
            'failedreason': 'Test failure reason'
        }
        mock_sslcommerz.return_value = mock_instance
        
        response = self.client.post(self.create_enrollment_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['message'], 'Payment initiation failed')
        self.assertEqual(response.data['error'], 'Test failure reason')
    
    @patch('enrollments.views.SSLCOMMERZ')
    def test_create_enrollment_already_enrolled(self, mock_sslcommerz):
        """Test creating an enrollment when already enrolled."""
        # Create a completed enrollment
        Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='COMPLETED'
        )
        
        response = self.client.post(self.create_enrollment_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['message'], 'Already enrolled in this contribution')
    
    @patch('enrollments.views.SSLCOMMERZ')
    def test_create_enrollment_with_pending_payment(self, mock_sslcommerz):
        """Test creating an enrollment when there's already a pending payment."""
        # Create a pending enrollment
        Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='PENDING'
        )
        
        # Mock the SSLCommerz response
        mock_instance = MagicMock()
        mock_instance.createSession.return_value = {
            'status': 'SUCCESS',
            'GatewayPageURL': 'https://sandbox.sslcommerz.com/payment/page'
        }
        mock_sslcommerz.return_value = mock_instance
        
        response = self.client.post(self.create_enrollment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        
        # Check that no new enrollment was created
        self.assertEqual(Enrollment.objects.filter(
            user=self.user,
            contribution=self.contribution
        ).count(), 1)
    
    @patch('enrollments.views.SSLCOMMERZ')
    def test_create_enrollment_with_failed_payment(self, mock_sslcommerz):
        """Test creating an enrollment when there's a failed payment."""
        # Create a failed enrollment
        Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='FAILED'
        )
        
        # Mock the SSLCommerz response
        mock_instance = MagicMock()
        mock_instance.createSession.return_value = {
            'status': 'SUCCESS',
            'GatewayPageURL': 'https://sandbox.sslcommerz.com/payment/page'
        }
        mock_sslcommerz.return_value = mock_instance
        
        response = self.client.post(self.create_enrollment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        
        # Check that the enrollment was updated to pending
        enrollment = Enrollment.objects.get(user=self.user, contribution=self.contribution)
        self.assertEqual(enrollment.payment_status, 'PENDING')


class PaymentCallbackTest(TestCase):
    """Test cases for payment callback functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        # Create test contribution
        self.contribution = Contributions.objects.create(
            title='Test Contribution',
            description='Test Description',
            price=100.00,
            user=self.user
        )
        
        # Create a pending enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=self.contribution.price,
            payment_status='PENDING'
        )
        
        # Set up URLs for testing
        self.success_url = f'/api/payment/success/{str(self.enrollment.id)}/'
        self.fail_url = f'/api/payment/fail/{str(self.enrollment.id)}/'
        self.cancel_url = f'/api/payment/cancel/{str(self.enrollment.id)}/'
    
    @patch('enrollments.views.settings.SSLCOMMERZ')
    def test_payment_success_sandbox(self, mock_sslcommerz_settings):
        """Test successful payment in sandbox mode."""
        # Configure sandbox mode
        mock_sslcommerz_settings.get.return_value = True
        
        # Mock the settings properties
        with patch('enrollments.views.settings.PAYMENT_REDIRECT_URLS', 
                  {'SUCCESS': 'http://localhost:3000/success'}):
            response = self.client.post(self.success_url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that the enrollment was updated
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.payment_status, 'COMPLETED')
        self.assertIsNotNone(self.enrollment.payment_reference)
        self.assertEqual(self.enrollment.payment_method, 'SANDBOX')
    
    @patch('enrollments.views.SSLCOMMERZ')
    @patch('enrollments.views.settings.SSLCOMMERZ')
    def test_payment_success_production(self, mock_sslcommerz_settings, mock_sslcommerz):
        """Test successful payment in production mode."""
        # Configure production mode
        mock_sslcommerz_settings.get.return_value = False
        
        # Mock the SSLCommerz response
        mock_instance = MagicMock()
        mock_instance.validationTransaction.return_value = {
            'status': 'VALID'
        }
        mock_sslcommerz.return_value = mock_instance
        
        # Mock the settings properties
        with patch('enrollments.views.settings.PAYMENT_REDIRECT_URLS', 
                  {'SUCCESS': 'http://localhost:3000/success'}):
            # Create a POST request with required parameters
            response = self.client.post(
                self.success_url,
                {
                    'val_id': 'test_val_id',
                    'tran_id': str(self.enrollment.id),
                    'amount': '100.00',
                    'status': 'VALID'
                }
            )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that the enrollment was updated
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.payment_status, 'COMPLETED')
    
    def test_payment_fail(self):
        """Test failed payment."""
        # Mock the settings properties
        with patch('enrollments.views.settings.PAYMENT_REDIRECT_URLS', 
                  {'FAILED': 'http://localhost:3000/failed'}):
            response = self.client.post(self.fail_url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that the enrollment was updated
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.payment_status, 'FAILED')
    
    def test_payment_cancel(self):
        """Test cancelled payment."""
        # Mock the settings properties
        with patch('enrollments.views.settings.PAYMENT_REDIRECT_URLS', 
                  {'CANCELLED': 'http://localhost:3000/cancelled'}):
            response = self.client.post(self.cancel_url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that the enrollment was updated
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.payment_status, 'CANCELLED')

