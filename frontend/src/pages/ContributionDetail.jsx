import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../Components/Navbar';
import { BaseUrl, isLoggedIn } from '../data/ApiCalls';
import '../styles/ContributionDetail.css';

function ContributionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contribution, setContribution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const [showFullContent, setShowFullContent] = useState(false);

  useEffect(() => {
    setIsUserAuthenticated(isLoggedIn());
    
    const fetchContribution = async () => {
      try {
        setLoading(true);
        const accessToken = localStorage.getItem('access_token');
        
        // Set up headers
        const headers = {
          'Content-Type': 'application/json',
        };
        
        // Add authorization header if token exists
        if (accessToken) {
          headers['Authorization'] = `Bearer ${accessToken}`;
        }
        
        // Fetch contribution details
        const response = await fetch(`${BaseUrl}/api/user-contributions/${id}/`, {
          headers: headers
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch contribution details');
        }
        
        const result = await response.json();
        
        if (result.status) {
          setContribution(result.data);
        } else {
          setError(result.message || 'Failed to fetch contribution');
        }
        
        // Check if user is enrolled
        if (accessToken) {
          const enrollmentsResponse = await fetch(`${BaseUrl}/api/enrollments/`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          
          if (enrollmentsResponse.ok) {
            const enrollmentsResult = await enrollmentsResponse.json();
            
            if (enrollmentsResult.status) {
              const enrolledContributionIds = enrollmentsResult.data.map(
                enrollment => enrollment.contribution_id
              );
              
              setIsEnrolled(enrolledContributionIds.includes(id));
            }
          }
        }
      } catch (error) {
        console.error('Error fetching contribution:', error);
        setError('An error occurred while fetching the contribution');
      } finally {
        setLoading(false);
      }
    };

    fetchContribution();
  }, [id]);

  const handleEnroll = async () => {
    if (!isUserAuthenticated) {
      navigate('/login', { state: { returnUrl: `/contributions/${id}` } });
      return;
    }
    
    try {
      const accessToken = localStorage.getItem('access_token');
      
      if (!accessToken) {
        navigate('/login', { state: { returnUrl: `/contributions/${id}` } });
        return;
      }
      
      // Enroll in the contribution
      const response = await fetch(`${BaseUrl}/api/enrollments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          contribution_id: id
        })
      });
      
      const result = await response.json();
      
      if (result.status) {
        setIsEnrolled(true);
        // Show success message or redirect to course content
      } else {
        // Show error message
        alert(result.message || 'Failed to enroll in this contribution');
      }
    } catch (error) {
      console.error('Error enrolling in contribution:', error);
      alert('An error occurred while trying to enroll');
    }
  };

  if (loading) {
    return (
      <div className="contribution-detail-page">
        <Navbar />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading contribution details...</p>
        </div>
      </div>
    );
  }

  if (error || !contribution) {
    return (
      <div className="contribution-detail-page">
        <Navbar />
        <div className="error-container">
          <h2>Error</h2>
          <p>{error || 'Failed to load contribution details'}</p>
          <button onClick={() => navigate('/contributions')}>Go Back to Contributions</button>
        </div>
      </div>
    );
  }

  return (
    <div className="contribution-detail-page">
      <Navbar />
      <div className="contribution-detail-content">
        <div className="contribution-header">
          <div className="contribution-header-left">
            <h1>{contribution.title}</h1>
            <p className="contribution-description">{contribution.description}</p>
            
            <div className="contribution-meta">
              <div className="meta-item">
                <span className="meta-label">Price:</span>
                <span className="meta-value">${contribution.price}</span>
              </div>
              
              <div className="meta-item">
                <span className="meta-label">Rating:</span>
                <span className="meta-value">
                  {contribution.rating ? `★ ${contribution.rating}` : 'Not rated yet'}
                </span>
              </div>
              
              {contribution.related_University && (
                <div className="meta-item">
                  <span className="meta-label">University:</span>
                  <span className="meta-value">{contribution.related_University.name}</span>
                </div>
              )}
              
              {contribution.related_Department && (
                <div className="meta-item">
                  <span className="meta-label">Department:</span>
                  <span className="meta-value">{contribution.related_Department.name}</span>
                </div>
              )}
              
              {contribution.related_Major_Subject && (
                <div className="meta-item">
                  <span className="meta-label">Subject:</span>
                  <span className="meta-value">{contribution.related_Major_Subject.name}</span>
                </div>
              )}
            </div>
            
            {contribution.tags && contribution.tags.length > 0 && (
              <div className="contribution-tags">
                {contribution.tags.map(tag => (
                  <span key={tag.id} className="tag">{tag.name}</span>
                ))}
              </div>
            )}
          </div>
          
          <div className="contribution-header-right">
            {contribution.thumbnail_image ? (
              <img 
                src={contribution.thumbnail_image} 
                alt={contribution.title} 
                className="detail-thumbnail"
              />
            ) : (
              <div className="placeholder-detail-thumbnail">
                <h3>{contribution.title}</h3>
              </div>
            )}
          </div>
        </div>

        {isUserAuthenticated && isEnrolled ? (
          <div className="enrolled-content-section">
            <div className="enrolled-header">
              <h2>Course Content</h2>
              <span className="enrollment-status">You are enrolled in this course</span>
            </div>
            
            {/* Full content accessible to enrolled users */}
            <div className="full-content">
              {contribution.content && (
                <div className="content-section">
                  <h3>Course Materials</h3>
                  <p>{contribution.content}</p>
                </div>
              )}
              
              {contribution.resources && contribution.resources.length > 0 && (
                <div className="resources-section">
                  <h3>Resources</h3>
                  <ul className="resource-list">
                    {contribution.resources.map((resource, index) => (
                      <li key={index} className="resource-item">
                        <a href={resource.url} target="_blank" rel="noopener noreferrer">
                          {resource.title || `Resource ${index + 1}`}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {contribution.files && contribution.files.length > 0 && (
                <div className="files-section">
                  <h3>Downloadable Files</h3>
                  <ul className="file-list">
                    {contribution.files.map((file, index) => (
                      <li key={index} className="file-item">
                        <a href={file.url} download>
                          {file.name || `File ${index + 1}`}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="enroll-section">
            <h2>Preview Content</h2>
            <div className="preview-content">
              <p>{contribution.description}</p>
              {/* Show a limited preview of content */}
              {contribution.preview_text && (
                <div className="preview-text">
                  <h3>Preview</h3>
                  <p>{contribution.preview_text}</p>
                </div>
              )}
            </div>
            
            <div className="enroll-action">
              <p>Enroll to access full course materials and resources</p>
              <button 
                className="enroll-button"
                onClick={handleEnroll}
              >
                Enroll Now - ${contribution.price}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ContributionDetail; 