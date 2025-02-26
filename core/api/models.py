from django.db import models
from uuid import uuid4
from auth_app.models import CustomUser



class contribution_videos(models.Model):
    """
    Model for storing contribution videos.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255,null=True,blank=True)
    video_file = models.FileField(upload_to='contribution_videos/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)

class Contribution_tags(models.Model):
    """
    Model for storing tags of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,blank=True)

class Contribution_origines(models.Model):
    """
    Model for storing origins of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    related_University = models.CharField(max_length=255,null=True,blank=True)
    related_Department = models.CharField(max_length=255,null=True,blank=True)
    related_Major_Subject = models.CharField(max_length=255,null=True,blank=True)

class Contribution_notes(models.Model):
    """
    Model for storing notes of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note_file = models.FileField(upload_to='contribution_notes/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Contributions(models.Model):
    """
    Model for storing contributions of users.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, related_name='contributions', on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnail_images/',null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    tags = models.ManyToManyField(Contribution_tags, related_name='contributions')
    videos = models.ManyToManyField(contribution_videos, related_name='contributions')
    notes = models.ManyToManyField(Contribution_notes,  related_name='contributions')
    origine = models.ManyToManyField(Contribution_origines, related_name='contributions', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        ('FAILED', 'Failed')
    ], default='PENDING')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'contribution']  # Prevent duplicate enrollments





