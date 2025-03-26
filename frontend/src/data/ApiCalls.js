export const BaseUrl = "http://127.0.0.1:8000"

export const signup = async (data) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/register/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: data.name,
                email: data.email,
                password: data.password,
                password2: data.confirmPassword
            }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error during signup:", error);
        return { status: false, message: "An error occurred during registration" };
    }
}

// Add this new function for OTP verification
export const verifyOtp = async (email, otp) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/verify-email/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                otp
            }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error during OTP verification:", error);
        return { status: false, message: "An error occurred during verification" };
    }
}

// Add this function to resend OTP if needed
export const resendOtp = async (email) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/resend-otp/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email
            }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error resending OTP:", error);
        return { status: false, message: "An error occurred while resending OTP" };
    }
}

// Add this new function for user login
export const login = async (username, password) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/login/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password
            }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error during login:", error);
        return { status: false, message: "An error occurred during login" };
    }
}

// Function to check if user is logged in
export const isLoggedIn = () => {
    return localStorage.getItem('user') !== null;
}

// Function to get current user data
export const getCurrentUser = () => {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

// Update the logout function to include authorization header
export const logout = async () => {
    try {
        // Get the tokens from localStorage
        const refreshToken = localStorage.getItem('refresh_token');
        const accessToken = localStorage.getItem('access_token');
        
        if (refreshToken && accessToken) {
            // Call the logout endpoint with authorization
            const response = await fetch(`${BaseUrl}/auth/logout/`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({
                    refresh: refreshToken
                }),
            });
            
            // Check if the logout was successful
            if (response.ok) {
                console.log("Logged out successfully on the server");
            } else {
                console.warn("Server logout failed, but proceeding with client-side logout");
            }
        }
    } catch (error) {
        console.error("Error during logout:", error);
    } finally {
        // Always clear local storage, even if the API call fails
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
}

// Function to request password reset
export const forgotPassword = async (email) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/forgot-password/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error requesting password reset:", error);
        return { 
            status: false, 
            message: "An error occurred while requesting password reset" 
        };
    }
}

// Function to reset password with OTP
export const resetPassword = async (email, otp, password, password2) => {
    try {
        const response = await fetch(`${BaseUrl}/auth/reset-password/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                otp,
                password,
                password2
            }),
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error resetting password:", error);
        return { 
            status: false, 
            message: "An error occurred while resetting password" 
        };
    }
}

