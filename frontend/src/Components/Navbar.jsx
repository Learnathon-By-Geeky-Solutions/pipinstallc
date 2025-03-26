import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import '../styles/Navbar.css'
import { isLoggedIn, getCurrentUser, logout } from '../data/ApiCalls'

function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showDropdown, setShowDropdown] = useState(false)
  
  // Check if user is logged in on component mount and route changes
  useEffect(() => {
    if (isLoggedIn()) {
      setUser(getCurrentUser())
    } else {
      setUser(null)
    }
  }, [location.pathname])
  
  const handleLogout = async () => {
    setShowDropdown(false);
    // Show some loading state if desired
    
    try {
      await logout();
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error("Error during logout:", error);
      // Still set user to null even if there's an error
      setUser(null);
      navigate('/');
    }
  }

  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">
          <img 
            src="/images/EDusphere.png"
            alt='EDusphere Logo'
            className="navbar-logo"
          />
        </Link>
      </div>
      <div className="nav-links">
        <Link to="/" className={location.pathname === "/" ? "active" : ""}>
          Home
        </Link>
        <Link to="/contributions" className={location.pathname === "/contributions" ? "active" : ""}>
          Contributions
        </Link>
        <Link to="/membership" className={location.pathname === "/membership" ? "active" : ""}>
          Membership
        </Link>
        <Link to="/contributors" className={location.pathname === "/contributors" ? "active" : ""}>
          Contributors
        </Link>
      </div>
      
      {user ? (
        <div className="user-menu">
          <div 
            className="user-profile" 
            onClick={() => setShowDropdown(!showDropdown)}
          >
            <span className="username">Welcome, {user.username}</span>
            <div className="avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
          </div>
          
          {showDropdown && (
            <div className="dropdown-menu">
              <Link to="/profile" onClick={() => setShowDropdown(false)}>
                My Profile
              </Link>
              <Link to="/my-contributions" onClick={() => setShowDropdown(false)}>
                My Contributions
              </Link>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          )}
        </div>
      ) : (
        <Link to="/login">
          <button className="l-btn">Login</button>
        </Link>
      )}
    </nav>
  )
}

export default Navbar