from rest_framework import serializers
from auth_app.models import CustomUser
from .models import Contributions, ContributionVideos, ContributionTags, ContributionNotes, ContributionsComments, ContributionRatings,University,Department,MajorSubject
from django.shortcuts import get_object_or_404
from django.db import models
from enrollments.models import Enrollment
from django.core.cache import cache


# Define constants for repeated string literals
NAME_WHITESPACE_ERROR = "Name cannot be empty or just whitespace"

def update_contribution_enrollment_status(contribution, user):
    """
    Utility function to update a contribution's enrollment status for a specific user.
    This function is called by signal handlers to ensure real-time updates.
    
    Args:
        contribution: The Contribution instance
        user: The User instance
    """
    # This is a cache-busting operation to ensure real-time updates
    # for the frontend's is_enrolled status
    
    # Clear contribution detail cache for this specific user
    user_specific_cache_key = f"contribution_detail:{contribution.id}:user:{user.id}"
    cache.delete(user_specific_cache_key)
    
    # Clear general contribution detail cache
    cache.delete(f"contribution_detail:{contribution.id}")
    
    # Clear any cached serializer data that might include enrollment status
    contribution_list_cache_keys = [
        f"contributions_list:user:{user.id}",
        f"user_contributions:{user.id}:*"
    ]
    
    # Delete pattern-based cache keys if supported
    for key_pattern in contribution_list_cache_keys:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(key_pattern)
        
    # Force django to refresh the contribution from the database
    # in case it's cached in memory
    contribution.refresh_from_db()
    
    return True

"""
Serializer for custom User model.
"""

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name']

    def validate_name(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError(NAME_WHITESPACE_ERROR)
        return value

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

    def validate_name(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError(NAME_WHITESPACE_ERROR)
        return value

class MajorSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorSubject
        fields = ['id', 'name']

    def validate_name(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError(NAME_WHITESPACE_ERROR)
        return value
    
    
class UserSerializer(serializers.ModelSerializer):

    '''
    Serializer for custom User model.
    user can view their profile and update their profile
    user must be authenticated to view their profile
    user can view a single user by id
    '''
    university = UniversitySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    major_subject = MajorSubjectSerializer(read_only=True)
    
    # Fields that should be read-only and not modifiable by users
    is_email_verified = serializers.BooleanField(read_only=True)
    is_profile_verified = serializers.BooleanField(read_only=True)
    
    # Write-only fields for updating with just IDs
    university_id = serializers.UUIDField(write_only=True, required=False)
    department_id = serializers.UUIDField(write_only=True, required=False)
    major_subject_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'is_email_verified', 'phone_number', 'is_profile_verified', 'date_of_birth', 'university', 'department', 'major_subject', 'university_id', 'department_id', 'major_subject_id']
    
    def update(self, instance, validated_data):
        # Handle the ID fields and remove them from validated_data
        if 'university_id' in validated_data:
            instance.university_id = validated_data.pop('university_id')
        if 'department_id' in validated_data:
            instance.department_id = validated_data.pop('department_id')
        if 'major_subject_id' in validated_data:
            instance.major_subject_id = validated_data.pop('major_subject_id')
        
        # Update the instance with remaining fields
        return super().update(instance, validated_data)



class ContributionVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for contribution videos
    """
    video_file = serializers.FileField(required=False, allow_null=True)  # Make file optional

    class Meta:
        model = ContributionVideos
        fields = ['id', 'title', 'video_file']

class ContributionTagSerializer(serializers.ModelSerializer):
    """
    Serializer for contribution tags
    """

    class Meta:
        model = ContributionTags
        fields = '__all__'


class ContributionNoteSerializer(serializers.ModelSerializer):
    note_file = serializers.FileField(required=False, allow_null=True)  # Make file optional

    class Meta:
        model = ContributionNotes
        fields = ['id', 'note_file']

class ContributionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributionsComments
        fields = '__all__'



class ContributionRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for contribution ratings
    User can rate a contribution once
    If user already rated, update the existing rating
    """
    class Meta:
        model = ContributionRatings
        fields = ['id', 'user', 'contribution', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create or update a rating
        """
        user = validated_data.get('user')
        contribution = validated_data.get('contribution')
        
        # Check if user already rated this contribution
        existing_rating = ContributionRatings.objects.filter(
            user=user, 
            contribution=contribution
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = validated_data.get('rating')
            existing_rating.save()
            return existing_rating
        else:
            # Create new rating
            rating = ContributionRatings.objects.create(**validated_data)
            return rating


class ContributionSerializer(serializers.ModelSerializer):
    videos = ContributionVideoSerializer(many=True, required=False)
    tags = ContributionTagSerializer(many=True, required=False)
    notes = ContributionNoteSerializer(many=True, required=False)
    comments = ContributionCommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Contributions
        fields = '__all__'
    
    def create(self, validated_data):
        videos_data = validated_data.pop('videos', [])
        tags_data = validated_data.pop('tags', [])
        notes_data = validated_data.pop('notes', [])

        # Create the contribution
        contribution = Contributions.objects.create(**validated_data)

        # Create related objects
        for video_data in videos_data:
            ContributionVideos.objects.create(
                contribution=contribution, 
                **video_data
            )

        # Create tags
        for tag_data in tags_data:
            tag, _ = ContributionTags.objects.get_or_create(**tag_data)
            contribution.tags.add(tag)

        # Create notes
        for note_data in notes_data:
            ContributionNotes.objects.create(
                contribution=contribution, 
                **note_data
            )

        return contribution

    def _update_videos(self, instance, videos_data):
        """Helper method to update videos"""
        if videos_data is not None:
            # Delete existing videos
            instance.videos.all().delete()
            
            # Create new videos
            for video_data in videos_data:
                ContributionVideos.objects.create(
                    contribution=instance,
                    **video_data
                )

    def _update_tags(self, instance, tags_data):
        """Helper method to update tags"""
        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, _ = ContributionTags.objects.get_or_create(**tag_data)
                instance.tags.add(tag)

    def _update_notes(self, instance, notes_data):
        """Helper method to update notes"""
        if notes_data is not None:
            instance.notes.all().delete()
            for note_data in notes_data:
                ContributionNotes.objects.create(
                    contribution=instance,
                    **note_data
                )

    def update(self, instance, validated_data):
        videos_data = validated_data.pop('videos', None)
        tags_data = validated_data.pop('tags', None)
        notes_data = validated_data.pop('notes', None)

        # Update the main instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update related objects using helper methods
        self._update_videos(instance, videos_data)
        self._update_tags(instance, tags_data)
        self._update_notes(instance, notes_data)

        return instance

    def validate(self, data):
        """
        Custom validation to handle file uploads
        """
        # Video validation
        if 'videos' in data:
            for video in data['videos']:
                if 'video_file' not in video and 'title' not in video:
                    raise serializers.ValidationError({
                        'videos': 'Both video file and title are required for each video'
                    })

        # Notes validation
        if 'notes' in data:
            for note in data['notes']:
                if 'note_file' not in note:
                    raise serializers.ValidationError({
                        'notes': 'Note file is required for each note'
                    })

        return data



        
class AllContributionSerializer(serializers.ModelSerializer):
    """
    get all contributions
    show only title, description, price, thumbnail_image, tags, origine, rating, comments
    if user is authenticated, show the enrollment status and if enrolled show with all the elements available
    if user is not authenticated, show only the basic elements
    """
    tags = ContributionTagSerializer(many=True, read_only=True)
    comments = ContributionCommentSerializer(many=True, read_only=True)
    videos = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    related_University=UniversitySerializer()
    related_Department=DepartmentSerializer()
    related_Major_Subject=MajorSubjectSerializer()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Contributions
        fields = ['id', 'title', 'description', 'price', 'thumbnail_image', 
                  'tags', 'related_University', 'related_Department', 'related_Major_Subject', 'rating', 'comments', 'videos', 
                  'notes', 'is_enrolled', 'created_at', 'updated_at']
    
    def get_is_enrolled(self, obj):
        """Check if the requesting user is enrolled in this contribution"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                user=request.user,
                contribution=obj,
                payment_status='COMPLETED'
            ).exists()
        return False
    
    def get_videos(self, obj):
        """Return videos only if user is enrolled"""
        if self.get_is_enrolled(obj):
            videos = obj.videos.all()
            return ContributionVideoSerializer(videos, many=True).data
        return None
    
    def get_notes(self, obj):
        """Return notes only if user is enrolled"""
        if self.get_is_enrolled(obj):
            notes = obj.notes.all()
            return ContributionNoteSerializer(notes, many=True).data
        return None
    
    def to_representation(self, instance):
        """Customize the representation based on user authentication and enrollment"""
        data = super().to_representation(instance)
        
        # If videos and notes are None (user not enrolled), remove them from response
        if data['videos'] is None:
            data.pop('videos')
        if data['notes'] is None:
            data.pop('notes')
            
        return data



