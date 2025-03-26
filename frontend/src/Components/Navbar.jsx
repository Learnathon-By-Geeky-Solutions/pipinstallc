import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import '../styles/Navbar.css'

function Navbar() {
  const location = useLocation()

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
      <Link to="/login">
        <button className="l-btn">Login</button>
      </Link>
    </nav>
  )
}

export default Navbar