import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { resetPassword } from '../data/ApiCalls';
import '../styles/ResetPassword.css';

function ResetPassword() {
  const [formData, setFormData] = useState({
    otp: '',
    email: '',
    password: '',
    password2: ''
  });
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get email from location state or localStorage
  useEffect(() => {
    const emailFromState = location.state?.email;
    const emailFromStorage = localStorage.getItem('resetEmail');
    
    if (emailFromState || emailFromStorage) {
      setFormData(prev => ({ ...prev, email: emailFromState || emailFromStorage }));
    } else {
      // If no email is found, redirect to forgot password page
      navigate('/forgot-password');
    }
  }, [location.state, navigate]);
  
  // Helper function to extract error message from API response
  const extractErrorMessage = (messageObj) => {
    if (typeof messageObj === 'string') {
      return messageObj;
    }
    
    if (messageObj && typeof messageObj === 'object') {
      // Check for non_field_errors array
      if (messageObj.non_field_errors && Array.isArray(messageObj.non_field_errors)) {
        return messageObj.non_field_errors[0];
      }
      
      // Check for other error fields
      for (const key in messageObj) {
        if (Array.isArray(messageObj[key])) {
          return messageObj[key][0];
        }
      }
      
      // If we can't find a specific error, stringify the object
      return JSON.stringify(messageObj);
    }
    
    return 'An error occurred. Please try again.';
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.otp) {
      setMessage({ text: 'Please enter the OTP sent to your email', type: 'error' });
      return;
    }
    
    if (!formData.password) {
      setMessage({ text: 'Please enter a new password', type: 'error' });
      return;
    }
    
    if (formData.password.length < 6) {
      setMessage({ text: 'Password must be at least 6 characters long', type: 'error' });
      return;
    }
    
    if (formData.password !== formData.password2) {
      setMessage({ text: 'Passwords do not match', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await resetPassword(
        formData.email,
        formData.otp,
        formData.password,
        formData.password2
      );
      
      if (response.status) {
        setMessage({ 
          text: response.message || 'Password reset successful!', 
          type: 'success' 
        });
        
        // Clear email from localStorage
        localStorage.removeItem('resetEmail');
        
        // Redirect to login page after successful password reset
        setTimeout(() => {
          navigate('/login', { 
            state: { 
              passwordResetSuccess: true,
              message: 'Password reset successful. You can now log in with your new password.'
            } 
          });
        }, 2000);
      } else {
        // Extract and display the error message
        const errorMessage = extractErrorMessage(response.message);
        setMessage({ 
          text: errorMessage || 'Failed to reset password. Please try again.', 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error("Password reset error:", error);
      setMessage({ 
        text: 'An error occurred while resetting password. Please try again.', 
        type: 'error' 
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        <div className="reset-password-header">
          <h2>Reset Password</h2>
        </div>
        
        <p className="reset-password-instruction">
          Enter the verification code sent to <strong>{formData.email}</strong> and your new password.
        </p>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="otp">Verification Code</label>
            <input
              id="otp"
              name="otp"
              type="text"
              placeholder="Enter OTP"
              value={formData.otp}
              onChange={handleChange}
              maxLength={6}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Enter new password"
              value={formData.password}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password2">Confirm New Password</label>
            <input
              id="password2"
              name="password2"
              type="password"
              placeholder="Confirm new password"
              value={formData.password2}
              onChange={handleChange}
            />
          </div>
          
          <button 
            type="submit" 
            className="reset-btn" 
            disabled={isLoading}
          >
            {isLoading ? 'Resetting...' : 'Reset Password'}
          </button>
          
          <div className="back-to-login">
            <p>Remember your password? <a href="/login">Back to Login</a></p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ResetPassword; 