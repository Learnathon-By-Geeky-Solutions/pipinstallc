import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BaseUrl } from '../data/ApiCalls';
import Navbar from '../Components/Navbar';
import '../styles/PaymentSuccess.css';

function PaymentSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [contributionId, setContributionId] = useState(null);
  const [redirectUrl, setRedirectUrl] = useState(null);
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    // Check if we're on the payment success page from SSLCommerz
    const currentUrl = window.location.href;
    
    if (currentUrl.includes('/api/payment/success/')) {
      // Show overlay to hide the HTML response
      setShowOverlay(true);
      setLoading(false); // No need to verify, we're already on the success page
      
      // Try to extract data from the HTML
      try {
        // Look for the hidden data element
        const dataElement = document.getElementById('payment-data');
        if (dataElement) {
          const extractedId = dataElement.getAttribute('data-contribution-id');
          const extractedRedirectUrl = dataElement.getAttribute('data-redirect-url');
          
          if (extractedId) {
            setContributionId(extractedId);
          }
          
          if (extractedRedirectUrl) {
            setRedirectUrl(extractedRedirectUrl);
          }
        }
        
        // If we can't find the data element, try to extract from the URL or links
        if (!redirectUrl) {
          const redirectLinks = document.querySelectorAll('a.redirect-btn');
          if (redirectLinks.length > 0) {
            const href = redirectLinks[0].getAttribute('href');
            if (href) {
              setRedirectUrl(href);
            }
          }
        }
      } catch (e) {
        console.log("Error extracting data:", e);
      }
      
      return;
    }
    
    // If we're on the normal PaymentSuccess component page
    // This is for when the user is redirected back from SSLCommerz
    const params = new URLSearchParams(location.search);
    const val_id = params.get('val_id');
    const tran_id = params.get('tran_id');
    
    // If we don't have these parameters, we're not coming from a payment gateway
    if (!val_id && !tran_id) {
      // Just show the success message without verification
      setLoading(false);
      return;
    }
    
    // If we have the parameters, verify the payment
    const verifyPayment = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');
        
        const response = await fetch(`${BaseUrl}/api/verify-payment/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({
            val_id,
            tran_id
          })
        });
        
        const result = await response.json();
        
        if (result.status === 'success' || result.status === true) {
          // Payment verified successfully
          if (result.contribution_id) {
            setContributionId(result.contribution_id);
          }
          
          if (result.redirect_url) {
            setRedirectUrl(result.redirect_url);
          }
          
          setLoading(false);
        } else {
          // Payment verification failed
          setError(result.message || 'Payment verification failed');
          setLoading(false);
        }
      } catch (error) {
        console.error('Error verifying payment:', error);
        setError('An error occurred while verifying your payment. However, your enrollment may still be successful.');
        setLoading(false);
      }
    };
    
    // Only verify if we have the parameters
    if (val_id || tran_id) {
      verifyPayment();
    } else {
      setLoading(false);
    }
  }, [location]);

  // Handle redirect based on available data
  const handleRedirect = () => {
    if (redirectUrl) {
      // Use the redirect URL from the backend
      window.location.href = redirectUrl.startsWith('http') ? 
        redirectUrl : 
        `http://localhost:5173${redirectUrl}`;
    } else if (contributionId) {
      // Fallback to the contribution page if we have an ID
      window.location.href = `http://localhost:5173/contributions/${contributionId}`;
    } else {
      // Default fallback
      window.location.href = `http://localhost:5173/contributions`;
    }
  };

  // If we're showing the overlay, render it over the entire page
  if (showOverlay) {
    return (
      <div className="payment-overlay">
        <div className="payment-overlay-content">
          <div className="success-icon">✅</div>
          <h1>Payment Successful!</h1>
          <p>Thank you for your payment. You have successfully enrolled in the course.</p>
          
          <button 
            className="overlay-button"
            onClick={handleRedirect}
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  // Normal payment success page
  return (
    <div className="payment-result-page">
      <Navbar />
      
      <div className="payment-result-container">
        {loading ? (
          <div className="payment-loading">
            <div className="loading-spinner"></div>
            <h2>Processing your payment...</h2>
            <p>Please wait while we confirm your enrollment.</p>
          </div>
        ) : error ? (
          <div className="payment-error">
            <div className="error-icon">⚠️</div>
            <h2>Payment Verification Notice</h2>
            <p>{error}</p>
            <p>You can still try to access your course:</p>
            <div className="action-buttons">
              <button 
                className="view-course-btn"
                onClick={() => navigate('/contributions')}
              >
                Go to Courses
              </button>
            </div>
          </div>
        ) : (
          <div className="payment-success">
            <div className="success-icon">✅</div>
            <h2>Payment Successful!</h2>
            <p>Thank you for your payment. You have successfully enrolled in the course.</p>
            
            <div className="action-buttons">
              <button 
                className="view-course-btn"
                onClick={handleRedirect}
              >
                Continue
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PaymentSuccess; 