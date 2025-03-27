import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { verifyOtp, resendOtp } from '../data/ApiCalls';
import '../styles/ConfirmOtp.css';

function ConfirmOtp() {
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [resendDisabled, setResendDisabled] = useState(false);
  const [countdown, setCountdown] = useState(0);
  
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get email from location state or localStorage
  const email = location.state?.email || localStorage.getItem('verificationEmail');
  
  useEffect(() => {
    // If no email is found, redirect to signup
    if (!email) {
      navigate('/signup');
    } else {
      // Store email in localStorage for persistence
      localStorage.setItem('verificationEmail', email);
    }
  }, [email, navigate]);
  
  useEffect(() => {
    // Countdown timer for resend button
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setResendDisabled(false);
    }
  }, [countdown]);

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
    
    if (!otp) {
      setMessage({ text: 'Please enter the OTP', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await verifyOtp(email, otp);
      console.log("API Response:", response); // For debugging
      
      if (response.status) {
        // Display the exact message from the API
        setMessage({ 
          text: response.message || 'Email verified successfully', 
          type: 'success' 
        });
        
        // Clear email from localStorage
        localStorage.removeItem('verificationEmail');
        
        // Redirect to login after successful verification
        setTimeout(() => {
          navigate('/login', { 
            state: { 
              verificationSuccess: true,
              message: response.message || 'Email verified successfully'
            } 
          });
        }, 2000);
      } else {
        // Extract and display the error message
        const errorMessage = extractErrorMessage(response.message);
        setMessage({ 
          text: errorMessage || 'Verification failed. Please check your OTP and try again.', 
          type: 'error' 
        });
        // Clear the OTP input to let the user try again
        setOtp('');
      }
    } catch (error) {
      console.error("Verification error:", error);
      setMessage({ 
        text: 'An error occurred during verification. Please try again.', 
        type: 'error' 
      });
      // Clear the OTP input to let the user try again
      setOtp('');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleResendOtp = async () => {
    setResendDisabled(true);
    setCountdown(60); // Disable resend for 60 seconds
    setMessage({ text: '', type: '' });
    
    try {
      const response = await resendOtp(email);
      
      if (response.status) {
        setMessage({ 
          text: response.message || 'OTP resent successfully. Please check your email.', 
          type: 'success' 
        });
      } else {
        // Extract and display the error message
        const errorMessage = extractErrorMessage(response.message);
        setMessage({ 
          text: errorMessage || 'Failed to resend OTP. Please try again.', 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error("Resend OTP error:", error);
      setMessage({ 
        text: 'An error occurred while resending OTP. Please try again.', 
        type: 'error' 
      });
    }
  };

  return (
    <div className="otp-container">
      <div className="otp-card">
        <div className="otp-header">
          <h2>Verify Your Email</h2>
        </div>
        
        <p className="otp-instruction">
          We've sent a verification code to <strong>{email}</strong>. 
          Please enter the code below to verify your email address.
        </p>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Verification Code</label>
            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
            />
          </div>

          <button 
            type="submit" 
            className="verify-btn" 
            disabled={isLoading}
          >
            {isLoading ? 'Verifying...' : 'Verify Email'}
          </button>
        </form>
        
        <div className="resend-otp">
          <p>
            Didn't receive the code?{' '}
            <button 
              onClick={handleResendOtp} 
              disabled={resendDisabled}
              className="resend-btn"
            >
              {resendDisabled ? `Resend in ${countdown}s` : 'Resend OTP'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default ConfirmOtp;
