import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { addContribution, isLoggedIn, BaseUrl } from '../data/ApiCalls'
import { toast, ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import '../styles/AddContrinutions.css'

function AddContributions() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    tags: [{ name: '' }],
    videos: [{ title: '', video_file: null }],
    notes: [{ note_file: null }],
    related_University: '',
    related_Department: '',
    related_Major_Subject: '',
    thumbnail_image: null
  })
  
  // State for dropdown options
  const [universities, setUniversities] = useState([])
  const [departments, setDepartments] = useState([])
  const [majorSubjects, setMajorSubjects] = useState([])
  const [loadingOptions, setLoadingOptions] = useState({
    universities: false,
    departments: false,
    majorSubjects: false
  })

  // Check if user is logged in
  useEffect(() => {
    if (!isLoggedIn()) {
      toast.error('You must be logged in to add contributions')
      navigate('/login')
    } else {
      // Fetch dropdown options
      fetchUniversities()
      fetchDepartments()
      fetchMajorSubjects()
    }
  }, [navigate])

  // Fetch universities from API
  const fetchUniversities = async () => {
    try {
      setLoadingOptions(prev => ({ ...prev, universities: true }))
      const accessToken = localStorage.getItem('access_token')
      
      const response = await fetch(`${BaseUrl}/api/universities/`, {
        headers: {
          'Authorization': accessToken ? `Bearer ${accessToken}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      const result = await response.json()
      
      if (result.status) {
        setUniversities(result.data)
      } else {
        console.error('Failed to fetch universities:', result.message)
      }
    } catch (error) {
      console.error('Error fetching universities:', error)
    } finally {
      setLoadingOptions(prev => ({ ...prev, universities: false }))
    }
  }
  
  // Fetch departments from API
  const fetchDepartments = async () => {
    try {
      setLoadingOptions(prev => ({ ...prev, departments: true }))
      const accessToken = localStorage.getItem('access_token')
      
      const response = await fetch(`${BaseUrl}/api/departments/`, {
        headers: {
          'Authorization': accessToken ? `Bearer ${accessToken}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      const result = await response.json()
      
      if (result.status) {
        setDepartments(result.data)
      } else {
        console.error('Failed to fetch departments:', result.message)
      }
    } catch (error) {
      console.error('Error fetching departments:', error)
    } finally {
      setLoadingOptions(prev => ({ ...prev, departments: false }))
    }
  }
  
  // Fetch major subjects from API
  const fetchMajorSubjects = async () => {
    try {
      setLoadingOptions(prev => ({ ...prev, majorSubjects: true }))
      const accessToken = localStorage.getItem('access_token')
      
      const response = await fetch(`${BaseUrl}/api/major-subjects/`, {
        headers: {
          'Authorization': accessToken ? `Bearer ${accessToken}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      const result = await response.json()
      
      if (result.status) {
        setMajorSubjects(result.data)
      } else {
        console.error('Failed to fetch major subjects:', result.message)
      }
    } catch (error) {
      console.error('Error fetching major subjects:', error)
    } finally {
      setLoadingOptions(prev => ({ ...prev, majorSubjects: false }))
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleTagChange = (e, index) => {
    const { value } = e.target
    const updatedTags = [...formData.tags]
    updatedTags[index] = { name: value }
    setFormData({
      ...formData,
      tags: updatedTags
    })
  }

  const addTag = () => {
    setFormData({
      ...formData,
      tags: [...formData.tags, { name: '' }]
    })
  }

  const handleVideoChange = (e, index, field) => {
    const updatedVideos = [...formData.videos]
    
    if (field === 'title') {
      updatedVideos[index] = { 
        ...updatedVideos[index], 
        title: e.target.value 
      }
    } else if (field === 'video_file') {
      updatedVideos[index] = { 
        ...updatedVideos[index], 
        video_file: e.target.files[0] 
      }
    }
    
    setFormData({
      ...formData,
      videos: updatedVideos
    })
  }

  const addVideo = () => {
    setFormData({
      ...formData,
      videos: [...formData.videos, { title: '', video_file: null }]
    })
  }

  const handleNoteFileChange = (e, index) => {
    const updatedNotes = [...formData.notes]
    updatedNotes[index] = { 
      note_file: e.target.files[0] 
    }
    
    setFormData({
      ...formData,
      notes: updatedNotes
    })
  }

  const addNote = () => {
    setFormData({
      ...formData,
      notes: [...formData.notes, { note_file: null }]
    })
  }

  const handleThumbnailChange = (e) => {
    setFormData({
      ...formData,
      thumbnail_image: e.target.files[0]
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Form validation
    if (!formData.title || !formData.description || !formData.price) {
      toast.error('Please fill in all required fields')
      return
    }

    // Create FormData object for multipart/form-data
    const submitFormData = new FormData()
    submitFormData.append('title', formData.title)
    submitFormData.append('description', formData.description)
    submitFormData.append('price', formData.price)
    
    // Add academic information using UUIDs from dropdowns
    if (formData.related_University) {
      submitFormData.append('related_University', formData.related_University)
    }
    if (formData.related_Department) {
      submitFormData.append('related_Department', formData.related_Department)
    }
    if (formData.related_Major_Subject) {
      submitFormData.append('related_Major_Subject', formData.related_Major_Subject)
    }
    
    // Add thumbnail image
    if (formData.thumbnail_image) {
      submitFormData.append('thumbnail_image', formData.thumbnail_image)
    }
    
    // Add tags
    formData.tags.forEach((tag, index) => {
      if (tag.name) {
        submitFormData.append(`tags[${index}][name]`, tag.name)
      }
    })
    
    // Add videos
    formData.videos.forEach((video, index) => {
      if (video.title && video.video_file) {
        submitFormData.append(`videos[${index}][title]`, video.title)
        submitFormData.append(`videos[${index}][video_file]`, video.video_file)
      }
    })
    
    // Add notes
    formData.notes.forEach((note, index) => {
      if (note.note_file) {
        submitFormData.append(`notes[${index}][note_file]`, note.note_file)
      }
    })

    try {
      setLoading(true)
      const response = await addContribution(submitFormData)
      
      if (response.status === 'success' || response.id) {
        toast.success('Contribution added successfully!')
        navigate('/contributions')
      } else {
        toast.error(response.message || 'Failed to add contribution')
      }
    } catch (error) {
      toast.error('An error occurred while adding your contribution')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="contributions-container">
      <ToastContainer position="top-right" autoClose={5000} />
      <div className="form-container">
        <h1 className="form-title">Add New Contribution</h1>
        
        <form onSubmit={handleSubmit} className={loading ? 'loading' : ''}>
          {/* Basic Information */}
          <div className="form-section">
            <h2 className="section-title">Basic Information</h2>
            <div className="form-row form-row-2">
              <div className="form-group">
                <label htmlFor="title" className="form-label required">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="price" className="form-label required">
                  Price
                </label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="description" className="form-label required">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className="form-textarea"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="thumbnail" className="form-label">
                Thumbnail Image
              </label>
              <input
                type="file"
                id="thumbnail"
                onChange={handleThumbnailChange}
                className="file-input"
                accept="image/*"
              />
            </div>
          </div>
          
          {/* Tags */}
          <div className="form-section">
            <div className="section-header">
              <h2 className="section-title">Tags</h2>
              <button
                type="button"
                onClick={addTag}
                className="add-btn"
              >
                Add Tag
              </button>
            </div>
            
            {formData.tags.map((tag, index) => (
              <div key={index} className="form-group">
                <label className="form-label">
                  Tag {index + 1}
                </label>
                <input
                  type="text"
                  value={tag.name}
                  onChange={(e) => handleTagChange(e, index)}
                  className="form-input"
                  placeholder="Enter tag name"
                />
              </div>
            ))}
          </div>
          
          {/* Videos */}
          <div className="form-section">
            <div className="section-header">
              <h2 className="section-title">Videos</h2>
              <button
                type="button"
                onClick={addVideo}
                className="add-btn"
              >
                Add Video
              </button>
            </div>
            
            {formData.videos.map((video, index) => (
              <div key={index} className="item-card">
                <div className="form-group">
                  <label className="form-label">
                    Video {index + 1} Title
                  </label>
                  <input
                    type="text"
                    value={video.title}
                    onChange={(e) => handleVideoChange(e, index, 'title')}
                    className="form-input"
                    placeholder="Enter video title"
                  />
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    Video File
                  </label>
                  <input
                    type="file"
                    onChange={(e) => handleVideoChange(e, index, 'video_file')}
                    className="file-input"
                    accept="video/*"
                  />
                </div>
              </div>
            ))}
          </div>
          
          {/* Notes */}
          <div className="form-section">
            <div className="section-header">
              <h2 className="section-title">Notes</h2>
              <button
                type="button"
                onClick={addNote}
                className="add-btn"
              >
                Add Note
              </button>
            </div>
            
            {formData.notes.map((note, index) => (
              <div key={index} className="form-group">
                <label className="form-label">
                  Note File {index + 1}
                </label>
                <input
                  type="file"
                  onChange={(e) => handleNoteFileChange(e, index)}
                  className="file-input"
                  accept=".pdf,.doc,.docx"
                />
              </div>
            ))}
          </div>
          
          {/* Academic Information */}
          <div className="form-section">
            <h2 className="section-title">Academic Information</h2>
            <div className="form-row form-row-3">
              <div className="form-group">
                <label htmlFor="university" className="form-label">
                  University
                </label>
                <select
                  id="university"
                  name="related_University"
                  value={formData.related_University}
                  onChange={handleChange}
                  className="form-select"
                  disabled={loadingOptions.universities}
                >
                  <option value="">Select University</option>
                  {universities.map(uni => (
                    <option key={uni.id} value={uni.id}>
                      {uni.name}
                    </option>
                  ))}
                </select>
                {loadingOptions.universities && (
                  <div className="select-loading">Loading universities...</div>
                )}
              </div>
              
              <div className="form-group">
                <label htmlFor="department" className="form-label">
                  Department
                </label>
                <select
                  id="department"
                  name="related_Department"
                  value={formData.related_Department}
                  onChange={handleChange}
                  className="form-select"
                  disabled={loadingOptions.departments}
                >
                  <option value="">Select Department</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
                {loadingOptions.departments && (
                  <div className="select-loading">Loading departments...</div>
                )}
              </div>
              
              <div className="form-group">
                <label htmlFor="subject" className="form-label">
                  Major Subject
                </label>
                <select
                  id="subject"
                  name="related_Major_Subject"
                  value={formData.related_Major_Subject}
                  onChange={handleChange}
                  className="form-select"
                  disabled={loadingOptions.majorSubjects}
                >
                  <option value="">Select Major Subject</option>
                  {majorSubjects.map(subject => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name}
                    </option>
                  ))}
                </select>
                {loadingOptions.majorSubjects && (
                  <div className="select-loading">Loading major subjects...</div>
                )}
              </div>
            </div>
          </div>
          
          <div className="form-submit-container">
            <button
              type="submit"
              disabled={loading}
              className="submit-btn"
            >
              {loading ? 'Submitting...' : 'Submit Contribution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddContributions