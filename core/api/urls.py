from django.urls import path
from .views import (
    ProfileView, UserInfoView, UserContributionView,
    ContributionAdsView, EnrollmentView, ContributionDetailsView,CreateEnrollmentView,
    payment_success, payment_fail, payment_cancel
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
    path('enrollments/<uuid:enrollment_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('create-enrollments/<uuid:contribution_id>/', CreateEnrollmentView.as_view(), name='enrollment-detail'),

    # payment urls
    path('payment/success/<uuid:enrollment_id>/', payment_success, name='payment_success'),
    path('payment/fail/<uuid:enrollment_id>/', payment_fail, name='payment_fail'),
    path('payment/cancel/<uuid:enrollment_id>/', payment_cancel, name='payment_cancel'),
]

