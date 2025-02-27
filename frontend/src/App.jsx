import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Home from './pages/Homepage'
import Login from './pages/Login'
import Footer from './Components/Footer'
import Signup from './pages/Signup'
import Contributions from './pages/Contributions'
import ContributionView from './pages/ContributionView'


function App() {
  return (
    <Router>
      <div className="app">
        <div className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/contributions" element={<Contributions />} />
            <Route path="/contributions/:id" element={<ContributionView />} />

          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  )
}

export default App