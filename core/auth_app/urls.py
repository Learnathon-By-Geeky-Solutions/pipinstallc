
from django.urls import path
from .views import RegisterView, LoginView, LogoutView, VerifyEmailView, ResendOTPView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),#fist user have to send the otp to the email
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),#then user have to enter the otp and new password
]

