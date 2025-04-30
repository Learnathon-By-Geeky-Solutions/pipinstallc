from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ContributionSerializer, ContributionCommentSerializer, AllContributionSerializer, ContributionRatingSerializer,UniversitySerializer,MajorSubjectSerializer,DepartmentSerializer
from .models import Contributions, ContributionsComments, ContributionRatings, University, Department, MajorSubject,ContributionVideos,ContributionNotes,ContributionTags

from django.conf import settings
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import  LimitOffsetPagination
from django.core.cache import cache
from django.db.models import Prefetch
from enrollments.models import Enrollment

# Define constants for repeated string literals
INVALID_DATA_MSG = 'Invalid data'
NOT_FOUND_MSG = 'Not found'
CONTRIBUTIONS_LIST_PATTERN = 'contributions_list:*'
GENERIC_ERROR_MSG = 'An error occurred while processing your request'


class OptimizedPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


# Helper methods to reduce code duplication
def create_success_response(message, data=None, status_code=status.HTTP_200_OK):
    """Create a standardized success response"""
    response_data = {
        'status': True,
        'message': message
    }
    if data is not None:
        response_data['data'] = data
    return Response(response_data, status=status_code)

def create_error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Create a standardized error response"""
    response_data = {
        'status': False,
        'message': message
    }
    if errors is not None:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)





class UserInfoView(APIView):
    """
    Add user info.
    """
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        data = request.data.copy()
        
        # Map the incoming IDs to the appropriate serializer fields
        if 'university' in data and data['university']:
            data['university_id'] = data.pop('university')
        
        if 'department' in data and data['department']:
            data['department_id'] = data.pop('department')
        
        if 'major_subject' in data and data['major_subject']:
            data['major_subject_id'] = data.pop('major_subject')
            
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                'User info updated successfully',
                serializer.data
            )
        return create_error_response(INVALID_DATA_MSG, serializer.errors)
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return create_success_response(
            'User info fetched successfully',
            serializer.data
        )

class UniversityView(APIView):
    """
    API View for handling University operations
    GET: List all universities or get a specific university
    POST: Create a new university
    """
    def get(self, request, pk=None):
        try:
            if pk:
                university = University.objects.get(id=pk)
                serializer = UniversitySerializer(university)
                return create_success_response('University fetched successfully', serializer.data)
            
            universities = University.objects.all()
            serializer = UniversitySerializer(universities, many=True)
            return create_success_response('Universities fetched successfully', serializer.data)
            
        except ObjectDoesNotExist:
            return create_error_response('University not found', status_code=status.HTTP_404_NOT_FOUND)
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = UniversitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_success_response(
                    'University created successfully', 
                    serializer.data, 
                    status_code=status.HTTP_201_CREATED
                )
            
            return create_error_response(INVALID_DATA_MSG, serializer.errors)
            
        except IntegrityError:
            return create_error_response('University with this name already exists')
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentView(APIView):
    """
    API View for handling Department operations
    GET: List all departments or get a specific department
    POST: Create a new department
    """
    def get(self, request, pk=None):
        try:
            if pk:
                department = Department.objects.get(id=pk)
                serializer = DepartmentSerializer(department)
                return create_success_response('Department fetched successfully', serializer.data)
            
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
            return create_success_response('Departments fetched successfully', serializer.data)
            
        except ObjectDoesNotExist:
            return create_error_response('Department not found', status_code=status.HTTP_404_NOT_FOUND)
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = DepartmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_success_response(
                    'Department created successfully', 
                    serializer.data, 
                    status_code=status.HTTP_201_CREATED
                )
            
            return create_error_response(INVALID_DATA_MSG, serializer.errors)
            
        except IntegrityError:
            return create_error_response('Department with this name already exists')
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MajorSubjectView(APIView):
    """
    API View for handling MajorSubject operations
    GET: List all major subjects or get a specific major subject
    POST: Create a new major subject
    """
    def get(self, request, pk=None):
        try:
            if pk:
                major_subject = MajorSubject.objects.get(id=pk)
                serializer = MajorSubjectSerializer(major_subject)
                return create_success_response('Major Subject fetched successfully', serializer.data)
            
            major_subjects = MajorSubject.objects.all()
            serializer = MajorSubjectSerializer(major_subjects, many=True)
            return create_success_response('Major Subjects fetched successfully', serializer.data)
            
        except ObjectDoesNotExist:
            return create_error_response('Major Subject not found', status_code=status.HTTP_404_NOT_FOUND)
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = MajorSubjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_success_response(
                    'Major Subject created successfully', 
                    serializer.data, 
                    status_code=status.HTTP_201_CREATED
                )
            
            return create_error_response(INVALID_DATA_MSG, serializer.errors)
            
        except IntegrityError:
            return create_error_response('Major Subject with this name already exists')
        except Exception:
            return create_error_response(GENERIC_ERROR_MSG, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserContributionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = OptimizedPagination  # Using the same pagination class as AllContributionView

    def get(self, request, pk=None):
        user = request.user
        if pk:
            try:
                contribution = Contributions.objects.get(id=pk, user=user)
                serializer = ContributionSerializer(contribution)
                return create_success_response('Success', serializer.data)
            except Contributions.DoesNotExist:
                return create_error_response(NOT_FOUND_MSG, status_code=status.HTTP_404_NOT_FOUND)
        
        # Get filter parameter for major subject
        major_subject_id = request.query_params.get('major_subject')
        
        # Get all contributions from the user
        contributions = Contributions.objects.filter(user=user)
        
        # Apply major subject filter if provided
        if major_subject_id:
            try:
                contributions = contributions.filter(related_Major_Subject_id=major_subject_id)
            except Exception:
                return create_error_response('Invalid major subject ID')
        
        # Order by newest first
        contributions = contributions.order_by('-created_at')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_contributions = paginator.paginate_queryset(contributions, request)
        
        serializer = ContributionSerializer(paginated_contributions, many=True)
        
        # Create response with pagination details
        response_data = {
            'status': True,
            'message': 'Success',
            'filters_applied': {
                'major_subject': major_subject_id if major_subject_id else None
            },
            'pagination': {
                'count': paginator.count,
                'next': request.build_absolute_uri(paginator.get_next_link()) if paginator.get_next_link() else None,
                'previous': request.build_absolute_uri(paginator.get_previous_link()) if paginator.get_previous_link() else None,
                'limit': paginator.limit,
                'offset': paginator.offset,
            },
            'data': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        # Create a properly structured data dictionary using the helper method
        parsed_data = self._prepare_post_data(request)
        
        # Create the serializer with our properly structured data
        serializer = ContributionSerializer(data=parsed_data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            
            # Invalidate cache for list views
            cache.delete_pattern(CONTRIBUTIONS_LIST_PATTERN) if hasattr(cache, 'delete_pattern') else cache.clear()
            
            return create_success_response('Created', serializer.data, status_code=status.HTTP_201_CREATED)
        
        # Log validation errors for debugging
        logger.error(f"Validation errors: {serializer.errors}")
        
        return create_error_response(INVALID_DATA_MSG, serializer.errors)

    def _prepare_post_data(self, request):
        """Helper method to prepare contribution data from request for post"""
        # Create base data dictionary
        parsed_data = {
            'title': request.data.get('title', ''),
            'description': request.data.get('description', ''),
            'price': request.data.get('price', 0),
            'related_University': request.data.get('related_University', ''),
            'related_Department': request.data.get('related_Department', ''),
            'related_Major_Subject': request.data.get('related_Major_Subject', ''),
        }
        
        # Handle thumbnail image
        if 'thumbnail_image' in request.FILES:
            parsed_data['thumbnail_image'] = request.FILES['thumbnail_image']
        
        # Process tags, videos and notes
        parsed_data.update(self._process_tags(request))
        parsed_data.update(self._process_post_videos(request))
        parsed_data.update(self._process_notes(request))
        
        return parsed_data
        
    def _process_post_videos(self, request):
        """Process videos specifically for post method"""
        result = {}
        videos = []
        video_titles = {}
        video_files = {}
        
        # First collect all video data
        for key in request.data:
            if key.startswith('videos[') and '][title]' in key:
                index = key.split('[')[1].split(']')[0]
                video_titles[index] = request.data[key]
        
        for key in request.FILES:
            if 'video_file' in key:
                # Extract index from key like 'videos[0].[video_file]'
                index = key.split('[')[1].split(']')[0]
                video_files[index] = request.FILES[key]
        
        # Now create video objects
        for index in set(list(video_titles.keys()) + list(video_files.keys())):
            video = {}
            if index in video_titles:
                video['title'] = video_titles[index]
            if index in video_files:
                video['video_file'] = video_files[index]
            if video:
                videos.append(video)
        
        if videos:
            result['videos'] = videos
            
        return result

    def _process_tags(self, request):
        """Extract tags from request data"""
        result = {}
        tags = []
        for key in request.data:
            if key.startswith('tags[') and key.endswith('][name]'):
                tags.append({'name': request.data[key]})
        if tags:
            result['tags'] = tags
        return result
    
    def _process_notes(self, request):
        """Extract notes from request data"""
        result = {}
        notes = []
        for key in request.FILES:
            if 'note_file' in key:
                notes.append({'note_file': request.FILES[key]})
        
        if notes:
            result['notes'] = notes
        
        return result

    def put(self, request, pk):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contribution = Contributions.objects.get(id=pk, user=request.user)
        except Contributions.DoesNotExist:
            return create_error_response(NOT_FOUND_MSG, status_code=status.HTTP_404_NOT_FOUND)
        
        # Extract contribution data processing to reduce complexity
        parsed_data = self._prepare_contribution_data(request, contribution)
        
        serializer = ContributionSerializer(contribution, data=parsed_data, partial=True)
        if serializer.is_valid():
            try:
                updated_contribution = serializer.save()
                
                # Invalidate cache for this contribution and list views
                cache.delete(f"contribution_detail:{pk}")
                cache.delete_pattern(CONTRIBUTIONS_LIST_PATTERN) if hasattr(cache, 'delete_pattern') else cache.clear()
                
                return create_success_response(
                    'Updated', 
                    ContributionSerializer(updated_contribution).data
                )
            except Exception:
                logger.error("Error updating contribution")
                return create_error_response(GENERIC_ERROR_MSG)
        
        logger.error(f"Validation errors: {serializer.errors}")
        return create_error_response(INVALID_DATA_MSG, serializer.errors)

    def delete(self, request, pk):
        try:
            contribution = Contributions.objects.get(id=pk, user=request.user)
            contribution.delete()
            
            # Invalidate cache for this contribution and list views
            cache.delete(f"contribution_detail:{pk}")
            cache.delete_pattern(CONTRIBUTIONS_LIST_PATTERN) if hasattr(cache, 'delete_pattern') else cache.clear()
            
            return create_success_response('Deleted')
        except Contributions.DoesNotExist:
            return create_error_response(NOT_FOUND_MSG, status_code=status.HTTP_404_NOT_FOUND)

    def _prepare_contribution_data(self, request, contribution):
        """Helper method to prepare contribution data from request"""
        # Create a properly structured data dictionary
        parsed_data = {
            'title': request.data.get('title', contribution.title),
            'description': request.data.get('description', contribution.description),
            'price': request.data.get('price', contribution.price),
            'related_University': request.data.get('related_University', contribution.related_University_id),
            'related_Department': request.data.get('related_Department', contribution.related_Department_id),
            'related_Major_Subject': request.data.get('related_Major_Subject', contribution.related_Major_Subject_id),
        }
        
        # Handle thumbnail image
        if 'thumbnail_image' in request.FILES:
            parsed_data['thumbnail_image'] = request.FILES['thumbnail_image']
        
        # Process tags
        parsed_data.update(self._process_tags(request))
        
        # Process videos
        parsed_data.update(self._process_videos(request))
        
        # Process notes - reusing the method defined earlier
        parsed_data.update(self._process_notes(request))
        
        return parsed_data
    
    def _process_videos(self, request):
        """Extract videos from request data"""
        result = {}
        videos = []
        video_titles = {}
        video_files = {}
        
        # Extract video titles
        for key in request.data:
            if key.startswith('videos[') and '][title]' in key:
                index = key.split('[')[1].split(']')[0]
                video_titles[index] = request.data[key]
        
        # Extract video files
        for key in request.FILES:
            if 'video_file' in key:
                index = key.split('[')[1].split(']')[0]
                video_files[index] = request.FILES[key]
        
        # Combine titles and files
        for index in set(list(video_titles.keys()) + list(video_files.keys())):
            video = {}
            if index in video_titles:
                video['title'] = video_titles[index]
            if index in video_files:
                video['video_file'] = video_files[index]
            if video:
                videos.append(video)
        
        if videos:
            result['videos'] = videos
        
        return result
    
    # Using the first implementation of _process_notes defined at line 364
    # This eliminates duplication and reduces complexity

class AllContributionView(APIView):
    """
    Get all contributions with optional filtering and optimized pagination
    with filters: GET /api/all-contributions/?university=uuid1&limit=10&offset=0
    
    Pagination:
    - Use limit and offset: ?limit=10&offset=20
    - Default limit: 10
    - Max limit: 100
    
    Filtering:
    - Filter by university: ?university=<uuid>
    - Filter by department: ?department=<uuid>
    - Filter by major_subject: ?major_subject=<uuid>
    - Filter by tag: ?tag=<tag_name>
    - Filter by user: ?user=<uuid> (to find a specific user's contributions)
    - Can combine multiple filters
    
    Optimizations:
    - Database-level pagination
    - Efficient querying of related fields
    - Optional caching for frequently accessed pages
    """
    pagination_class = OptimizedPagination

    def get_cached_key(self, params):
        """Generate a cache key based on request parameters"""
        # Create a more robust cache key that includes all filter parameters
        param_keys = sorted(params.keys())
        key_parts = []
        
        for key in param_keys:
            value = params.get(key, '')
            if value:  # Only include non-empty parameters
                key_parts.append(f"{key}:{value}")
                
        # If no parameters, use 'all' to indicate no filters
        key_string = "-".join(key_parts) if key_parts else "all"
        return f"contributions_list:{key_string}"

    def get(self, request, pk=None):
        # For individual contribution detail view
        if pk:
            return self._get_contribution_detail(request, pk)

        # For listing view with millions of records
        return self._get_contribution_list(request)
        
    def _get_contribution_detail(self, request, pk):
        # For individual contribution, use a different cache key
        cache_key = f"contribution_detail:{pk}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
            
        try:
            # Only select the related fields we actually need
            contribution = Contributions.objects.select_related(
                'related_University',
                'related_Department',
                'related_Major_Subject',
                'user'
            ).prefetch_related(
                'tags',
                Prefetch('videos', queryset=ContributionVideos.objects.only('id', 'title', 'video_file')),
                Prefetch('notes', queryset=ContributionNotes.objects.only('id', 'note_file')),
                
            ).get(id=pk)
            
            serializer = AllContributionSerializer(contribution, context={'request': request})
            response_data = {
                'status': True,
                'message': 'Contribution fetched successfully',
                'data': serializer.data
            }
            
            # Cache individual contribution detail
            cache_timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('contribution_detail', 600)
            cache.set(cache_key, response_data, timeout=cache_timeout)
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Contributions.DoesNotExist:
            return create_error_response('Contribution not found', status_code=status.HTTP_404_NOT_FOUND)
            
    def _get_contribution_list(self, request):
        # Build filter query params
        filter_params = {}
        university_id = request.query_params.get('university')
        department_id = request.query_params.get('department')
        major_subject_id = request.query_params.get('major_subject')
        user_id = request.query_params.get('user')
        tag_name = request.query_params.get('tag')
        
        # Try to get cached response for this specific query
        cache_key = self.get_cached_key(request.query_params)
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # Get filtered contributions queryset
        contributions = self._get_filtered_contributions(
            filter_params, 
            university_id, 
            department_id, 
            major_subject_id, 
            user_id, 
            tag_name
        )
        
        contributions = contributions.order_by('-created_at')
        
        # Get count efficiently without retrieving all objects
        try:
            total_count = contributions.count()
        except Exception :
            # Fallback if count() is too slow
            total_count = None
        
        # Apply pagination - critical for millions of records
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(contributions, request)
        
        # Process paginated results
        response_data = self._process_paginated_results(
            paginated_qs, 
            request, 
            total_count, 
            paginator, 
            university_id, 
            department_id, 
            major_subject_id, 
            user_id, 
            tag_name
        )

        # Get cache timeout from settings or use default (5 minutes)
        cache_timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('contributions_list', 300)
        cache.set(cache_key, response_data, timeout=cache_timeout)

        return Response(response_data, status=status.HTTP_200_OK)
        
    def _get_filtered_contributions(self, filter_params, university_id, department_id, major_subject_id, user_id, tag_name):
        # Start with optimized queryset - only select needed fields to reduce memory usage
        # For large datasets, we want to be very specific about what we fetch
        contributions = Contributions.objects.only(
            'id', 
            'title', 
            'thumbnail_image', 
            'price', 
            'rating', 
            'created_at',
            'user_id',
            'related_University_id',
            'related_Department_id',
            'related_Major_Subject_id'
        )
        
        # Process all ID filters
        filter_params = self._apply_id_filters(filter_params, university_id, department_id, major_subject_id, user_id)
        
        # Apply all filters at once for better performance
        if filter_params:
            contributions = contributions.filter(**filter_params)
        
        # Apply tag filter separately since it requires a more complex lookup
        if tag_name:
            try:
                contributions = contributions.filter(tags__name__icontains=tag_name).distinct()
            except Exception:
                return create_error_response('Invalid tag name')
                
        return contributions
    
    def _apply_id_filters(self, filter_params, university_id, department_id, major_subject_id, user_id):
        """Helper method to apply ID filters to reduce complexity"""
        # Apply direct filter conditions for better performance
        if university_id:
            try:
                filter_params['related_University_id'] = university_id
            except Exception:
                return create_error_response('Invalid university ID')
                
        if department_id:
            try:
                filter_params['related_Department_id'] = department_id
            except Exception:
                return create_error_response('Invalid department ID')
                
        if major_subject_id:
            try:
                filter_params['related_Major_Subject_id'] = major_subject_id
            except Exception:
                return create_error_response('Invalid major subject ID')
                
        if user_id:
            try:
                filter_params['user_id'] = user_id
            except Exception:
                return create_error_response('Invalid user ID')
        
        return filter_params
        
    def _process_paginated_results(self, paginated_qs, request, total_count, paginator, university_id, department_id, major_subject_id, user_id, tag_name):
        # Only after pagination, load the related objects for the paginated subset
        # This is key for handling millions of records - only load relations for the current page
        ids_in_page = [item.id for item in paginated_qs]
        if ids_in_page:
            # Now get complete data only for the paginated items
            detailed_contributions = Contributions.objects.filter(id__in=ids_in_page).select_related(
                'related_University',
                'related_Department',
                'related_Major_Subject',
                'user'
            ).prefetch_related(
                'tags',
                Prefetch('videos', queryset=ContributionVideos.objects.only('id', 'title', 'video_file')),
                Prefetch('notes', queryset=ContributionNotes.objects.only('id', 'note_file')),
                
            ).order_by('-created_at')
            
            serializer = AllContributionSerializer(detailed_contributions, many=True, context={'request': request})
        else:
            serializer = AllContributionSerializer([], many=True, context={'request': request})
        
        # Build response with pagination details
        return {
            'status': True,
            'message': 'Contributions fetched successfully',
            'filters_applied': {
                'university': university_id if university_id else None,
                'department': department_id if department_id else None,
                'major_subject': major_subject_id if major_subject_id else None,
                'tag': tag_name if tag_name else None,
                'user': user_id if user_id else None
            },
            'pagination': {
                'count': total_count,
                'next': request.build_absolute_uri(paginator.get_next_link()) if paginator.get_next_link() else None,
                'previous': request.build_absolute_uri(paginator.get_previous_link()) if paginator.get_previous_link() else None,
                'limit': paginator.limit,
                'offset': paginator.offset,
            },
            'data': serializer.data
        }




class ContributionCommentView(APIView):
    """
    Handle contribution comments
    user can add comments to a contribution
    user can view comments of a contribution
    user can delete comments of a contribution
    user can update comments of a contribution

    """
    permission_classes = [IsAuthenticated]

    def get(self, request, contribution_id=None):
        """
        if contribution_id is provided, get all comments of a contribution
        if no contribution_id is provided, get all comments
        """
        if contribution_id:
            contribution = get_object_or_404(Contributions, id=contribution_id)
            comments = ContributionsComments.objects.filter(contribution=contribution)
            serializer = ContributionCommentSerializer(comments, many=True)
        else:
            comments = ContributionsComments.objects.all()
            serializer = ContributionCommentSerializer(comments, many=True)
        return create_success_response('Comments fetched successfully', serializer.data)

    def post(self, request):
        """
        create a new comment
        """
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ContributionCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                'Comment Posted successfully',
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return create_error_response(INVALID_DATA_MSG, serializer.errors)



    def delete(self, request, contribution_id, comment_id):
        """
        delete a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(ContributionsComments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            comment.delete()
            return create_success_response('Comment deleted successfully')
        else:
            return create_error_response(
                'You do not have permission to delete this comment',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
    def put(self, request, contribution_id, comment_id):
        """
        update a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(ContributionsComments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            data = request.data.copy()
            data['user'] = request.user.id
            serializer = ContributionCommentSerializer(comment, data=data)
            if serializer.is_valid():
                serializer.save()
                return create_success_response('Comment updated successfully', serializer.data)
        else:
            return create_error_response(
                'You do not have permission to update this comment',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
class ContributionRatingView(APIView):
    """
    User can rate a contribution
    User can view ratings of a contribution
    Rating is stored as a decimal value between 0 and 5
    The contribution's rating field is updated with the average of all ratings
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, contribution_id):
        """
        Get all ratings for a contribution or the user's rating if exists
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        
        # Check if user wants their own rating
        user_rating_only = request.query_params.get('user_rating', 'false').lower() == 'true'
        
        if user_rating_only:
            # Get user's rating if it exists
            rating = ContributionRatings.objects.filter(
                user=request.user,
                contribution=contribution
            ).first()
            
            if rating:
                serializer = ContributionRatingSerializer(rating)
                return create_success_response('User rating fetched successfully', serializer.data)
            else:
                return create_error_response(
                    'You have not rated this contribution yet',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get all ratings for the contribution
            ratings = ContributionRatings.objects.filter(contribution=contribution)
            serializer = ContributionRatingSerializer(ratings, many=True)
            
            return create_success_response('Ratings fetched successfully', {
                'average_rating': contribution.rating,
                'total_ratings': ratings.count(),
                'ratings': serializer.data
            })
    
    def post(self, request, contribution_id):
        """
        Create or update a rating for a contribution
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        
        # Check if user is enrolled in this contribution
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            contribution=contribution,
            payment_status='COMPLETED'
        ).exists()
        
        if not is_enrolled:
            return create_error_response(
                'You must be enrolled in this contribution to rate it',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Add user and contribution to request data
        data = request.data.copy()
        data['user'] = request.user.id
        data['contribution'] = contribution_id
        
        # Validate rating value
        rating_value = data.get('rating')
        try:
            rating_value = float(rating_value)
            if rating_value < 0 or rating_value > 5:
                return create_error_response(
                    'Rating must be between 0 and 5',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return create_error_response(
                'Rating must be a number between 0 and 5',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ContributionRatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            # The signal handler will update the contribution's rating automatically
            
            return create_success_response(
                'Rating submitted successfully',
                {'rating': serializer.data},
                status_code=status.HTTP_201_CREATED
            )
        
        return create_error_response(INVALID_DATA_MSG, serializer.errors)


