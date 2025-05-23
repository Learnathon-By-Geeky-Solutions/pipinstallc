import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import './App.css'
import Home from './pages/Homepage'
import Login from './pages/Login'
import Footer from './Components/Footer'
import Signup from './pages/Signup'
import Contributions from './pages/Contributions'
import ContributionView from './pages/ContributionView'
import { ThreeDots } from 'react-loader-spinner'
import Navbar from './Components/Navbar'
import SignupForm from './Components/SignupForm'
import LoginForm from './Components/LoginForm'
import ConfirmOtp from './pages/ConfirmOtp'
import ForgotPass from './pages/ForgotPass'
import ResetPassword from './pages/ResetPassword'
import PaymentSuccess from './pages/PaymentSuccess'
import PaymentFail from './pages/PaymentFail'
import PaymentCancel from './pages/PaymentCancel'
import AddContributions from './pages/AddContributions'
import UserContributions from './pages/UserContributions'
import UpdateContributions from './pages/UpdateContributions'
import Profile from './pages/Profile'
import Contributors from './pages/Contributors'

// RouteChangeTracker component to handle route changes
const RouteChangeTracker = ({ setLoading }) => {
  const location = useLocation();
  
  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      setLoading(false);
    }, 600); // Adjust loading time as needed
    
    return () => clearTimeout(timer);
  }, [location.pathname, setLoading]);
  
  return null;
};


function App() {
  const [loading, setLoading] = useState(false);

  return (
    <Router>
      <div className="app">
        <RouteChangeTracker setLoading={setLoading} />
        <Navbar />
        {loading && (
          <div className="loading-container">
            <ThreeDots 
              height="80" 
              width="80" 
              color="#6c2bb3" 
              ariaLabel="loading"
              visible={true}
            />
          </div>
        )}
        <div className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginForm />} />
            <Route path="/signup" element={<SignupForm />} />
            <Route path="/contributions" element={<Contributions />} />
            <Route path="/contributions/:id" element={<ContributionView />} />
            <Route path="/verify-otp" element={<ConfirmOtp />} />
            <Route path="/forgot-password" element={<ForgotPass />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/payment-success" element={<PaymentSuccess />} />
            <Route path="/payment-fail" element={<PaymentFail />} />
            <Route path="/payment-cancel" element={<PaymentCancel />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/contributors" element={<Contributors />} />
            
            <Route path="/add-contributions" element={<AddContributions />} />
            <Route path="/user-contributions" element={<UserContributions />} />
            <Route path="/update-contributions/:id" element={<UpdateContributions />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  )
}

export default App