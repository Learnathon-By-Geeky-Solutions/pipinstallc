
from django.urls import path
from .views import ProfileView, UserInfoView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user-info/', UserInfoView.as_view(), name='add-user-info'),
]

