from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Contributions, University, Department, MajorSubject
from auth_app.models import CustomUser


class APITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)

        # Create related objects
        self.university = University.objects.create(name="Test University")
        self.department = Department.objects.create(name="Test Department")
        self.major_subject = MajorSubject.objects.create(name="Test Major")

        # Create a contribution
        self.contribution = Contributions.objects.create(
            user=self.user,
            title="Test Contribution",
            description="This is a test contribution.",
            price=10.99,
            rating=4.5,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )

    def test_get_contribution_by_id(self):
        """Test retrieving a single contribution by ID."""
        response = self.client.get(f'/api/user-contributions/{str(self.contribution.id)}/')
        print(response.data)  # Debugging output
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data['data'])  # Access nested 'data'
        self.assertEqual(response.data['data']['title'], "Test Contribution")


    def test_add_contribution(self):
        """Test adding a new contribution."""
        data = {
            'title': "New Contribution",
            'description': "This is a new contribution.",
            'price': 15.99,
            'rating': 4.0,
            'related_University': str(self.university.id),  # UUID typecast to string
            'related_Department': str(self.department.id),  # UUID typecast to string
            'related_Major_Subject': str(self.major_subject.id)  # UUID typecast to string
        }
        response = self.client.post('/api/user-contributions/', data, format='json')
        print(response.data)  # Debugging output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('title', response.data['data'])  # Access nested 'data'
        self.assertEqual(response.data['data']['title'], "New Contribution")


    def test_update_contribution(self):
        """Test updating an existing contribution."""
        data = {
            'title': "Updated Contribution",
            'description': "This is an updated contribution.",
            'price': 20.99,
            'rating': 4.8,
            'related_University': str(self.university.id),  # UUID typecast to string
            'related_Department': str(self.department.id),  # UUID typecast to string
            'related_Major_Subject': str(self.major_subject.id)  # UUID typecast to string
        }
        response = self.client.put(f'/api/user-contributions/{str(self.contribution.id)}/', data, format='json')
        print(response.data)  # Debugging output
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data['data'])  # Access nested 'data'
        self.assertEqual(response.data['data']['title'], "Updated Contribution")


    def test_delete_contribution(self):
        """Test deleting a contribution."""
        response = self.client.delete(f'/api/user-contributions/{str(self.contribution.id)}/')
        print(response.data)  # Debugging output
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Contributions.objects.filter(id=self.contribution.id).exists())



from django.test import TestCase
from django.contrib.admin.sites import site
from api.models import (
    Contributions, ContributionTags, ContributionVideos, ContributionNotes,
    ContributionsComments, ContributionRatings
)

class ApiAdminTest(TestCase):
    def test_models_registered(self):
        """Test that all models are registered in the admin site."""
        models = [
            Contributions, ContributionTags, ContributionVideos,
            ContributionNotes, ContributionsComments, ContributionRatings
        ]
        for model in models:
            with self.subTest(model=model):
                self.assertIn(model, site._registry)





from api.models import (
    Contributions, ContributionTags, ContributionVideos, ContributionNotes,
     University, Department, MajorSubject
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
        self.tag = ContributionTags.objects.create(name="Test Tag")
        self.video = ContributionVideos.objects.create(title="Test Video")
        self.note = ContributionNotes.objects.create()
        self.university = University.objects.create(name="Test University")
        self.department = Department.objects.create(name="Test Department")
        self.major_subject = MajorSubject.objects.create(name="Test Major")

        # Create a contribution
        self.contribution = Contributions.objects.create(
            user=self.user,
            title="Test Contribution",
            description="This is a test contribution.",
            price=10.99,
            rating=4.5,
            related_University=self.university,
            related_Department=self.department,
            related_Major_Subject=self.major_subject
        )
        self.contribution.tags.add(self.tag)
        self.contribution.videos.add(self.video)
        self.contribution.notes.add(self.note)