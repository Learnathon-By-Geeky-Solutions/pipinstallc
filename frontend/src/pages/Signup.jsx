import React from 'react';
import Navbar from '../Components/Navbar';
import SignupForm from '../Components/SignupForm';
import '../styles/SignupForm.css';

function Signup() {
  return (
    <div className="signup-page">
      <Navbar />
      <div className="signup-content">
        <SignupForm />
      </div>
    </div>
  );
}

export default Signup; 