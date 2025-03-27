import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BaseUrl, isLoggedIn } from '../data/ApiCalls';
import Navbar from '../Components/Navbar';
import '../styles/ContributionView.css';

function ContributionView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Description');
  const [activeVideoIndex, setActiveVideoIndex] = useState(0);
  const [contribution, setContribution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentVideo, setCurrentVideo] = useState(null);
  const [userRating, setUserRating] = useState(0);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [enrollmentStatus, setEnrollmentStatus] = useState('not-enrolled');
  const [enrollmentError, setEnrollmentError] = useState(null);
  const [showVideoList, setShowVideoList] = useState(true);

  // Fetch contribution data based on ID
  useEffect(() => {
    const fetchContributionData = async () => {
      try {
        setLoading(true);
        
        // Get the access token if user is logged in
        const accessToken = localStorage.getItem('access_token');
        const headers = accessToken ? 
          { 'Authorization': `Bearer ${accessToken}` } : {};
        
        const response = await fetch(`${BaseUrl}/api/all-contributions/${id}/`, {
          headers
        });
        
        const result = await response.json();
        
        if (result.status) {
          setContribution(result.data);
          setIsEnrolled(result.data.is_enrolled || false);
          
          // Set current video if videos are available and user is enrolled
          if (result.data.videos && result.data.videos.length > 0) {
            setCurrentVideo(result.data.videos[0]);
          }
        } else {
          setError(result.message || 'Failed to fetch contribution details');
        }
      } catch (error) {
        console.error("Error fetching contribution data:", error);
        setError('An error occurred while fetching the contribution details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchContributionData();
    }
  }, [id]);

  // Fetch user's rating if logged in
  useEffect(() => {
    // Only proceed if user is logged in
    if (isLoggedIn() && id) {
      const fetchUserRating = async () => {
        try {
          const accessToken = localStorage.getItem('access_token');
          
          const response = await fetch(`${BaseUrl}/api/ratings/${id}/?user_rating=true`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          
          const result = await response.json();
          
          if (result.status) {
            setUserRating(result.data.rating);
          }
        } catch (error) {
          console.error("Error fetching user rating:", error);
        }
      };
      
      fetchUserRating();
    }
  }, [id]);

  // Set current video when active index changes
  useEffect(() => {
    if (contribution && contribution.videos && contribution.videos.length > activeVideoIndex) {
      setCurrentVideo(contribution.videos[activeVideoIndex]);
    }
  }, [contribution, activeVideoIndex]);

  // Handle enrollment
  const handleEnroll = async () => {
    if (!isLoggedIn()) {
      navigate('/login', { state: { returnUrl: `/contributions/${id}` } });
      return;
    }

    try {
      setEnrollmentStatus('enrolling');
      setEnrollmentError(null);
      
      const accessToken = localStorage.getItem('access_token');
      
      const response = await fetch(`${BaseUrl}/api/create-enrollments/${id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      
      const result = await response.json();
      
      if (result.status) {
        if (result.data && result.data.payment_url) {
          window.location.href = result.data.payment_url;
        } else {
          setIsEnrolled(true);
          setEnrollmentStatus('enrolled');
          window.location.reload();
        }
      } else {
        setEnrollmentStatus('failed');
        setEnrollmentError(result.message || 'Failed to enroll in this course');
      }
    } catch (error) {
      console.error("Error enrolling in course:", error);
      setEnrollmentStatus('failed');
      setEnrollmentError('An error occurred while enrolling in this course');
    }
  };

  // Handle rating submission
  const handleRateSubmit = async (rating) => {
    if (!isLoggedIn()) {
      navigate('/login', { state: { returnUrl: `/contributions/${id}` } });
      return;
    }

    if (!isEnrolled) {
      alert('You must be enrolled in this course to rate it');
      return;
    }

    try {
      const accessToken = localStorage.getItem('access_token');
      
      const response = await fetch(`${BaseUrl}/api/ratings/${id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ rating })
      });
      
      const result = await response.json();
      
      if (result.status) {
        setUserRating(rating);
        window.location.reload();
      } else {
        alert(result.message || 'Failed to submit rating');
      }
    } catch (error) {
      console.error("Error submitting rating:", error);
      alert('An error occurred while submitting your rating');
    }
  };

  // Toggle video list visibility
  const toggleVideoList = () => {
    setShowVideoList(!showVideoList);
  };

  if (loading) {
    return (
      <div className="contribution-view">
        <Navbar />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading course details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="contribution-view">
        <Navbar />
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/contributions')} className="back-btn">
            Back to Courses
          </button>
        </div>
      </div>
    );
  }

  if (!contribution) {
    return (
      <div className="contribution-view">
        <Navbar />
        <div className="error-container">
          <h2>Course Not Found</h2>
          <p>The course you're looking for doesn't exist or has been removed.</p>
          <button onClick={() => navigate('/contributions')} className="back-btn">
            Back to Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="contribution-view">
      <Navbar />
      
      {/* Hero section */}
      <div className="course-hero">
        <div className="hero-container">
          <div className="course-header">
            <h1>{contribution.title}</h1>
          </div>
          
          <div className="course-meta">
            <div className="meta-item">
              <span className="rating">
                ★ {contribution.rating || 'Not rated yet'}
              </span>
            </div>
            
            <div className="meta-item">
              <span className="price">${contribution.price}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main content area */}
      <div className="course-content">
        {/* Left column - course details */}
        <div className="course-details">
          {/* Video player section */}
          <div className="course-player-section">
            {isEnrolled ? (
              <div className="video-container">
                <div className="video-player">
                  {currentVideo && currentVideo.video_file ? (
                    <video 
                      className="video-element" 
                      controls
                      src={currentVideo.video_file.startsWith('http') 
                        ? currentVideo.video_file 
                        : `${BaseUrl}${currentVideo.video_file}`}
                      key={currentVideo.id}
                      autoPlay
                    >
                      Your browser does not support the video tag.
                    </video>
                  ) : (
                    <div className="video-placeholder">
                      <p>No video available or selected</p>
                    </div>
                  )}
                </div>
                
                {currentVideo && (
                  <div className="current-video-info">
                    <h3>{currentVideo.title || `Video ${activeVideoIndex + 1}`}</h3>
                  </div>
                )}
                
                <div className="video-list-toggle">
                  <button onClick={toggleVideoList} className="toggle-btn">
                    {showVideoList ? 'Hide Course Content' : 'Show Course Content'}
                  </button>
                </div>
                
                {showVideoList && (
                  <div className="video-list-container">
                    <h3 className="video-list-title">Course Content</h3>
                    
                    <div className="video-list">
                      {contribution.videos && contribution.videos.length > 0 ? (
                        <ul>
                          {contribution.videos.map((video, index) => (
                            <li 
                              key={video.id} 
                              className={`video-item ${index === activeVideoIndex ? 'active' : ''}`}
                              onClick={() => setActiveVideoIndex(index)}
                            >
                              <div className="video-item-content">
                                <span className="video-number">{index + 1}</span>
                                <div className="video-item-details">
                                  <span className="video-title">{video.title || `Video ${index + 1}`}</span>
                                </div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="no-videos">No videos available for this course.</p>
                      )}
                    </div>
                    
                    {contribution.notes && contribution.notes.length > 0 && (
                      <div className="notes-section">
                        <h3 className="notes-title">Course Resources</h3>
                        <ul className="notes-list">
                          {contribution.notes.map((note, index) => (
                            <li key={index} className="note-item">
                              <a 
                                href={note.note_file.startsWith('http') 
                                  ? note.note_file 
                                  : `${BaseUrl}${note.note_file}`}
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="note-link"
                              >
                                <span className="note-icon">📄</span>
                                <span className="note-name">Resource {index + 1}</span>
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="thumbnail-container">
                <img 
                  src={contribution.thumbnail_image} 
                  alt={contribution.title}
                  className="course-thumbnail"
                />
                <div className="thumbnail-overlay">
                  <p>Enroll to access course content</p>
                </div>
              </div>
            )}
          </div>
          
          {/* Content tabs */}
          <div className="content-tabs">
            <nav className="tabs-nav">
              <button
                onClick={() => setActiveTab('Description')}
                className={`tab-button ${activeTab === 'Description' ? 'active' : ''}`}
              >
                Description
              </button>
              
              <button
                onClick={() => setActiveTab('Comments')}
                className={`tab-button ${activeTab === 'Comments' ? 'active' : ''}`}
              >
                Comments
              </button>
              
              <button
                onClick={() => setActiveTab('Rate')}
                className={`tab-button ${activeTab === 'Rate' ? 'active' : ''}`}
              >
                Rate
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'Description' && (
              <div className="description-content">
                <h3>About this course</h3>
                <p>{contribution.description || 'No description available for this course.'}</p>
                
                {contribution.tags && contribution.tags.length > 0 && (
                  <div className="tags-section">
                    <h4>Topics covered</h4>
                    <div className="tags-list">
                      {contribution.tags.map(tag => (
                        <span key={tag.id} className="tag">{tag.name}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {contribution.origine && contribution.origine.length > 0 && (
                  <div className="origin-section">
                    <h4>Academic Information</h4>
                    <ul>
                      {contribution.origine.map(origin => (
                        <li key={origin.id}>
                          <strong>University:</strong> {origin.related_University || 'N/A'}<br />
                          <strong>Department:</strong> {origin.related_Department || 'N/A'}<br />
                          <strong>Subject:</strong> {origin.related_Major_Subject || 'N/A'}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'Comments' && (
              <div className="comments-content">
                <h4>Student Feedback</h4>
                {contribution.comments && contribution.comments.length > 0 ? (
                  <div className="comments-list">
                    {contribution.comments.map(comment => (
                      <div key={comment.id} className="comment">
                        <div className="comment-header">
                          <span className="comment-author">{comment.user?.username || 'Anonymous'}</span>
                          <span className="comment-date">
                            {new Date(comment.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="comment-text">{comment.comment}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No reviews yet. Be the first to leave a review!</p>
                )}
                
                {isLoggedIn() && (
                  <div className="comment-form">
                    <h4>Leave a Review</h4>
                    <textarea 
                      placeholder="Share your experience with this course..."
                      className="comment-textarea"
                    ></textarea>
                    <button className="submit-comment-btn">Submit Review</button>
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'Rate' && (
              <div className="rating-content">
                <h4>Rate this Course</h4>
                {isEnrolled ? (
                  <div className="rating-stars">
                    {[1, 2, 3, 4, 5].map(star => (
                      <span 
                        key={star}
                        className={`star ${userRating >= star ? 'active' : ''}`}
                        onClick={() => handleRateSubmit(star)}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                ) : (
                  <p>You must be enrolled in this course to rate it.</p>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Right column - enrollment card */}
        <div className="enrollment-card">
          <div className="card-price">${contribution.price}</div>
          
          {!isEnrolled ? (
            <>
              <button 
                className="enroll-btn"
                onClick={handleEnroll}
                disabled={enrollmentStatus === 'enrolling'}
              >
                {enrollmentStatus === 'enrolling' ? 'Processing...' : 'Enroll Now'}
              </button>
              
              {!isLoggedIn() && (
                <button 
                  className="login-redirect-btn"
                  onClick={() => navigate('/login', { state: { returnUrl: `/contributions/${id}` } })}
                >
                  Log in to Enroll
                </button>
              )}
              
              {enrollmentError && (
                <div className="enrollment-error">
                  {enrollmentError}
                </div>
              )}
            </>
          ) : (
            <div className="enrolled-message">
              <p>You are enrolled in this course</p>
            </div>
          )}
          
          <div className="course-includes">
            <h4>This course includes:</h4>
            <ul className="includes-list">
              {contribution.videos && (
                <li>
                  <span className="includes-icon">✓</span>
                  {contribution.videos.length} video lessons
                </li>
              )}
              {contribution.notes && (
                <li>
                  <span className="includes-icon">✓</span>
                  {contribution.notes.length} downloadable resources
                </li>
              )}
              <li>
                <span className="includes-icon">✓</span>
                Full lifetime access
              </li>
              <li>
                <span className="includes-icon">✓</span>
                Access on mobile and desktop
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContributionView; 