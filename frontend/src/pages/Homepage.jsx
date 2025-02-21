import React from 'react'
import Navbar from '../Components/Navbar'
import Footer from '../Components/Footer'
 // Make sure to add your illustration to assets folder
import '../styles/Home.css'
import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home">
      <Navbar />
      <div className="hero-section">
        <div className="hero-content">
          <h1>
            Increase your<br />
            Result<br />
            with us!
          </h1>
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do 
             eiusmod tempor incididunt ut labom et dolore magna aliqua. Ut 
             enim ad minim veniam</p>
          <button 
            className="explore-btn"
            onClick={() => navigate('/contributions')}
          >
            <span className="dot"></span>
            EXPLORE
          </button>
         </div>
        <div className="hero-image">
          <img src={'images/homepic.png'} alt="Education illustration" />
        </div>
      </div>
      
    </div>
  )
}

export default Home