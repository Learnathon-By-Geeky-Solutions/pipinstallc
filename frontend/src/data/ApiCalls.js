export const BaseUrl = "https://edusphare.pythonanywhere.com"

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
                email: username, // Sending as email field as expected by backend
                password: password
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

// Function to submit user contributions
export const addContribution = async (formData) => {
    try {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            return { 
                status: false, 
                message: "You must be logged in to add contributions" 
            };
        }
        
        const response = await fetch(`${BaseUrl}/api/user-contributions/`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            body: formData,
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error adding contribution:", error);
        return { 
            status: false, 
            message: "An error occurred while adding your contribution" 
        };
    }
}

// Function to get all contributions
export const getContributions = async () => {
    try {
        const response = await fetch(`${BaseUrl}/api/user-contributions/`, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error fetching contributions:", error);
        return { 
            status: false, 
            message: "An error occurred while fetching contributions" 
        };
    }
}

// Function to get user's own contributions
export const getUserContributions = async () => {
    try {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            return { 
                status: false, 
                message: "Authentication required" 
            };
        }
        
        const response = await fetch(`${BaseUrl}/api/user-contributions/`, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
        });
        
        const result = await response.json();
        
        // Check if response follows the format shown in the Postman example
        if (result.status === true && result.message === "Success" && Array.isArray(result.data)) {
            return result.data; // Return just the data array for easier handling
        } else if (Array.isArray(result)) {
            // For backwards compatibility, if the response is directly an array
            return result;
        } else {
            // Return an error message if data isn't available
            return { 
                status: false, 
                message: result.message || "Failed to load contributions" 
            };
        }
    } catch (error) {
        console.error("Error fetching user contributions:", error);
        return { 
            status: false, 
            message: "An error occurred while fetching your contributions" 
        };
    }
}

// Function to get a single contribution by ID
export const getContributionById = async (id) => {
    try {
        const accessToken = localStorage.getItem('access_token');
        
        const headers = {
            'Content-Type': 'application/json',
        };
        
        // Add authorization header if token is available
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }
        
        const response = await fetch(`${BaseUrl}/api/user-contributions/${id}/`, {
            method: "GET",
            headers: headers,
        });
        
        const result = await response.json();
        
        // Check if response follows the format shown in the Postman example
        if (result.status === true && result.message === "Success" && result.data) {
            return result.data; // Return just the data for easier handling
        } else if (result.id) {
            // For backwards compatibility, if the response directly has an ID
            return result;
        } else {
            // Return an error message if data isn't available
            return { 
                status: false, 
                message: result.message || "Failed to load contribution" 
            };
        }
    } catch (error) {
        console.error("Error fetching contribution:", error);
        return { 
            status: false, 
            message: "An error occurred while fetching the contribution" 
        };
    }
}

// Function to update a contribution
export const updateContribution = async (id, formData) => {
    try {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            return { 
                status: false, 
                message: "You must be logged in to update contributions" 
            };
        }
        
        const response = await fetch(`${BaseUrl}/api/user-contributions/${id}/`, {
            method: "PUT",
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            body: formData,
        });
        
        const result = await response.json();
        
        // Check if response follows the format shown in the Postman example
        if (result.status === true && result.message === "Success" && result.data) {
            return result.data;
        } else if (result.id) {
            // For backwards compatibility, if the response directly has an ID
            return result;
        } else {
            return { 
                status: result.status || false, 
                message: result.message || "Failed to update contribution" 
            };
        }
    } catch (error) {
        console.error("Error updating contribution:", error);
        return { 
            status: false, 
            message: "An error occurred while updating your contribution" 
        };
    }
}

// Function to delete a contribution
export const deleteContribution = async (id) => {
    try {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            return { 
                status: false, 
                message: "You must be logged in to delete contributions" 
            };
        }
        
        const response = await fetch(`${BaseUrl}/api/user-contributions/${id}/`, {
            method: "DELETE",
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
        });
        
        // For successful deletion (204 No Content), return success message
        if (response.status === 204) {
            return { 
                status: true, 
                message: "Contribution deleted successfully" 
            };
        }
        
        // If there's a response body, parse it
        try {
            const result = await response.json();
            
            // If response follows the format shown in the Postman example
            if (result.status !== undefined) {
                return {
                    status: result.status,
                    message: result.message || "Operation completed"
                };
            }
            
            return result;
        } catch {
            // If no JSON in response (like 204 No Content)
            return { 
                status: response.ok, 
                message: response.ok ? "Contribution deleted successfully" : "Failed to delete contribution" 
            };
        }
    } catch (error) {
        console.error("Error deleting contribution:", error);
        return { 
            status: false, 
            message: "An error occurred while deleting your contribution" 
        };
    }
}

