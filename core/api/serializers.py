from rest_framework import serializers
from auth_app.models import CustomUser
from .models import Contributions, contribution_videos, Contribution_tags, Contribution_origines, Contribution_notes, Enrollment
from django.shortcuts import get_object_or_404


"""
Serializer for custom User model.
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'is_email_verified', 'phone_number', 'is_profile_verified', 'date_of_birth', 'university', 'department', 'major_subject']










class ContributionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = contribution_videos
        fields = '__all__'

class ContributionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution_tags
        fields = '__all__'

class ContributionOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution_origines
        fields = '__all__'

class ContributionNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution_notes
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Contribution model.
    '''
    videos = ContributionVideoSerializer(many=True, required=False)
    tags = ContributionTagSerializer(many=True, required=False)
    origine = ContributionOriginSerializer(many=True, required=False)
    notes = ContributionNoteSerializer(many=True, required=False)

    class Meta:
        model = Contributions
        fields = '__all__'

    def create(self, validated_data):
        # Pop nested data
        videos_data = validated_data.pop('videos', [])
        tags_data = validated_data.pop('tags', [])
        origine_data = validated_data.pop('origine', [])
        notes_data = validated_data.pop('notes', [])

        # Create the contribution
        contribution = Contributions.objects.create(**validated_data)

        # Create and add related objects only if they exist and aren't None
        if videos_data:
            for video_data in videos_data:
                if video_data:  # Check if video data is not None
                    video = contribution_videos.objects.create(**video_data)
                    contribution.videos.add(video)

        if tags_data:
            for tag_data in tags_data:
                if tag_data:  # Check if tag data is not None
                    tag = Contribution_tags.objects.create(**tag_data)
                    contribution.tags.add(tag)

        if origine_data:
            for origin_data in origine_data:
                if origin_data:  # Check if origin data is not None
                    origin = Contribution_origines.objects.create(**origin_data)
                    contribution.origine.add(origin)

        if notes_data:
            for note_data in notes_data:
                if note_data:  # Check if note data is not None
                    note = Contribution_notes.objects.create(**note_data)
                    contribution.notes.add(note)

        return contribution

    def update(self, instance, validated_data):
        # Handle nested updates
        videos_data = validated_data.pop('videos', [])
        tags_data = validated_data.pop('tags', [])
        origine_data = validated_data.pop('origine', [])
        notes_data = validated_data.pop('notes', [])

        # Update the main instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update related objects only if they exist and aren't None
        if videos_data is not None:
            instance.videos.clear()
            for video_data in videos_data:
                if video_data:
                    video = contribution_videos.objects.create(**video_data)
                    instance.videos.add(video)

        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                if tag_data:
                    tag = Contribution_tags.objects.create(**tag_data)
                    instance.tags.add(tag)

        if origine_data is not None:
            instance.origine.clear()
            for origin_data in origine_data:
                if origin_data:
                    origin = Contribution_origines.objects.create(**origin_data)
                    instance.origine.add(origin)

        if notes_data is not None:
            instance.notes.clear()
            for note_data in notes_data:
                if note_data:
                    note = Contribution_notes.objects.create(**note_data)
                    instance.notes.add(note)

        instance.save()
        return instance


class ContributionBasicAdsSerializer(serializers.ModelSerializer):
    tags = ContributionTagSerializer(many=True, required=False)
    origine = ContributionOriginSerializer(many=True, required=False)
    class Meta:
        model = Contributions
        fields = ['id', 'title', 'description' ,'price','thumbnail_image','tags','origine','rating']

class ContributionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed contribution view based on enrollment status
    """
    videos = ContributionVideoSerializer(many=True, required=False)
    tags = ContributionTagSerializer(many=True, required=False)
    origine = ContributionOriginSerializer(many=True, required=False)
    notes = ContributionNoteSerializer(many=True, required=False)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Contributions
        fields = '__all__'

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(
                user=request.user,
                payment_status='COMPLETED'
            ).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # request = self.context.get('request')
        
        # Remove sensitive data if user is not enrolled
        if not self.get_is_enrolled(instance):
            data.pop('videos', None)
            data.pop('notes', None)
        
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for enrollment model.
    user can get all their enrollments and add new enrollments
    user must be authenticated to enroll in a contribution
    
    """
    user = UserSerializer(read_only=True)
    contribution = ContributionDetailSerializer(read_only=True)

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
    
    
