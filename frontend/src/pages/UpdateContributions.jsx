import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getContributionById, updateContribution, isLoggedIn } from '../data/ApiCalls'
import { toast, ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import '../styles/AddContrinutions.css'

function UpdateContributions() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    tags: [],
    videos: [],
    notes: [],
    related_University: '',
    related_Department: '',
    related_Major_Subject: '',
    thumbnail_image: null
  })
  const [originalThumbnail, setOriginalThumbnail] = useState(null)

  // Check if user is logged in and fetch contribution data
  useEffect(() => {
    if (!isLoggedIn()) {
      toast.error('You must be logged in to update contributions')
      navigate('/login')
      return
    }
    
    fetchContribution()
  }, [id, navigate])

  const fetchContribution = async () => {
    try {
      setLoading(true)
      const response = await getContributionById(id)
      
      if (response && response.id) {
        // Prepare form data from response
        const contributionData = {
          title: response.title || '',
          description: response.description || '',
          price: response.price || '',
          tags: response.tags?.length ? response.tags : [{ name: '' }],
          videos: response.videos?.length ? response.videos : [{ title: '', video_file: null }],
          notes: response.notes?.length ? response.notes.map(note => ({ note_file: null })) : [{ note_file: null }],
          related_University: response.related_University || '',
          related_Department: response.related_Department || '',
          related_Major_Subject: response.related_Major_Subject || '',
          thumbnail_image: null
        }
        
        setFormData(contributionData)
        
        // Store original thumbnail URL
        if (response.thumbnail_image) {
          setOriginalThumbnail(response.thumbnail_image)
        }
      } else {
        toast.error('Failed to load contribution data')
        navigate('/user-contributions')
      }
    } catch (error) {
      console.error('Error fetching contribution:', error)
      toast.error('An error occurred while loading contribution data')
      navigate('/user-contributions')
    } finally {
      setLoading(false)
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
    updatedTags[index] = { ...updatedTags[index], name: value }
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
      ...updatedNotes[index],
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
    submitFormData.append('related_University', formData.related_University)
    submitFormData.append('related_Department', formData.related_Department)
    submitFormData.append('related_Major_Subject', formData.related_Major_Subject)
    
    // Add thumbnail image only if changed
    if (formData.thumbnail_image) {
      submitFormData.append('thumbnail_image', formData.thumbnail_image)
    }
    
    // Add tags
    formData.tags.forEach((tag, index) => {
      if (tag.name) {
        submitFormData.append(`tags[${index}][name]`, tag.name)
      }
    })
    
    // Add videos - only add file if it's a new file
    formData.videos.forEach((video, index) => {
      if (video.title) {
        submitFormData.append(`videos[${index}][title]`, video.title)
        
        if (video.video_file) {
          submitFormData.append(`videos[${index}][video_file]`, video.video_file)
        }
        
        // If there's an existing video ID, include it for reference
        if (video.id) {
          submitFormData.append(`videos[${index}][id]`, video.id)
        }
      }
    })
    
    // Add notes - only add file if it's a new file
    formData.notes.forEach((note, index) => {
      if (note.note_file) {
        submitFormData.append(`notes[${index}][note_file]`, note.note_file)
      }
      
      // If there's an existing note ID, include it for reference
      if (note.id) {
        submitFormData.append(`notes[${index}][id]`, note.id)
      }
    })

    try {
      setSubmitting(true)
      const response = await updateContribution(id, submitFormData)
      
      if (response.id) {
        toast.success('Contribution updated successfully!')
        navigate('/user-contributions')
      } else {
        toast.error(response.message || 'Failed to update contribution')
      }
    } catch (error) {
      toast.error('An error occurred while updating your contribution')
      console.error(error)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="contributions-container">
        <div className="loading">
          <p>Loading contribution data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="contributions-container">
      <ToastContainer position="top-right" autoClose={5000} />
      <div className="form-container">
        <h1 className="form-title">Update Contribution</h1>
        
        <form onSubmit={handleSubmit} className={submitting ? 'loading' : ''}>
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
                Thumbnail Image {originalThumbnail && '(Leave empty to keep current image)'}
              </label>
              {originalThumbnail && (
                <div className="current-thumbnail">
                  <img 
                    src={originalThumbnail} 
                    alt="Current thumbnail" 
                    style={{ maxWidth: '200px', marginBottom: '10px' }} 
                  />
                </div>
              )}
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
                {video.id && (
                  <div className="form-group">
                    <small>Current video: {video.title || video.id}</small>
                  </div>
                )}
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
                    Video File {video.id && '(Leave empty to keep current file)'}
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
                {note.id && (
                  <div>
                    <small>Current note file: {note.id}</small>
                  </div>
                )}
                <label className="form-label">
                  Note File {index + 1} {note.id && '(Leave empty to keep current file)'}
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
                <input
                  type="text"
                  id="university"
                  name="related_University"
                  value={formData.related_University}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Enter university name"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="department" className="form-label">
                  Department
                </label>
                <input
                  type="text"
                  id="department"
                  name="related_Department"
                  value={formData.related_Department}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Enter department name"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="subject" className="form-label">
                  Major Subject
                </label>
                <input
                  type="text"
                  id="subject"
                  name="related_Major_Subject"
                  value={formData.related_Major_Subject}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Enter major subject"
                />
              </div>
            </div>
          </div>
          
          <div className="form-submit-container">
            <button
              type="button"
              onClick={() => navigate('/user-contributions')}
              className="cancel-btn"
              style={{
                marginRight: '10px',
                background: '#f0f0f0',
                color: '#333',
                border: 'none',
                padding: '0.75rem 2rem',
                borderRadius: '6px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="submit-btn"
            >
              {submitting ? 'Updating...' : 'Update Contribution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UpdateContributions