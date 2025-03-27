import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { forgotPassword } from '../data/ApiCalls';
import '../styles/ForgotPass.css';

function ForgotPass() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!email) {
      setMessage({ text: 'Please enter your email address', type: 'error' });
      return;
    }
    
    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setMessage({ text: 'Please enter a valid email address', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await forgotPassword(email);
      
      if (response.status) {
        setMessage({ 
          text: response.message || 'Password reset OTP sent successfully. Please check your email.', 
          type: 'success' 
        });
        
        // Store email in localStorage for the reset password page
        localStorage.setItem('resetEmail', email);
        
        // Redirect to reset password page after a delay
        setTimeout(() => {
          navigate('/reset-password', { state: { email } });
        }, 2000);
      } else {
        // Extract and display the error message
        const errorMessage = extractErrorMessage(response.message);
        setMessage({ 
          text: errorMessage || 'Failed to send password reset OTP. Please try again.', 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error("Forgot password error:", error);
      setMessage({ 
        text: 'An error occurred while requesting password reset. Please try again.', 
        type: 'error' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <div className="forgot-password-header">
          <h2>Forgot Password</h2>
        </div>
        
        <p className="forgot-password-instruction">
          Enter your email address below and we'll send you instructions to reset your password.
        </p>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <button 
            type="submit" 
            className="reset-btn" 
            disabled={isLoading}
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
          
          <div className="back-to-login">
            <p>Remember your password? <a href="/login">Back to Login</a></p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ForgotPass;
