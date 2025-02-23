
from django.urls import path
from .views import ProfileView, UserInfoView, UserContributionView,ContributionAdsView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user-info/', UserInfoView.as_view(), name='add-user-info'),
    #contribution urls
    path('contributions/', UserContributionView.as_view(), name='contributions'),
    path('contributions/<str:pk>/', UserContributionView.as_view(), name='contribution-detail'),
    path('contributions-ads/', ContributionAdsView.as_view(), name='contribution-ads'),
]

