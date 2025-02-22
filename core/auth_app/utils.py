import secrets

def generate_otp():
    """
    Generate a cryptographically secure 4-digit OTP using secrets module.
    This is more secure than using random.randint() for security-critical operations.
    """
    # Generate a secure random number between 1000 and 9999
    return str(secrets.randbelow(9000) + 1000) 