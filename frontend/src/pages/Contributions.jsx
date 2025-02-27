import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

import Navbar from '../Components/Navbar';
import '../styles/Contributions.css';

function Contributions() {
  const navigate = useNavigate();

  const [activeTag, setActiveTag] = useState('DSA');
  const [showFilter, setShowFilter] = useState(false);
  const filterRef = useRef(null);

  const tags = [
    'DSA', 'algorithm', 'english', 'business', 
    'department', 'SWE', 'more..'
  ];

  const filterTags = [
    'BFS', 'Ceaser Cipher', 'DFS', 'Decision Tree', 
    'Graph', 'Linked List', 'Logistic Regression', 'Tree'
  ];

  const universities = [
    'AIUB', 'BRACU', 'DIU', 'EWU', 'IUB'
  ];

  // Handle click outside to close filter
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (filterRef.current && !filterRef.current.contains(event.target)) {
        setShowFilter(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleApplyFilter = () => {
    setShowFilter(false);
  };

  const handleClearFilter = () => {
    setShowFilter(false);
  };

  const handleViewClick = (id) => {
    navigate(`/contributions/${id}`);
  };


  return (
    <div className="contributions-page">
      <Navbar />
      <div className="contributions-content">
        <h1 style={{color: '#6c2bb3'}}>All the exam preparations you need in one place</h1>
        <p className="subtitle">From critical skills to exam topics, edusphere supports your development.</p>
        
        <div className="sub-navbar">
          <div className="tags-container">
            {tags.map((tag) => (
              <button 
                key={tag}
                className={`nav-tag ${activeTag === tag ? 'active' : ''}`}
                onClick={() => setActiveTag(tag)}
              >
                {tag}
              </button>
            ))}
          </div>

          <div className="filter-container" ref={filterRef}>
            <button 
              className="filter-btn"
              onClick={() => setShowFilter(!showFilter)}
            >
              <img src={"/images/filter.png"} alt="filter" className="filter-icon" />
            </button>

            {showFilter && (
              <div className="filter-dropdown">
                <div className="filter-section">
                  <h4>Tags</h4>
                  <div className="filter-options">
                    {filterTags.map(tag => (
                      <label key={tag} className="filter-option">
                        <input type="checkbox" /> {tag}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="filter-section">
                  <h4>Universities</h4>
                  <div className="filter-options">
                    {universities.map(uni => (
                      <label key={uni} className="filter-option">
                        <input type="checkbox" /> {uni}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="filter-section">
                  <h4>Rating</h4>
                  <div className="filter-options">
                    <label className="filter-option">
                      <input type="checkbox" /> 4+ Stars
                    </label>
                    <label className="filter-option">
                      <input type="checkbox" /> 3+ Stars
                    </label>
                    <label className="filter-option">
                      <input type="checkbox" /> All Ratings
                    </label>
                  </div>
                </div>

                <div className="filter-actions">
                  <button className="clear-filter-btn" onClick={handleClearFilter}>
                    Clear
                  </button>
                  <button className="apply-filter-btn" onClick={handleApplyFilter}>
                    Apply
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="video-grid">
          <div className="video-card">
            <div className="video-thumbnail">
              <h3>learn {activeTag}</h3>
              <button 
                onClick={() => handleViewClick('learn-algorithm')}
                className="view-btn"
              >
                view
              </button>

            </div>
          </div>
          <div className="video-card">
            <div className="video-thumbnail">
              <h3>easy {activeTag}</h3>
              <button className="view-btn">view</button>
            </div>
          </div>
          <div className="video-card">
            <div className="video-thumbnail">
              <h3>advanced {activeTag}</h3>
              <button className="view-btn">view</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Contributions;