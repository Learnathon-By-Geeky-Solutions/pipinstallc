from django.test import TestCase
from api.models import (
    Contributions, Contribution_tags, contribution_videos, Contribution_notes,
    Contribution_origines, Enrollment
)
from auth_app.models import CustomUser

class ContributionModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Create related objects
        self.tag = Contribution_tags.objects.create(name="Test Tag")
        self.video = contribution_videos.objects.create(title="Test Video")
        self.note = Contribution_notes.objects.create()
        self.origine = Contribution_origines.objects.create(
            related_University="Test University",
            related_Department="Test Department",
            related_Major_Subject="Test Major"
        )

        # Create a contribution
        self.contribution = Contributions.objects.create(
            user=self.user,
            title="Test Contribution",
            description="This is a test contribution.",
            price=10.99,
            rating=4.5
        )
        self.contribution.tags.add(self.tag)
        self.contribution.videos.add(self.video)
        self.contribution.notes.add(self.note)
        self.contribution.origine.add(self.origine)

    def test_contribution_creation(self):
        """Test that a contribution is created successfully"""
        self.assertEqual(self.contribution.title, "Test Contribution")
        self.assertEqual(self.contribution.user, self.user)
        self.assertEqual(self.contribution.price, 10.99)
        self.assertEqual(self.contribution.rating, 4.5)
        self.assertIn(self.tag, self.contribution.tags.all())
        self.assertIn(self.video, self.contribution.videos.all())
        self.assertIn(self.note, self.contribution.notes.all())
        self.assertIn(self.origine, self.contribution.origine.all())

class EnrollmentModelTest(TestCase):
    def setUp(self):
        # Create a test user and contribution
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.contribution = Contributions.objects.create(
            user=self.user,
            title="Test Contribution"
        )

        # Create an enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=10.99,
            payment_status="COMPLETED",
            payment_reference="REF123",
            payment_method="Credit Card"
        )

    def test_enrollment_creation(self):
        """Test that an enrollment is created successfully"""
        self.assertEqual(self.enrollment.user, self.user)
        self.assertEqual(self.enrollment.contribution, self.contribution)
        self.assertEqual(self.enrollment.amount_paid, 10.99)
        self.assertEqual(self.enrollment.payment_status, "COMPLETED")
        self.assertEqual(self.enrollment.payment_reference, "REF123")
        self.assertEqual(self.enrollment.payment_method, "Credit Card")
