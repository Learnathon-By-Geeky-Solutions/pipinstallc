
from .models import  Enrollment
from django.shortcuts import get_object_or_404

from api.serializers import  UserSerializer,AllContributionSerializer,Contributions
from rest_framework import serializers


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for enrollment model.
    user can get all their enrollments and add new enrollments
    user must be authenticated to enroll in a contribution
    
    """
    user = UserSerializer(read_only=True)
    contribution = AllContributionSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'contribution', 'amount_paid', 'payment_status', 'enrolled_at']
        read_only_fields = ['id', 'created_at', 'user', 'contribution']

    def create(self, validated_data):
        """
        Create an enrollment record.
        """
        user = self.context['request'].user
        contribution_id = self.context['contribution_id']
        contribution = get_object_or_404(Contributions, id=contribution_id)
        
        return Enrollment.objects.create(
            user=user,
            contribution=contribution,
            **validated_data
        )
    
    
