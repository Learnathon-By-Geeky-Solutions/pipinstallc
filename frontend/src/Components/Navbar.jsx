import React from 'react'
import '../styles/Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">
        <h2>Edusphere</h2>
      </div>
      <div className="nav-links">
        <a href="#">Home</a>
        <a href="#">Contributions</a>
        <a href="#">Membership</a>
        <a href="#">Contributors</a>
        <button className="l-btn">Login</button>
      </div>
    </nav>
  )
}

export default Navbar