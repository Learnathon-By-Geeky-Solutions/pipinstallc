from django.urls import path
from .views import (
    ProfileView, UserInfoView, UserContributionView, 
    ContributionCommentView, AllContributionView,
    ContributionRatingView, UniversityView, DepartmentView, MajorSubjectView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user-info/', UserInfoView.as_view(), name='add-user-info'),
    # contribution urls for registered user to view their contributions
    path('user-contributions/', UserContributionView.as_view(), name='contributions'),
    path('user-contributions/<str:pk>/', UserContributionView.as_view(), name='contributions-delete-update'),

    path('all-contributions/', AllContributionView.as_view(), name='all-contributions'),
    path('all-contributions/<str:pk>/', AllContributionView.as_view(), name='all-contributions-detail'),


    path('contribution-comments/<uuid:contribution_id>/', ContributionCommentView.as_view(), name='contribution-comments'), #view all comments inside a contribution
    path('contribution-comments/<uuid:contribution_id>/<uuid:comment_id>/', ContributionCommentView.as_view(), name='contribution-comments'), #delete or update a comment 
    path('contribution-comments/', ContributionCommentView.as_view(), name='contribution-comments'), #view all comments or create a new comment

    path('ratings/<uuid:contribution_id>/', ContributionRatingView.as_view(), name='contribution-ratings'),

    # University, Department, and MajorSubject views
    path('universities/', UniversityView.as_view(), name='universities'),
    path('universities/<int:pk>/', UniversityView.as_view(), name='university-detail'),
    path('departments/', DepartmentView.as_view(), name='departments'),
    path('departments/<int:pk>/', DepartmentView.as_view(), name='department-detail'),
    path('major-subjects/', MajorSubjectView.as_view(), name='major-subjects'),
    path('major-subjects/<int:pk>/', MajorSubjectView.as_view(), name='major-subject-detail'),
]

