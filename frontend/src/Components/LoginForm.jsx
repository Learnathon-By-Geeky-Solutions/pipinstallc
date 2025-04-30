import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/LoginForm.css';
import { login } from '../data/ApiCalls';

function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Check if redirected from verification page
  useEffect(() => {
    if (location.state?.verificationSuccess) {
      setMessage({
        text: location.state.message || 'Email verified successfully. You can now log in.',
        type: 'success'
      });
    }
  }, [location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Basic validation
    if (!formData.email || !formData.password) {
      setMessage({ text: 'Please enter both email and password', type: 'error' });
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage({ text: 'Please enter a valid email address', type: 'error' });
      return;
    }

    setIsLoading(true);
    setMessage({ text: '', type: '' });
    try {
      const response = await login(formData.email, formData.password);
      
      if (response.status) {
        setMessage({ text: response.message || 'Login successful!', type: 'success' });
        // Store user data and tokens in localStorage
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        // Redirect to home page after successful login
        setTimeout(() => {
          navigate('/');
        }, 1500);
      } else {
        // Handle server validation errors
        let errorMessage = response.message || 'Invalid credentials';
        
        // Check if the response contains detailed error information
        if (response.errors) {
          const errors = response.errors;
          if (errors.non_field_errors) {
            errorMessage = errors.non_field_errors[0];
          } else if (errors.email) {
            errorMessage = errors.email[0];
          } else if (errors.password) {
            errorMessage = errors.password[0];
          }
        }
        
        setMessage({ text: errorMessage, type: 'error' });
      }
    } catch (error) {
      console.error('Login error:', error);
      setMessage({ text: 'An error occurred during login', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>Welcome Back!</h2>
          <p>New to Edusphere? <a href="/signup">Sign up</a></p>
        </div>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">
              <i className="fas fa-envelope"></i> Email
            </label>
            <div className="input-wrapper">
              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="password">
              <i className="fas fa-lock"></i> Password
            </label>
            <div className="input-wrapper">
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
            </div>
          </div>
          
          <div className="form-options">
            <label className="remember-me">
              <input
                type="checkbox"
                checked={formData.rememberMe}
                onChange={(e) => setFormData({...formData, rememberMe: e.target.checked})}
              />
              <span>Remember me</span>
            </label>
            <a href="/forgot-password" className="forgot-password">Forgot Password?</a>
          </div>
          
          <button type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Logging in...
              </>
            ) : (
              <>
                <i className="fas fa-sign-in-alt"></i>
                Login
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
