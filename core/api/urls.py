from django.urls import path
from .views import (
    ProfileView, UserInfoView, UserContributionView,
    ContributionAdsView, EnrollmentView, ContributionDetailsView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user-info/', UserInfoView.as_view(), name='add-user-info'),
    # contribution urls
    path('contributions/', UserContributionView.as_view(), name='contributions'),
    path('contributions/<str:pk>/', ContributionDetailsView.as_view(), name='contribution-detail'),
    path('contributions-ads/', ContributionAdsView.as_view(), name='contribution-ads'),
    # enrollment urls
    path('enrollments/', EnrollmentView.as_view(), name='user-enrollments'),
    path('enrollments/<uuid:contribution_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
]