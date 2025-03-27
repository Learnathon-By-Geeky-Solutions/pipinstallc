import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../Components/Navbar';
import '../styles/PaymentSuccess.css'; // We'll reuse the same CSS

function PaymentCancel() {
  const navigate = useNavigate();
  const location = useLocation();

  // Get the contribution ID from the URL if available
  const params = new URLSearchParams(location.search);
  const contributionId = params.get('contribution_id');

  return (
    <div className="payment-result-page">
      <Navbar />
      
      <div className="payment-result-container">
        <div className="payment-error">
          <div className="error-icon">⚠️</div>
          <h2>Payment Cancelled</h2>
          <p>You have cancelled the payment process. No charges were made to your account.</p>
          
          <div className="action-buttons">
            {contributionId && (
              <button 
                className="view-course-btn"
                onClick={() => navigate(`/contributions/${contributionId}`)}
              >
                Return to Course
              </button>
            )}
            
            <button 
              className="back-to-courses-btn"
              onClick={() => navigate('/contributions')}
            >
              Browse Courses
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentCancel; 