import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BaseUrl, getCurrentUser, isLoggedIn } from '../data/ApiCalls';
import Navbar from '../Components/Navbar';
import '../styles/Contributions.css';

function Contributions() {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTag, setActiveTag] = useState('All');
  const [showFilter, setShowFilter] = useState(false);
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredContributions, setFilteredContributions] = useState([]);
  const filterRef = useRef(null);
  const [userEnrollments, setUserEnrollments] = useState([]);
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination state
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    limit: 10,
    offset: 0
  });
  
  // Filter state
  const [filters, setFilters] = useState({
    university: '',
    department: '',
    major_subject: '',
    tag: '',
    user: '',
    search: ''
  });

  // Function to build the API URL with filters and pagination
  const buildApiUrl = () => {
    let url = `${BaseUrl}/api/all-contributions/`;
    const params = new URLSearchParams();
    
    // Add pagination parameters
    params.append('limit', pagination.limit);
    params.append('offset', pagination.offset);
    
    // Add filter parameters if they exist
    if (filters.university) params.append('university', filters.university);
    if (filters.department) params.append('department', filters.department);
    if (filters.major_subject) params.append('major_subject', filters.major_subject);
    if (filters.tag) params.append('tag', filters.tag);
    if (filters.user) params.append('user', filters.user);
    if (filters.search) params.append('search', filters.search);
    
    // Append query parameters to URL if they exist
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    
    return url;
  };

  // Fetch contributions with filters and pagination
  const fetchContributions = async () => {
    try {
      setLoading(true);
      const url = buildApiUrl();
      const response = await fetch(url);
      const result = await response.json();
      
      if (result.status) {
        setContributions(result.data || []);
        setFilteredContributions(result.data || []);
        
        // Update pagination info if available
        if (result.pagination) {
          setPagination(result.pagination);
        }
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

  // Fetch contributions when component mounts or when filters/pagination change
  useEffect(() => {
    fetchContributions();
  }, [pagination.offset, pagination.limit, filters]);

  // Extract unique tags from contributions
  const allTags = ['All', ...new Set(contributions.flatMap(contribution => 
    contribution.tags ? contribution.tags.map(tag => tag.name) : []
  ))];

  // Handle tag filtering
  useEffect(() => {
    if (activeTag === 'All') {
      setFilters(prevFilters => ({
        ...prevFilters,
        tag: ''
      }));
    } else {
      setFilters(prevFilters => ({
        ...prevFilters,
        tag: activeTag
      }));
    }
  }, [activeTag]);

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
    // Reset offset when applying a new filter
    setPagination(prev => ({
      ...prev,
      offset: 0
    }));
    fetchContributions();
    setShowFilter(false);
  };

  const handleClearFilter = () => {
    // Clear all filters
    setFilters({
      university: '',
      department: '',
      major_subject: '',
      tag: '',
      user: ''
    });
    setActiveTag('All');
    setPagination(prev => ({
      ...prev,
      offset: 0
    }));
    setShowFilter(false);
  };

  const handleViewClick = (id) => {
    // Store the selected contribution ID in localStorage for persistence
    localStorage.setItem('selectedContributionId', id);
    
    // Navigate to the contribution detail page
    navigate(`/contributions/${id}`);
  };

  // Pagination handlers
  const handleNextPage = () => {
    if (pagination.next) {
      setPagination(prev => ({
        ...prev,
        offset: prev.offset + prev.limit
      }));
    }
  };

  const handlePrevPage = () => {
    if (pagination.previous) {
      setPagination(prev => ({
        ...prev,
        offset: Math.max(0, prev.offset - prev.limit)
      }));
    }
  };

  // Check if user is authenticated
  useEffect(() => {
    setIsUserAuthenticated(isLoggedIn());
    
    // If user is authenticated, fetch their enrollments
    if (isLoggedIn()) {
      fetchUserEnrollments();
    }
  }, []);
  
  // Function to fetch user enrollments
  const fetchUserEnrollments = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) return;
      
      const response = await fetch(`${BaseUrl}/api/enrollments/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      
      const result = await response.json();
      
      if (result.status) {
        setUserEnrollments(result.data.map(enrollment => enrollment.contribution_id));
      }
    } catch (error) {
      console.error('Error fetching user enrollments:', error);
    }
  };
  
  // Check if user is enrolled in a specific contribution
  const isEnrolled = (contributionId) => {
    return userEnrollments.includes(contributionId);
  };

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Handle search submission
  const handleSearch = (e) => {
    e.preventDefault();
    setFilters(prev => ({
      ...prev,
      search: searchQuery
    }));
    setPagination(prev => ({
      ...prev,
      offset: 0
    }));
  };

  return (
    <div className="contributions-page">
      <Navbar />
      <div className="contributions-content">
        <h1>All the exam preparations you need in one place</h1>
        <p className="subtitle">From critical skills to exam topics, edusphere supports your development.</p>
        
        <div className="sub-navbar">
          <div className="search-container">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="Search by keyword or tag..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="search-input"
              />
              <button type="submit" className="search-button">
                <i className="fas fa-search"></i>
              </button>
            </form>
          </div>

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
                    {universities.map(uni => (
                      <label key={uni.id} className="filter-option">
                        <input 
                          type="checkbox" 
                          checked={filters.university === uni.id}
                          onChange={() => setFilters(prev => ({
                            ...prev,
                            university: prev.university === uni.id ? '' : uni.id
                          }))}
                        /> 
                        {uni.name}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="filter-section">
                  <h4>Departments</h4>
                  <div className="filter-options">
                    {departments.map(dept => (
                      <label key={dept.id} className="filter-option">
                        <input 
                          type="checkbox" 
                          checked={filters.department === dept.id}
                          onChange={() => setFilters(prev => ({
                            ...prev,
                            department: prev.department === dept.id ? '' : dept.id
                          }))}
                        /> 
                        {dept.name}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="filter-section">
                  <h4>Major Subjects</h4>
                  <div className="filter-options">
                    {majorSubjects.map(subject => (
                      <label key={subject.id} className="filter-option">
                        <input 
                          type="checkbox" 
                          checked={filters.major_subject === subject.id}
                          onChange={() => setFilters(prev => ({
                            ...prev,
                            major_subject: prev.major_subject === subject.id ? '' : subject.id
                          }))}
                        /> 
                        {subject.name}
                      </label>
                    ))}
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
          <>
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
                        {isUserAuthenticated && isEnrolled(contribution.id) ? (
                          <div className="enrolled-indicator">
                            <span className="enrolled-badge">Enrolled</span>
                            <button 
                              onClick={() => handleViewClick(contribution.id)}
                              className="view-enrolled-btn"
                            >
                              View Content
                            </button>
                          </div>
                        ) : (
                          <button 
                            onClick={() => handleViewClick(contribution.id)}
                            className="view-btn"
                          >
                            View
                          </button>
                        )}
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
            
            {/* Pagination Controls */}
            {filteredContributions.length > 0 && (
              <div className="pagination-controls">
                <button 
                  onClick={handlePrevPage} 
                  disabled={!pagination.previous}
                  className="pagination-btn"
                >
                  Previous
                </button>
                <span className="pagination-info">
                  Showing {pagination.offset + 1} to {Math.min(pagination.offset + filteredContributions.length, pagination.count)} of {pagination.count}
                </span>
                <button 
                  onClick={handleNextPage} 
                  disabled={!pagination.next}
                  className="pagination-btn"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Contributions;