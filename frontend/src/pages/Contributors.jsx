import React, { useState, useEffect } from 'react';
import { BaseUrl } from '../data/ApiCalls';
import { FaTrophy, FaMedal, FaAward, FaChartLine, FaStar, FaGraduationCap, FaExclamationCircle } from 'react-icons/fa';
import '../styles/Contributors.css';

function Contributors() {
  const [contributors, setContributors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchContributors = async () => {
      try {
        const response = await fetch(`${BaseUrl}/api/all-contributions/`);
        const result = await response.json();
        
        if (result.status) {
          // Process contributions to get contributor stats
          const contributorStats = {};
          
          result.data.forEach(contribution => {
            if (!contributorStats[contribution.user?.id]) {
              contributorStats[contribution.user?.id] = {
                id: contribution.user?.id,
                name: contribution.user?.username || 'Anonymous',
                totalContributions: 0,
                totalRating: 0,
                averageRating: 0,
                contributions: []
              };
            }
            
            contributorStats[contribution.user?.id].totalContributions++;
            if (contribution.rating) {
              contributorStats[contribution.user?.id].totalRating += parseFloat(contribution.rating);
              contributorStats[contribution.user?.id].averageRating = 
                contributorStats[contribution.user?.id].totalRating / 
                contributorStats[contribution.user?.id].totalContributions;
            }
            contributorStats[contribution.user?.id].contributions.push(contribution);
          });

          // Convert to array and sort by contributions and rating
          const sortedContributors = Object.values(contributorStats)
            .sort((a, b) => {
              if (b.totalContributions !== a.totalContributions) {
                return b.totalContributions - a.totalContributions;
              }
              return b.averageRating - a.averageRating;
            });

          setContributors(sortedContributors);
        } else {
          setError(result.message || 'Failed to fetch contributors');
        }
      } catch (error) {
        console.error('Error fetching contributors:', error);
        setError('An error occurred while fetching contributors');
      } finally {
        setLoading(false);
      }
    };

    fetchContributors();
  }, []);

  const getContributorBadge = (index) => {
    switch(index) {
      case 0:
        return <FaTrophy className="badge gold" title="Gold Contributor" />;
      case 1:
        return <FaMedal className="badge silver" title="Silver Contributor" />;
      case 2:
        return <FaAward className="badge bronze" title="Bronze Contributor" />;
      default:
        return null;
    }
  };

  const getTotalEnrollments = (contributor) => {
    return contributor.contributions.reduce((total, contribution) => {
      return total + (contribution.total_enrollments || 0);
    }, 0);
  };

  if (loading) {
    return (
      <div className="contributors-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading contributors...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="contributors-container">
        <div className="error-container">
          <FaExclamationCircle className="error-icon" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="contributors-container">
      <div className="contributors-header">
        <h1>Our Top Contributors</h1>
        <p className="subtitle">Celebrating the educators shaping our community's success</p>
        
        <div className="stats-overview">
          <div className="stat-card">
            <FaChartLine className="stat-icon" />
            <div className="stat-content">
              <h3>{contributors.length}</h3>
              <p>Active Contributors</p>
            </div>
          </div>
          <div className="stat-card">
            <FaStar className="stat-icon" />
            <div className="stat-content">
              <h3>{contributors.reduce((sum, c) => sum + c.totalContributions, 0)}</h3>
              <p>Total Contributions</p>
            </div>
          </div>
          <div className="stat-card">
            <FaGraduationCap className="stat-icon" />
            <div className="stat-content">
              <h3>{contributors.reduce((sum, c) => sum + getTotalEnrollments(c), 0)}</h3>
              <p>Total Enrollments</p>
            </div>
          </div>
        </div>
      </div>

      <div className="contributors-grid">
        {contributors.map((contributor, index) => (
          <div key={contributor.id} 
               className={`contributor-card ${index < 3 ? `top-${index + 1}` : ''}`}>
            <div className="card-header">
              {getContributorBadge(index)}
              <div className="rank-circle">{index + 1}</div>
              <div className="contributor-avatar">
                <img 
                  src={contributor.profile_picture || '/images/default-avatar.png'} 
                  alt={contributor.name}
                  onError={(e) => {
                    e.target.src = '/images/default-avatar.png';
                  }}
                />
              </div>
              <h2>{contributor.name}</h2>
              <p className="joined-date">Member since {new Date(contributor.joined_date || Date.now()).getFullYear()}</p>
            </div>

            <div className="card-body">
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{contributor.totalContributions}</span>
                  <span className="stat-label">Contributions</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">
                    {contributor.averageRating ? 
                      <>
                        <FaStar className="star-icon" />
                        {contributor.averageRating.toFixed(1)}
                      </> : 
                      'N/A'}
                  </span>
                  <span className="stat-label">Avg Rating</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{getTotalEnrollments(contributor)}</span>
                  <span className="stat-label">Enrollments</span>
                </div>
              </div>

              <div className="contributions-preview">
                <h3>Recent Contributions</h3>
                <div className="preview-list">
                  {contributor.contributions.slice(0, 3).map(contribution => (
                    <div key={contribution.id} className="preview-item">
                      <div className="preview-content">
                        <h4>{contribution.title}</h4>
                        <div className="preview-meta">
                          {contribution.rating && (
                            <span className="rating">
                              <FaStar className="star-icon" />
                              {contribution.rating}
                            </span>
                          )}
                          <span className="enrollments">
                            {contribution.total_enrollments || 0} enrolled
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Contributors;