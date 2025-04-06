from django.db import models
from uuid import uuid4
from auth_app.models import CustomUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Contributions(models.Model):
    """
    Model for storing contributions of users.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, related_name='contributions', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnail_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tags = models.ManyToManyField('Contribution_tags', related_name='contributions')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
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


class Contribution_origines(models.Model):
    """
    Model for storing origins of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='origine', on_delete=models.CASCADE)
    related_University = models.CharField(max_length=255, null=True, blank=True)
    related_Department = models.CharField(max_length=255, null=True, blank=True)
    related_Major_Subject = models.CharField(max_length=255, null=True, blank=True)


class Contribution_notes(models.Model):
    """
    Model for storing notes of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='notes', on_delete=models.CASCADE)
    note_file = models.FileField(upload_to='contribution_notes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contributions_comments(models.Model):
    """
    Model for storing comments of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    contribution = models.ForeignKey(Contributions, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user and self.user.username:
            return self.user.username
        return f"Comment {self.id}"


class Contribution_ratings(models.Model):
    """
    Model for storing ratings of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    contribution = models.ForeignKey(Contributions, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
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
    contribution = models.ForeignKey(Contributions, on_delete=models.CASCADE, related_name='enrollments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)  # Store SSLCommerz transaction reference
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # Store payment method used
    
    class Meta:
        unique_together = ['user', 'contribution']  # Prevent duplicate enrollments


@receiver([post_save, post_delete], sender='api.Contribution_ratings')
def update_contribution_rating(sender, instance, **kwargs):
    """
    Update the contribution's average rating whenever a rating is added, updated, or deleted
    """
    contribution = instance.contribution
    ratings = Contribution_ratings.objects.filter(contribution=contribution)
    
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





