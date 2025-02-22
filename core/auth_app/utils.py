import random
import string

def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))  # This ensures exactly 4 digits 