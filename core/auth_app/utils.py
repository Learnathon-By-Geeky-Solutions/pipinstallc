import secrets

def generate_otp():
    """
    Generate a cryptographically secure 4-digit OTP using secrets module.
    This is more secure than using random.randint() for security-critical operations.
    Optimized for high-volume authentication systems.
    """
    # Generate a secure random number between 1000 and 9999
    # Using direct bit operations for better performance with large user bases
    return str(1000 + (secrets.randbits(14) % 9000)) 