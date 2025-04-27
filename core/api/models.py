from django.db import models
from uuid import uuid4
from auth_app.models import CustomUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



class ContributionVideos(models.Model):
    """
    Model for storing contribution videos.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    video_file = models.FileField(upload_to='contribution_videos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)

class ContributionTags(models.Model):
    """
    Model for storing tags of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)

class ContributionOrigines(models.Model):
    """
    Model for storing origins of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    related_University = models.CharField(max_length=255, blank=True)
    related_Department = models.CharField(max_length=255, blank=True)
    related_Major_Subject = models.CharField(max_length=255, blank=True)

class ContributionNotes(models.Model):
    """
    Model for storing notes of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note_file = models.FileField(upload_to='contribution_notes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contribution(models.Model):
    """
    Model for storing contributions of users.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, related_name='contributions', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnail_images/', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.ManyToManyField(ContributionTags, related_name='contributions')
    videos = models.ManyToManyField(ContributionVideos, related_name='contributions')
    notes = models.ManyToManyField(ContributionNotes, related_name='contributions')
    origine = models.ManyToManyField(ContributionOrigines, related_name='contributions', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            return self.title
        return f"Contribution {self.id}"


class contribution_videos(models.Model):
    """
    Model for storing contribution videos.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    video_file = models.FileField(upload_to='contribution_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contribution_tags(models.Model):
    """
    Model for storing tags of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)



class Contribution_notes(models.Model):
    """
    Model for storing notes of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='notes', on_delete=models.CASCADE)
    note_file = models.FileField(upload_to='contribution_notes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContributionComments(models.Model):
    """
    Model for storing comments of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    comment = models.TextField(blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user and self.user.username:
            return self.user.username
        return f"Comment {self.id}"

class ContributionRatings(models.Model):
    """
    Model for storing ratings of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user and self.user.username:
            return self.user.username
        return f"Rating {self.id}"
    
    class Meta:
        unique_together = ['user', 'contribution']  # Prevent duplicate ratings


class Enrollment(models.Model):
    """
    Model for tracking user enrollments in contributions
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='enrollments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_reference = models.CharField(max_length=100, blank=True)  # Store SSLCommerz transaction reference
    payment_method = models.CharField(max_length=50, blank=True)  # Store payment method used
    
    class Meta:
        unique_together = ['user', 'contribution']  # Prevent duplicate enrollments






@receiver([post_save, post_delete], sender=ContributionRatings)
def update_contribution_rating(sender, instance, **kwargs):
    """
    Update the contribution's average rating whenever a rating is added, updated, or deleted
    """
    contribution = instance.contribution
    ratings = ContributionRatings.objects.filter(contribution=contribution)
    
    if ratings.exists():
        # Calculate average rating
        from django.db.models import Avg
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        # Round to 2 decimal places
        contribution.rating = round(avg_rating, 2)
    else:
        # No ratings, set to None
        contribution.rating = None
    
    contribution.save(update_fields=['rating'])





