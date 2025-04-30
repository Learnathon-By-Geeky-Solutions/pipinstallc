import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BaseUrl, isLoggedIn } from '../data/ApiCalls';
import Navbar from '../Components/Navbar';
import '../styles/Profile.css';

function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    university: '',
    department: '',
    major_subject: '',
    profile_picture: null
  });
  
  // State for dropdown options
  const [universities, setUniversities] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [majorSubjects, setMajorSubjects] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate('/login');
      return;
    }
    fetchUserInfo();
    fetchDropdownOptions();
  }, [navigate]);

  const fetchUserInfo = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const response = await fetch(`${BaseUrl}/api/user-info/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      
      const result = await response.json();
      if (result.status) {
        setProfileData({
          username: result.data.username || '',
          email: result.data.email || '',
          phone_number: result.data.phone_number || '',
          date_of_birth: result.data.date_of_birth || '',
          university: result.data.university?.id || '',
          department: result.data.department?.id || '',
          major_subject: result.data.major_subject?.id || '',
          profile_picture: result.data.profile_picture
        });
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDropdownOptions = async () => {
    try {
      // Fetch universities
      const uniResponse = await fetch(`${BaseUrl}/api/universities/`);
      const uniResult = await uniResponse.json();
      if (uniResult.status) {
        setUniversities(uniResult.data);
      }
      
      // Fetch departments
      const deptResponse = await fetch(`${BaseUrl}/api/departments/`);
      const deptResult = await deptResponse.json();
      if (deptResult.status) {
        setDepartments(deptResult.data);
      }
      
      // Fetch major subjects
      const subjectResponse = await fetch(`${BaseUrl}/api/major-subjects/`);
      const subjectResult = await subjectResponse.json();
      if (subjectResult.status) {
        setMajorSubjects(subjectResult.data);
      }
    } catch (error) {
      console.error('Error fetching options:', error);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setProfileData(prev => ({
        ...prev,
        profile_picture: URL.createObjectURL(file)
      }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUpdating(true);

    try {
      const accessToken = localStorage.getItem('access_token');
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
      };

      // If there's a new profile picture, send it as form data
      if (selectedImage) {
        const formData = new FormData();
        formData.append('profile_picture', selectedImage);
        
        await fetch(`${BaseUrl}/api/user-info/`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${accessToken}`
          },
          body: formData
        });
      }

      // Send other data as JSON
      const jsonData = {
        phone_number: profileData.phone_number || '',
        date_of_birth: profileData.date_of_birth || '',
        university: profileData.university || '',
        department: profileData.department || '',
        major_subject: profileData.major_subject || ''
      };

      const response = await fetch(`${BaseUrl}/api/user-info/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
      });

      const result = await response.json();
      if (result.status) {
        alert('Profile updated successfully!');
        fetchUserInfo(); // Refresh the profile data
      } else {
        alert(result.message || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('An error occurred while updating your profile');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <Navbar />
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <Navbar />
      <div className="profile-container">
        <h1>Profile Settings</h1>
        <form onSubmit={handleSubmit} className="profile-form">
          <div className="profile-image-section">
            <div className="profile-image-container">
              {profileData.profile_picture ? (
                <img 
                  src={typeof profileData.profile_picture === 'string' ? profileData.profile_picture : URL.createObjectURL(profileData.profile_picture)} 
                  alt="Profile" 
                  className="profile-image"
                />
              ) : (
                <div className="profile-image-placeholder">
                  <span>{profileData.username?.charAt(0)?.toUpperCase()}</span>
                </div>
              )}
            </div>
            <div className="image-upload">
              <label htmlFor="profile_picture" className="upload-button">
                Change Profile Picture
              </label>
              <input
                type="file"
                id="profile_picture"
                accept="image/*"
                onChange={handleImageChange}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={profileData.username}
                disabled
                className="form-input disabled"
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={profileData.email}
                disabled
                className="form-input disabled"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Phone Number</label>
              <input
                type="tel"
                name="phone_number"
                value={profileData.phone_number}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your phone number"
              />
            </div>
            <div className="form-group">
              <label>Date of Birth</label>
              <input
                type="date"
                name="date_of_birth"
                value={profileData.date_of_birth}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>University</label>
              <select
                name="university"
                value={profileData.university}
                onChange={handleChange}
                className="form-select"
              >
                <option value="">Select University</option>
                {universities.map(uni => (
                  <option key={uni.id} value={uni.id}>
                    {uni.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Department</label>
              <select
                name="department"
                value={profileData.department}
                onChange={handleChange}
                className="form-select"
              >
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Major Subject</label>
              <select
                name="major_subject"
                value={profileData.major_subject}
                onChange={handleChange}
                className="form-select"
              >
                <option value="">Select Major Subject</option>
                {majorSubjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="save-button" 
              disabled={updating}
            >
              {updating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Profile;