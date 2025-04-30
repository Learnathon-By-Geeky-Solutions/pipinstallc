import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/SignupForm.css';
import { signup } from '../data/ApiCalls';

function SignupForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState({ text: '', type: '' });
  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setFieldErrors({});
    setMessage({ text: '', type: '' });
    
    // Basic validation
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setMessage({ text: 'All fields are required', type: 'error' });
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setMessage({ text: 'Passwords do not match', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Convert form data to match API expectations
      const apiFormData = {
        username: formData.name,
        email: formData.email,
        password: formData.password,
        password2: formData.confirmPassword
      };

      const response = await signup(apiFormData);
      
      if (response.status) {
        setMessage({ text: response.message, type: 'success' });
        // Redirect to OTP verification page with email
        setTimeout(() => {
          navigate('/verify-otp', { state: { email: formData.email } });
        }, 1500);
      } else {
        // Handle server-side validation errors
        if (response.errors) {
          const errors = response.errors;
          setFieldErrors(errors);
          
          // Set general error message
          setMessage({ 
            text: response.message || 'Please correct the errors below',
            type: 'error'
          });
        } else {
          setMessage({ 
            text: response.message || 'Registration failed', 
            type: 'error' 
          });
        }
      }
    } catch (error) {
      console.error("Registration error:", error);
      setMessage({ text: 'An error occurred during registration', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        <div className="signup-header">
          <h2>Sign Up</h2>
        </div>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className={fieldErrors.username ? 'input-error' : ''}
            />
            {fieldErrors.username && (
              <div className="field-error">{fieldErrors.username[0]}</div>
            )}
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className={fieldErrors.email ? 'input-error' : ''}
            />
            {fieldErrors.email && (
              <div className="field-error">{fieldErrors.email[0]}</div>
            )}
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className={fieldErrors.password ? 'input-error' : ''}
            />
            {fieldErrors.password && (
              <div className="field-error">{fieldErrors.password[0]}</div>
            )}
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              className={fieldErrors.password2 ? 'input-error' : ''}
            />
            {fieldErrors.password2 && (
              <div className="field-error">{fieldErrors.password2[0]}</div>
            )}
          </div>

          <button 
            type="submit" 
            className="signup-btn" 
            disabled={isLoading}
          >
            {isLoading ? 'Signing Up...' : 'Sign Up'}
          </button>

          <div className="divider">
            <span>or</span>
          </div>

          <button type="button" className="google-btn">
            <img src={"images/google.png"} alt="Google" />
            Sign up with Google
          </button>

          <div className="login-redirect">
            <p>Already have an account? <a href="/login"><u>Login</u></a></p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignupForm; 