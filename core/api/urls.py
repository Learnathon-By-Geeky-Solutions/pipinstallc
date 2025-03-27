from django.urls import path
from .views import (
    ProfileView, UserInfoView, UserContributionView, EnrollmentView,CreateEnrollmentView,
    payment_success, payment_fail, payment_cancel, ContributionCommentView, AllContributionView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user-info/', UserInfoView.as_view(), name='add-user-info'),
    # contribution urls for registered user to view their contributions
    path('user-contributions/', UserContributionView.as_view(), name='contributions'),
    path('user-contributions/<str:pk>/', UserContributionView.as_view(), name='contributions-delete-update'),


    # contribution urls for all users to view all contributions
    # if pk is provided, view a single contribution,
    # if authenticated and enrolled show all elements,if not authenticated show only basic elements
    path('all-contributions/', AllContributionView.as_view(), name='all-contributions'),
    path('all-contributions/<str:pk>/', AllContributionView.as_view(), name='all-contributions-detail'),

    # enrollment urls
    # user can view their enrollments and create new enrollments
    path('enrollments/', EnrollmentView.as_view(), name='user-enrollments'),
    path('enrollments/<uuid:enrollment_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('create-enrollments/<uuid:contribution_id>/', CreateEnrollmentView.as_view(), name='enrollment-detail'),

    # payment urls
    path('payment/success/<uuid:enrollment_id>/', payment_success, name='payment_success'),
    path('payment/fail/<uuid:enrollment_id>/', payment_fail, name='payment_fail'),
    path('payment/cancel/<uuid:enrollment_id>/', payment_cancel, name='payment_cancel'),

    # contribution comment urls
    path('contribution-comments/<uuid:contribution_id>/', ContributionCommentView.as_view(), name='contribution-comments'), #view all comments inside a contribution
    path('contribution-comments/<uuid:contribution_id>/<uuid:comment_id>/', ContributionCommentView.as_view(), name='contribution-comments'), #delete or update a comment 
    path('contribution-comments/', ContributionCommentView.as_view(), name='contribution-comments'), #view all comments or create a new comment
    
]

