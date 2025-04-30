import React, { useState, useEffect, useRef } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import '../styles/Navbar.css'
import { isLoggedIn, getCurrentUser, logout } from '../data/ApiCalls'

function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showDropdown, setShowDropdown] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const navRef = useRef(null)
  const mobileMenuRef = useRef(null)
  const dropdownRef = useRef(null)
  
  // Check if user is logged in on component mount and route changes
  useEffect(() => {
    if (isLoggedIn()) {
      setUser(getCurrentUser())
    } else {
      setUser(null)
    }
  }, [location.pathname])
  
  // Close mobile menu when route changes
  useEffect(() => {
    closeMobileMenu();
  }, [location.pathname]);
  
  // Handle click outside of mobile menu to close it
  useEffect(() => {
    function handleClickOutside(event) {
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target) &&
          !navRef.current.contains(event.target)) {
        if (mobileMenuOpen) {
          setMobileMenuOpen(false);
        }
      }
      
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        if (showDropdown) {
          setShowDropdown(false);
        }
      }
    }
    
    // Add when the component mounts
    document.addEventListener("mousedown", handleClickOutside);
    // Return function to be called when unmounted
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [mobileMenuOpen, showDropdown]);
  
  // Prevent body scrolling when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [mobileMenuOpen]);
  
  const handleLogout = async () => {
    setShowDropdown(false);
    setMobileMenuOpen(false);
    
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

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
    // Close dropdown if menu is being toggled
    if (showDropdown) setShowDropdown(false);
  }

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  }

  return (
    <nav className="navbar" ref={navRef}>
      <div className="logo">
        <Link to="/">
          <img 
            src="/images/EDusphere.png"
            alt='EDusphere Logo'
            className="navbar-logo"
          />
        </Link>
      </div>

      {/* Mobile menu button */}
      <div className="mobile-menu-button" onClick={toggleMobileMenu}>
        <div className={`menu-icon ${mobileMenuOpen ? 'open' : ''}`}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      {/* Navigation links - both desktop and mobile */}
      <div 
        className={`nav-links ${mobileMenuOpen ? 'mobile-active' : ''}`}
        ref={mobileMenuRef}
      >
        <Link 
          to="/" 
          className={location.pathname === "/" ? "active" : ""}
          onClick={closeMobileMenu}
        >
          Home
        </Link>
        <Link 
          to="/contributions" 
          className={location.pathname === "/contributions" ? "active" : ""}
          onClick={closeMobileMenu}
        >
          Contributions
        </Link>
        <Link 
          to="/membership" 
          className={location.pathname === "/membership" ? "active" : ""}
          onClick={closeMobileMenu}
        >
          Membership
        </Link>
        <Link 
          to="/contributors" 
          className={location.pathname === "/contributors" ? "active" : ""}
          onClick={closeMobileMenu}
        >
          Contributors
        </Link>

        {/* Mobile-only user options */}
        {user && mobileMenuOpen && (
          <div className="mobile-user-options">
            <Link to="/profile" onClick={closeMobileMenu}>
              My Profile
            </Link>
            <Link to="/user-contributions" onClick={closeMobileMenu}>
              My Contributions
            </Link>
            <button onClick={handleLogout} className="mobile-logout-btn">
              Logout
            </button>
          </div>
        )}

        {/* Mobile-only login button */}
        {!user && mobileMenuOpen && (
          <Link to="/login" onClick={closeMobileMenu}>
            <button className="mobile-login-btn">Login</button>
          </Link>
        )}
      </div>
      
      {/* Desktop user menu */}
      {user ? (
        <div className="user-menu desktop-only">
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
            <div className="dropdown-menu" ref={dropdownRef}>
              <Link to="/profile" onClick={() => setShowDropdown(false)}>
                My Profile
              </Link>
              <Link to="/user-contributions" onClick={() => setShowDropdown(false)}>
                My Contributions
              </Link>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          )}
        </div>
      ) : (
        <Link to="/login" className="desktop-only">
          <button className="l-btn">Login</button>
        </Link>
      )}
      
      {/* Backdrop overlay for mobile menu */}
      {mobileMenuOpen && <div className="mobile-backdrop" onClick={closeMobileMenu}></div>}
    </nav>
  )
}

export default Navbar