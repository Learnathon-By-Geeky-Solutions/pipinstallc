from django.db import models
from django.conf import settings
from api.models import Contributions
# Create your models here.
from uuid import uuid4


class Enrollment(models.Model):
    """
    Model for tracking user enrollments in contributions
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
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

