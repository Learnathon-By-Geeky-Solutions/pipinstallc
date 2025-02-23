import React from 'react';
import Navbar from '../Components/Navbar';
import LoginForm from '../Components/LoginForm';
import '../styles/Login.css';

function Login() {
  return (
    <div className="login-page">
      <Navbar />
      <div className="login-content">
        <LoginForm />
      </div>
    </div>
  );
}

export default Login; 