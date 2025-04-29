from django.db import models
from uuid import uuid4
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class University(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed University"
    
    class Meta:
        verbose_name_plural = "Universities"


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed Department"


class MajorSubject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed Major Subject"

    class Meta:
        verbose_name_plural = "Major Subjects"


class Contributions(models.Model):
    """
    Model for storing contributions of users.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contributions', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnail_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    tags = models.ManyToManyField('ContributionTags', related_name='contributions')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, db_index=True)
    related_University = models.ForeignKey(University, related_name='contributions', on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    related_Department = models.ForeignKey(Department, related_name='contributions', on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    related_Major_Subject = models.ForeignKey(MajorSubject, related_name='contributions', on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            return self.title
        return f"Contribution {self.id}"

    class Meta:
        verbose_name_plural = "Contributions"
        indexes = [
            models.Index(fields=['created_at', 'rating']),
            models.Index(fields=['related_University', 'related_Department', 'related_Major_Subject']),
        ]


class contributionVideos(models.Model):
    """
    Model for storing contribution videos.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    video_file = models.FileField(upload_to='contribution_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContributionTags(models.Model):
    """
    Model for storing tags of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)



class ContributionNotes(models.Model):
    """
    Model for storing notes of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    contribution = models.ForeignKey(Contributions, related_name='notes', on_delete=models.CASCADE)
    note_file = models.FileField(upload_to='contribution_notes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContributionsComments(models.Model):
    """
    Model for storing comments of contributions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    contribution = models.ForeignKey(Contributions, on_delete=models.CASCADE, related_name='comments')
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
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



@receiver([post_save, post_delete], sender='api.ContributionRatings')
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





