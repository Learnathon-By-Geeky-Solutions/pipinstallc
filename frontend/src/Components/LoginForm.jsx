import React, { useState } from 'react';
import '../styles/LoginForm.css';

function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Form submitted:', formData);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header" style={{fontSize: '1.25rem'}}>
          <p>Don't Have an account?<a href="/signup"><u>Sign up</u></a></p>
        </div>
        
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

          <button type="submit" className="login-btn">Login</button>

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
