import React from 'react'
import './Footer.css'

function Footer() {
  return (
    <div className="footer">
      <div className="footer-content">
        <p className="footer-text">
          <span>Top companies choose</span>
          <span className="highlight"> Edusphere </span>
          <span>to build in-demand career skills.</span>
        </p>
        <div className="company-logos">
          {/* Replace these with your actual company logo images */}
          <img src="/logos/logo1.png" alt="Company 1" />
          <img src="/logos/logo2.png" alt="Company 2" />
          <img src="/logos/logo3.png" alt="Company 3" />
          <img src="/logos/logo4.png" alt="Company 4" />
          <img src="/logos/logo5.png" alt="Company 5" />
        </div>
      </div>
    </div>
  )
}

export default Footer