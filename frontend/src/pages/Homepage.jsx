import React from 'react'
import Navbar from '../Components/Navbar'
import Footer from '../Components/Footer'
import homePic from '../images/homepic.png' // Make sure to add your illustration to assets folder
import '../styles/Home.css'

function Home() {
    return (
      <div className="home">
        <Navbar />
        <div className="hero-section">
          <div className="hero-content" style={{ width: '100%' }}>
            <h1>
              Increase your<br />
              Result<br />
              with us!
            </h1>
          <p style={{ textAlign: 'left' }}>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do 
             eiusmod tempor incididunt ut labom et dolore magna aliqua. Ut 
             enim ad minim veniam</p>
          <button className="explore-btn">
            <span className="dot"></span>
            EXPLORE
          </button>
         </div>
        <div className="hero-image">
          <img src={homePic} alt="Education illustration" />
        </div>
      </div>
      <Footer />
    </div>
  )
}

export default Home