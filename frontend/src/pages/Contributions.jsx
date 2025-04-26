import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { BaseUrl } from '../data/ApiCalls';
import Navbar from '../Components/Navbar';
import '../styles/Contributions.css';

function Contributions() {
  const navigate = useNavigate();
  const [activeTag, setActiveTag] = useState('All');
  const [showFilter, setShowFilter] = useState(false);
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredContributions, setFilteredContributions] = useState([]);
  const filterRef = useRef(null);

  // Fetch all contributions when component mounts
  useEffect(() => {
    const fetchContributions = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${BaseUrl}/api/all-contributions/`);
        const result = await response.json();
        
        if (result.status) {
          setContributions(result.data);
          setFilteredContributions(result.data);
        } else {
          setError(result.message || 'Failed to fetch contributions');
        }
      } catch (error) {
        console.error('Error fetching contributions:', error);
        setError('An error occurred while fetching contributions');
      } finally {
        setLoading(false);
      }
    };

    fetchContributions();
  }, []);

  // Extract unique tags from contributions
  const allTags = ['All', ...new Set(contributions.flatMap(contribution => 
    contribution.tags ? contribution.tags.map(tag => tag.name) : []
  ))];

  // Filter contributions when active tag changes
  useEffect(() => {
    if (activeTag === 'All') {
      setFilteredContributions(contributions);
    } else {
      const filtered = contributions.filter(contribution => 
        contribution.tags && contribution.tags.some(tag => tag.name === activeTag)
      );
      setFilteredContributions(filtered);
    }
  }, [activeTag, contributions]);

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
    // Implement filter logic here
    setShowFilter(false);
  };

  const handleClearFilter = () => {
    // Clear filters
    setShowFilter(false);
  };

  const handleViewClick = (id) => {
    // Store the selected contribution ID in localStorage for persistence
    localStorage.setItem('selectedContributionId', id);
    
    // Navigate to the contribution detail page
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
            {allTags.map((tag) => (
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
                  <h4>Universities</h4>
                  <div className="filter-options">
                    {['AIUB', 'BRACU', 'DIU', 'EWU', 'IUB'].map(uni => (
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

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading contributions...</p>
          </div>
        ) : error ? (
          <div className="error-message">
            <p>{error}</p>
          </div>
        ) : (
          <div className="video-grid">
            {filteredContributions.length > 0 ? (
              filteredContributions.map(contribution => (
                <div className="video-card" key={contribution.id}>
                  <div className="video-thumbnail">
                    {contribution.thumbnail_image ? (
                      <img 
                        src={contribution.thumbnail_image} 
                        alt={contribution.title} 
                        className="thumbnail-image"
                      />
                    ) : (
                      <div className="placeholder-thumbnail">
                        <h3>{contribution.title}</h3>
                      </div>
                    )}
                    <div className="card-overlay">
                      <h3>{contribution.title}</h3>
                      <p className="price">${contribution.price}</p>
                      <div className="rating">
                        {contribution.rating ? `★ ${contribution.rating}` : 'Not rated yet'}
                      </div>
                      <button 
                        onClick={() => handleViewClick(contribution.id)}
                        className="view-btn"
                      >
                        View
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-results">
                <p>No contributions found for the selected filter.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Contributions;