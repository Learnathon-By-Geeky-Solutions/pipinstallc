from django.test import TestCase
from django.contrib.admin.sites import site
from api.models import (
    Contributions, Contribution_tags, contribution_videos, Contribution_notes,
    Enrollment, Contributions_comments, Contribution_ratings
)

class ApiAdminTest(TestCase):
    def test_models_registered(self):
        """Test that all models are registered in the admin site."""
        models = [
            Contributions, Contribution_tags, contribution_videos,
            Contribution_notes, Enrollment, Contributions_comments,
            Contribution_ratings
        ]
        for model in models:
            with self.subTest(model=model):
                self.assertIn(model, site._registry)