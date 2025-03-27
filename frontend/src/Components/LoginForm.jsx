import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/LoginForm.css';
import { login } from '../data/ApiCalls';

function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',
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
    if (!formData.username || !formData.password) {
      setMessage({ text: 'Please enter both username and password', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await login(formData.username, formData.password);
      
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
        // Handle error message
        let errorMessage = response.message;
        if (typeof errorMessage === 'object') {
          // Extract error message from object if needed
          if (errorMessage.non_field_errors && errorMessage.non_field_errors.length > 0) {
            errorMessage = errorMessage.non_field_errors[0];
          } else {
            errorMessage = 'Invalid credentials. Please try again.';
          }
        }
        
        setMessage({ text: errorMessage || 'Login failed', type: 'error' });
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
        <div className="login-header" style={{fontSize: '1.25rem'}}>
          <p>Don't Have an account?<a href="/signup"><u>Sign up</u></a></p>
        </div>
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
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
            <a href="/forgot-password" className="forgot-password">Forgot Password</a>
          </div>

          <button 
            type="submit" 
            className="login-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>

          <div className="divider">
            <span>or</span>
          </div>

          <button type="button" className="google-btn">
            <img src={"images/google.png"} alt="Google" />
            Login with Google
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
