from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Enrollment


@receiver(post_save, sender=Enrollment)
def enrollment_saved(sender, instance, created, **kwargs):
    """
    Signal handler that runs when an enrollment is created or updated.
    This ensures that enrollment changes take effect immediately.
    """
    # Invalidate cache for this user's enrollments
    cache.delete(f"user_enrollments:{instance.user.id}")
    
    # Invalidate cache for this contribution's enrollments
    cache.delete(f"contribution_enrollments:{instance.contribution.id}")
    
    # Invalidate cache for the contribution detail
    cache.delete(f"contribution_detail:{instance.contribution.id}")
    
    # Clear general caches that might include enrollment information
    contribution_cache_patterns = [
        f"contributions_list:*",
        f"user_contributions:{instance.user.id}:*"
    ]
    
    # Clear cache patterns if available, otherwise clear all cache
    for pattern in contribution_cache_patterns:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
    
    # Update contribution is_enrolled status in real-time
    # This ensures frontend immediately knows user is enrolled
    if instance.payment_status == 'COMPLETED':
        from api.serializers import update_contribution_enrollment_status
        update_contribution_enrollment_status(instance.contribution, instance.user)


@receiver(post_delete, sender=Enrollment)
def enrollment_deleted(sender, instance, **kwargs):
    """
    Signal handler that runs when an enrollment is deleted.
    Ensures that deleted enrollments take effect immediately.
    """
    # Same cache invalidation as for saves
    cache.delete(f"user_enrollments:{instance.user.id}")
    cache.delete(f"contribution_enrollments:{instance.contribution.id}")
    cache.delete(f"contribution_detail:{instance.contribution.id}")
    
    contribution_cache_patterns = [
        f"contributions_list:*",
        f"user_contributions:{instance.user.id}:*"
    ]
    
    for pattern in contribution_cache_patterns:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern) 