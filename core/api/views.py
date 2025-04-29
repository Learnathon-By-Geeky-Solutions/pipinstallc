from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ContributionSerializer, ContributionCommentSerializer, AllContributionSerializer, ContributionRatingSerializer,UniversitySerializer,MajorSubjectSerializer,DepartmentSerializer
from .models import Contributions, ContributionsComments, ContributionRatings, University, Department, MajorSubject,contributionVideos,ContributionNotes,ContributionTags

from django.conf import settings
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import  LimitOffsetPagination
from django.core.cache import cache
from django.db.models import Prefetch
from enrollments.models import Enrollment


class ProfileView(APIView):
    """
    Get user profile data.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)   

        return Response(
            {
                'status': True,
                'message': 'User profile fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )


class UserInfoView(APIView):
    """
    Add user info.
    """
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'User info updated successfully',
                    'data':serializer.data
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(
            {
                'status': True,
                'message': 'User info fetched successfully',    
                'data': serializer.data
            },
            status=status.HTTP_200_OK
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
                return Response({
                    'status': True,
                    'message': 'University fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            universities = University.objects.all()
            serializer = UniversitySerializer(universities, many=True)
            return Response({
                'status': True,
                'message': 'Universities fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                'status': False,
                'message': 'University not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'status': False,
                'message': 'An error occurred while processing your request'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = UniversitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'message': 'University created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError:
            return Response({
                'status': False,
                'message': 'University with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception :
            return Response({
                'status': False,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                return Response({
                    'status': True,
                    'message': 'Department fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
            return Response({
                'status': True,
                'message': 'Departments fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                'status': False,
                'message': 'Department not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'status': False,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = DepartmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'message': 'Department created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError:
            return Response({
                'status': False,
                'message': 'Department with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                'status': False,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                return Response({
                    'status': True,
                    'message': 'Major Subject fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            major_subjects = MajorSubject.objects.all()
            serializer = MajorSubjectSerializer(major_subjects, many=True)
            return Response({
                'status': True,
                'message': 'Major Subjects fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                'status': False,
                'message': 'Major Subject not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'status': False,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = MajorSubjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'message': 'Major Subject created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError:
            return Response({
                'status': False,
                'message': 'Major Subject with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                'status': False,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserContributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            try:
                contribution = Contributions.objects.get(id=pk, user=user)
                serializer = ContributionSerializer(contribution)
                return Response({'status': True, 'message': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)
            except Contributions.DoesNotExist:
                return Response({'status': False, 'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        contributions = Contributions.objects.filter(user=user)
        serializer = ContributionSerializer(contributions, many=True)
        return Response({'status': True, 'message': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        # Log the incoming data for debugging
        logger.info(f"Request FILES: {request.FILES}")
        logger.info(f"Request DATA: {request.data}")
        
        # Create a properly structured data dictionary
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
        
        # Handle tags
        tags = []
        for key in request.data:
            if key.startswith('tags[') and key.endswith('][name]'):
                tags.append({'name': request.data[key]})
        if tags:
            parsed_data['tags'] = tags
        
        # Handle videos
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
            parsed_data['videos'] = videos
        
        # Handle notes
        notes = []
        for key in request.FILES:
            if 'note_file' in key:
                notes.append({'note_file': request.FILES[key]})
        
        if notes:
            parsed_data['notes'] = notes
        
        logger.info(f"Parsed data: {parsed_data}")
        
        # Create the serializer with our properly structured data
        serializer = ContributionSerializer(data=parsed_data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'status': True, 
                'message': 'Created', 
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        # Log validation errors for debugging
        logger.error(f"Validation errors: {serializer.errors}")
        
        return Response({
            'status': False, 
            'message': 'Invalid data', 
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contribution = Contributions.objects.get(id=pk, user=request.user)
        except Contributions.DoesNotExist:
            return Response({'status': False, 'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Log the incoming data for debugging
        logger.info(f"Request FILES: {request.FILES}")
        logger.info(f"Request DATA: {request.data}")
        
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
        
        # Handle tags
        tags = []
        for key in request.data:
            if key.startswith('tags[') and key.endswith('][name]'):
                tags.append({'name': request.data[key]})
        if tags:
            parsed_data['tags'] = tags
            
        # Handle videos
        videos = []
        video_titles = {}
        video_files = {}
        
        for key in request.data:
            if key.startswith('videos[') and '][title]' in key:
                index = key.split('[')[1].split(']')[0]
                video_titles[index] = request.data[key]
        
        for key in request.FILES:
            if 'video_file' in key:
                index = key.split('[')[1].split(']')[0]
                video_files[index] = request.FILES[key]
        
        for index in set(list(video_titles.keys()) + list(video_files.keys())):
            video = {}
            if index in video_titles:
                video['title'] = video_titles[index]
            if index in video_files:
                video['video_file'] = video_files[index]
            if video:
                videos.append(video)
        
        if videos:
            parsed_data['videos'] = videos
            
        # Handle notes
        notes = []
        for key in request.FILES:
            if 'note_file' in key:
                notes.append({'note_file': request.FILES[key]})
        
        if notes:
            parsed_data['notes'] = notes
        
        logger.info(f"Parsed data for update: {parsed_data}")
        
        serializer = ContributionSerializer(contribution, data=parsed_data, partial=True)
        if serializer.is_valid():
            try:
                updated_contribution = serializer.save()
                return Response({
                    'status': True, 
                    'message': 'Updated', 
                    'data': ContributionSerializer(updated_contribution).data
                }, status=status.HTTP_200_OK)
            except Exception:
                logger.error(f"Error updating contributin")
                return Response({
                    'status': False,
                    'message': f'Error updating contribution',
                }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.error(f"Validation errors: {serializer.errors}")
        return Response({
            'status': False, 
            'message': 'Invalid data', 
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            contribution = Contributions.objects.get(id=pk, user=request.user)
            contribution.delete()
            return Response({'status': True, 'message': 'Deleted'}, status=status.HTTP_200_OK)
        except Contributions.DoesNotExist:
            return Response({'status': False, 'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class OptimizedPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

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
    - Can combine multiple filters
    
    Optimizations:
    - Database-level pagination
    - Efficient querying of related fields
    - Optional caching for frequently accessed pages
    """
    pagination_class = OptimizedPagination

    def get_cached_key(self, params):
        """Generate a cache key based on request parameters"""
        return f"contributions_list:{params.get('university','')}-{params.get('department','')}-{params.get('major_subject','')}-{params.get('limit','')}-{params.get('offset','')}"

    def get(self, request, pk=None):
        if pk:
            try:
                contribution = Contributions.objects.select_related(
                    'related_University',
                    'related_Department',
                    'related_Major_Subject',
                    'user'
                ).prefetch_related(
                    'tags',
                    'videos',
                    'notes',
                    'comments'
                ).get(id=pk)
                
                serializer = AllContributionSerializer(contribution, context={'request': request})
                return Response({
                    'status': True,
                    'message': 'Contribution fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            except Contributions.DoesNotExist:
                return Response({
                    'status': False,
                    'message': 'Contribution not found'
                }, status=status.HTTP_404_NOT_FOUND)

        # Try to get cached response
        cache_key = self.get_cached_key(request.query_params)
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # Get filter parameters
        university_id = request.query_params.get('university')
        department_id = request.query_params.get('department')
        major_subject_id = request.query_params.get('major_subject')
        
        # Start with optimized queryset
        contributions = Contributions.objects.select_related(
            'related_University',
            'related_Department',
            'related_Major_Subject',
            'user'
        ).prefetch_related(
            'tags',
            Prefetch('videos', queryset=contributionVideos.objects.only('id', 'title', 'video_file')),
            Prefetch('notes', queryset=ContributionNotes.objects.only('id', 'note_file')),
            Prefetch('comments', queryset=ContributionsComments.objects.select_related('user').only(
                'id', 'comment', 'user__username', 'created_at'
            ))
        )
        
        # Apply filters if provided
        if university_id:
            try:
                contributions = contributions.filter(related_University_id=university_id)
            except Exception:
                return Response({
                    'status': False,
                    'message': f'Invalid university ID'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        if department_id:
            try:
                contributions = contributions.filter(related_Department_id=department_id)
            except Exception:
                return Response({
                    'status': False,
                    'message': f'Invalid department ID'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        if major_subject_id:
            try:
                contributions = contributions.filter(related_Major_Subject_id=major_subject_id)
            except Exception:
                return Response({
                    'status': False,
                    'message': f'Invalid major subject ID'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Add ordering by created_at (newest first)
        contributions = contributions.order_by('-created_at')

        # Apply pagination
        paginator = self.pagination_class()
        paginated_contributions = paginator.paginate_queryset(contributions, request)
        
        serializer = AllContributionSerializer(paginated_contributions, many=True, context={'request': request})
        
        response_data = {
            'status': True,
            'message': 'Contributions fetched successfully',
            'filters_applied': {
                'university': university_id if university_id else None,
                'department': department_id if department_id else None,
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

        # Cache the response for 5 minutes
        cache.set(cache_key, response_data, timeout=300)

        return Response(response_data, status=status.HTTP_200_OK)




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
        return Response(
            {
                'status': True,
                'message': 'Comments fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        create a new comment
        """
        serializer = ContributionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Comment Posted successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(
            {
                'status': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, contribution_id, comment_id):
        """
        delete a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(ContributionsComments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            comment.delete()
            return Response(
                {
                    'status': True,
                    'message': 'Comment deleted successfully',
                }, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'status': False,
                    'message': 'You do not have permission to delete this comment',
                }, status=status.HTTP_403_FORBIDDEN)
        
    def put(self, request, contribution_id, comment_id):
        """
        update a comment
        """
        contribution = get_object_or_404(Contributions, id=contribution_id)
        comment = get_object_or_404(ContributionsComments, id=comment_id, contribution=contribution)
        if comment.user.id == request.user.id:
            serializer = ContributionCommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'status': True,
                        'message': 'Comment updated successfully',
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'status': False,
                    'message': 'You do not have permission to update this comment',
                }, status=status.HTTP_403_FORBIDDEN)
        
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
                return Response({
                    'status': True,
                    'message': 'User rating fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': False,
                    'message': 'You have not rated this contribution yet'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get all ratings for the contribution
            ratings = ContributionRatings.objects.filter(contribution=contribution)
            serializer = ContributionRatingSerializer(ratings, many=True)
            
            return Response({
                'status': True,
                'message': 'Ratings fetched successfully',
                'data': {
                    'average_rating': contribution.rating,
                    'total_ratings': ratings.count(),
                    'ratings': serializer.data
                }
            }, status=status.HTTP_200_OK)
    
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
            return Response({
                'status': False,
                'message': 'You must be enrolled in this contribution to rate it'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Add user and contribution to request data
        data = request.data.copy()
        data['user'] = request.user.id
        data['contribution'] = contribution_id
        
        # Validate rating value
        rating_value = data.get('rating')
        try:
            rating_value = float(rating_value)
            if rating_value < 0 or rating_value > 5:
                return Response({
                    'status': False,
                    'message': 'Rating must be between 0 and 5'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({
                'status': False,
                'message': 'Rating must be a number between 0 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ContributionRatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            # The signal handler will update the contribution's rating automatically
            
            return Response({
                'status': True,
                'message': 'Rating submitted successfully',
                'data': {
                    'rating': serializer.data,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


