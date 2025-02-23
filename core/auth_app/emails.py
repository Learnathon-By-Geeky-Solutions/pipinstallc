from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_otp
from .models import CustomUser



def send_otp_via_email(email):
    subject = 'Your Email Verification OTP'
    otp = generate_otp()
    message = f'Your OTP for email verification is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    
    try:
        # Send email
        send_mail(
            subject,
            message,
            email_from,
            [email],
            fail_silently=False,
        )
        
        # Update user's OTP in database
        user = CustomUser.objects.get(email=email)
        user.otp = otp
        user.save()
        
        return otp
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return None

def send_otp_via_email_forgot_password(email):
    subject = 'Your Password Reset OTP'
    otp = generate_otp()
    message = f'Your OTP for password reset is: {otp}'
    email_from = settings.EMAIL_HOST_USER

    try:
        # Send email
        send_mail(
            subject,
            message,
            email_from,
            [email],
            fail_silently=False,
        )
        
        # Update user's OTP in database 
        user = CustomUser.objects.get(email=email)
        user.otp = otp
        user.save()
        
        return otp
    except Exception as e:  
        print(f"Error sending email: {str(e)}")
        return None
    


