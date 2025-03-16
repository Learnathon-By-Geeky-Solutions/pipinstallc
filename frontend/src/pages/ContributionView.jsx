import React, { useState, useEffect } from 'react';
import Navbar from '../Components/Navbar';
import { useParams } from 'react-router-dom';
import '../styles/ContributionView.css';

function ContributionView() {
  // const { id } = useParams(); // Commented out for now
  const [isMenuHidden, setIsMenuHidden] = useState(false);
  const [activeTab, setActiveTab] = useState('Transcript');
  const [activeVideoIndex, setActiveVideoIndex] = useState(0);
  const [contentData, setContentData] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentVideo, setCurrentVideo] = useState(null);

  // Using fixed "learn-algorithm" as example
  // TODO: Replace with dynamic ID from useParams when connecting to API
  const exampleId = 'learn-algorithm';
  
  // Fetch course data based on course ID
  useEffect(() => {
    const fetchCourseData = async () => {
      setLoading(true);
      try {
        // Simulating API response with fixed example data
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/courses/${id}`);
        // const data = await response.json();
        setTimeout(() => {
          const mockData = {
            'learn-algorithm': {
              title: 'Learn Algorithm',
              section: 'DSA',
              subsection: 'Week 1',
              content: [
                { 
                  title: 'Welcome to Algorithms', 
                  duration: '2 min', 
                  completed: true,
                  videoUrl: 'https://example.com/videos/algo-intro.mp4',
                  transcript: 'Welcome to Algorithms. In this course, we\'ll explore the fundamental concepts of algorithmic thinking and problem-solving techniques.'
                },
                { 
                  title: 'Basic Concepts', 
                  duration: '4 min', 
                  completed: false,
                  videoUrl: 'https://example.com/videos/algo-basics.mp4',
                  transcript: 'In this video, we\'ll cover the basic concepts of algorithms including time complexity, space complexity, and Big O notation.'
                },
                { 
                  title: 'Practice Problems', 
                  duration: '10 min', 
                  completed: false,
                  videoUrl: 'https://example.com/videos/algo-practice.mp4',
                  transcript: 'Let\'s work through some practice problems to reinforce the concepts we\'ve learned so far.'
                },
              ]
            }
            // Other course data commented out for now
            /*
            'easy-algorithm': {
              title: 'Easy Algorithm',
              section: 'DSA',
              subsection: 'Week 2',
              content: [
                { 
                  title: 'Introduction to Sorting', 
                  duration: '3 min', 
                  completed: true,
                  videoUrl: 'https://example.com/videos/sorting-intro.mp4',
                  transcript: 'Sorting is a fundamental operation in computer science. In this video, we\'ll introduce various sorting algorithms.'
                },
                { 
                  title: 'Bubble Sort', 
                  duration: '5 min', 
                  completed: false,
                  videoUrl: 'https://example.com/videos/bubble-sort.mp4',
                  transcript: 'Bubble sort is a simple sorting algorithm that repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order.'
                }
              ]
            },
            'advanced-algorithm': {
              title: 'Advanced Algorithm',
              section: 'DSA',
              subsection: 'Week 3',
              content: [
                { 
                  title: 'Introduction to Graphs', 
                  duration: '4 min', 
                  completed: false,
                  videoUrl: 'https://example.com/videos/graph-intro.mp4',
                  transcript: 'Graphs are versatile data structures that can model a wide variety of problems. In this video, we\'ll introduce graph concepts and representations.'
                },
                { 
                  title: 'DFS and BFS', 
                  duration: '7 min', 
                  completed: false,
                  videoUrl: 'https://example.com/videos/dfs-bfs.mp4',
                  transcript: 'Depth-First Search (DFS) and Breadth-First Search (BFS) are two fundamental graph traversal algorithms.'
                }
              ]
            }
            */
          };
          
          setContentData(mockData);
          setLoading(false);
        }, 800);
      } catch (error) {
        console.error("Error fetching course data:", error);
        setLoading(false);
      }
    };

    fetchCourseData();
  }, []);  // Removed id dependency since we're using fixed example

  // Set current video when course data or active index changes
  useEffect(() => {
    if (contentData[exampleId] && contentData[exampleId].content && contentData[exampleId].content.length > 0) {
      setCurrentVideo(contentData[exampleId].content[activeVideoIndex]);
    }
  }, [contentData, activeVideoIndex]);

  // Handle video selection from sidebar
  const handleVideoSelect = (index) => {
    setActiveVideoIndex(index); // Update the active video index
    console.log(`Playing video: ${contentData[exampleId]?.content[index]?.title}`);
    
    // Set the current video based on the selected index
    setCurrentVideo(contentData[exampleId].content[index]);
    
    // TODO: In the future, we might want to track progress or update completion status
  };

  // Loading state
  if (loading) {
    return (
      <div className="contribution-view">
        <Navbar />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading course content...</p>
        </div>
      </div>
    );
  }

  // Error state - no content found (keeping this for future use)
  if (!contentData[exampleId] || !contentData[exampleId].content || contentData[exampleId].content.length === 0) {
    return (
      <div className="contribution-view">
        <Navbar />
        <div className="error-container">
          <h2>Course Not Found</h2>
          <p>Sorry, we couldn't find the course you're looking for.</p>
        </div>
      </div>
    );
  }

  const course = contentData[exampleId];

  return (
    <div className="contribution-view">
      <Navbar />
      
      {/* Breadcrumb Navigation */}
      <div className="breadcrumb">
        <button 
          onClick={() => setIsMenuHidden(!isMenuHidden)}
          className="menu-toggle-btn"
        >
          {isMenuHidden ? 'Show menu' : 'Hide menu'}
        </button>
        <span className="breadcrumb-separator">›</span>
        <span>{course.title}</span>
        {/* <span className="breadcrumb-separator">›</span>
        <span>{course.subsection}</span> */}
        <span className="breadcrumb-separator">›</span>
        <span>{currentVideo?.title || course.title}</span>
      </div>

      <div className="content-container">
        {/* Left Sidebar */}
        {!isMenuHidden && (
          <div className="sidebar">
            <div className="sidebar-section">
              <h4 className="sidebar-title">Overview of {course.title}</h4>
              <div className="sidebar-items">
                {course.content.map((item, index) => (
                  <div 
                    key={index} 
                    className={`sidebar-item ${activeVideoIndex === index ? 'active' : ''}`}
                    onClick={() => handleVideoSelect(index)}
                  >
                    <div className={`completion-indicator ${activeVideoIndex === index ? 'active' : ''} ${item.completed ? 'completed' : ''}`}>
                      {activeVideoIndex === index && (
                        <svg className="check-icon" viewBox="0 0 24 24">
                          <path d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                    <span className="item-title">{item.title}</span>
                    <span className="item-duration">{item.duration}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className={`main-content ${isMenuHidden ? 'full-width' : ''}`}>
          <div className="content-wrapper">
            {/* Video Player Section */}
            <div className="video-player">
              {/* In a real implementation, replace this with an actual video player */}
              <div className="video-placeholder">
                <div className="placeholder-text">{currentVideo?.title || 'Select a video'}</div>
              </div>
              {/* Video Controls */}
              <div className="video-controls">
                <div className="controls-container">
                  <button 
                    className="play-button" 
                    onClick={() => console.log(`Playing video: ${currentVideo?.title}`)} // Handle video play
                  >
                    <svg viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </button>
                  <div className="progress-bar">
                    <div className="progress-indicator"></div>
                  </div>
                  <span className="time-display">0:00 / {currentVideo?.duration || '0:00'}</span>
                </div>
              </div>
            </div>

            {/* Content Tabs */}
            <div className="content-tabs">
              <nav className="tabs-nav">
                {['Transcript', 'Notes', 'Downloads'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`tab-button ${activeTab === tab ? 'active' : ''}`}
                  >
                    {tab}
                  </button>
                ))}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {activeTab === 'Transcript' && (
                <div className="transcript-item">
                  <span className="timestamp">0:01</span>
                  <p className="transcript-text">
                    {currentVideo?.transcript || 'No transcript available for this video.'}
                  </p>
                </div>
              )}
              {activeTab === 'Notes' && (
                <div className="notes-content">
                  <textarea 
                    className="notes-textarea" 
                    placeholder="Take notes here..."
                  ></textarea>
                </div>
              )}
              {activeTab === 'Downloads' && (
                <div className="downloads-content">
                  <p>No downloads available for this video.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContributionView; 