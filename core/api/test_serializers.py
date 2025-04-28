from django.test import TestCase
from api.models import (
    Contributions, Contribution_tags, contribution_videos, Contribution_notes, Enrollment
)
from auth_app.models import CustomUser
from api.serializers import (
    ContributionSerializer, ContributionTagSerializer, ContributionVideoSerializer,
    ContributionNoteSerializer, EnrollmentSerializer
)

class ContributionTagSerializerTest(TestCase):
    def test_contribution_tag_serializer(self):
        """Test ContributionTagSerializer"""
        tag = Contribution_tags.objects.create(name="Test Tag")
        serializer = ContributionTagSerializer(tag)
        self.assertEqual(serializer.data['name'], "Test Tag")

class ContributionVideoSerializerTest(TestCase):
    def test_contribution_video_serializer(self):
        """Test ContributionVideoSerializer"""
        video = contribution_videos.objects.create(title="Test Video")
        serializer = ContributionVideoSerializer(video)
        self.assertEqual(serializer.data['title'], "Test Video")

class ContributionNoteSerializerTest(TestCase):
    def test_contribution_note_serializer(self):
        """Test ContributionNoteSerializer"""
        note = Contribution_notes.objects.create()
        serializer = ContributionNoteSerializer(note)
        self.assertIn('id', serializer.data)

class ContributionSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.tag = Contribution_tags.objects.create(name="Test Tag")
        self.video = contribution_videos.objects.create(title="Test Video")
        self.note = Contribution_notes.objects.create()
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

    def test_contribution_serializer(self):
        """Test ContributionSerializer"""
        serializer = ContributionSerializer(self.contribution)
        self.assertEqual(serializer.data['title'], "Test Contribution")
        self.assertEqual(serializer.data['description'], "This is a test contribution.")
        self.assertEqual(serializer.data['price'], "10.99")
        self.assertEqual(serializer.data['rating'], "4.5")
        self.assertEqual(len(serializer.data['tags']), 1)
        self.assertEqual(len(serializer.data['videos']), 1)
        self.assertEqual(len(serializer.data['notes']), 1)

class EnrollmentSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.contribution = Contributions.objects.create(
            user=self.user,
            title="Test Contribution"
        )
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            contribution=self.contribution,
            amount_paid=10.99,
            payment_status="COMPLETED"
        )

    def test_enrollment_serializer(self):
        """Test EnrollmentSerializer"""
        serializer = EnrollmentSerializer(self.enrollment)
        self.assertEqual(serializer.data['amount_paid'], "10.99")
        self.assertEqual(serializer.data['payment_status'], "COMPLETED")