import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUserContributions, deleteContribution } from '../data/ApiCalls'
import { toast, ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import '../styles/UserContributions.css'
import { FaPlus, FaEdit, FaTrash } from 'react-icons/fa'
import { ThreeDots } from 'react-loader-spinner'

function UserContributions() {
  const navigate = useNavigate()
  const [contributions, setContributions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteId, setDeleteId] = useState(null)

  // Fetch user contributions on component mount
  useEffect(() => {
    fetchContributions()
  }, [])

  const fetchContributions = async () => {
    try {
      setLoading(true)
      const response = await getUserContributions()
      
      if (Array.isArray(response)) {
        setContributions(response)
      } else {
        toast.error(response.message || 'Failed to load contributions')
      }
    } catch (error) {
      console.error('Error fetching contributions:', error)
      toast.error('An error occurred while loading your contributions')
    } finally {
      setLoading(false)
    }
  }

  const handleAddContribution = () => {
    navigate('/add-contributions')
  }

  const handleEditContribution = (id) => {
    navigate(`/update-contributions/${id}`)
  }

  const confirmDelete = (id) => {
    setDeleteId(id)
    setShowDeleteModal(true)
  }

  const handleDeleteContribution = async () => {
    if (!deleteId) return
    
    try {
      setLoading(true)
      const response = await deleteContribution(deleteId)
      
      if (response.status) {
        toast.success('Contribution deleted successfully')
        // Remove the deleted contribution from state
        setContributions(contributions.filter(item => item.id !== deleteId))
      } else {
        toast.error(response.message || 'Failed to delete contribution')
      }
    } catch (error) {
      console.error('Error deleting contribution:', error)
      toast.error('An error occurred while deleting the contribution')
    } finally {
      setShowDeleteModal(false)
      setDeleteId(null)
      setLoading(false)
    }
  }

  const cancelDelete = () => {
    setShowDeleteModal(false)
    setDeleteId(null)
  }

  // Function to handle image paths correctly
  const getImageUrl = (item) => {
    if (item.thumbnail_image) {
      // If thumbnail_image starts with '/', it's a relative URL
      if (item.thumbnail_image.startsWith('/')) {
        return `http://127.0.0.1:8000${item.thumbnail_image}`
      }
      return item.thumbnail_image
    }
    return 'https://via.placeholder.com/300x180?text=No+Image'
  }

  // Function to format price display
  const formatPrice = (price) => {
    return typeof price === 'string' && price.includes('.') 
      ? `$${price}` 
      : `$${price}.00`
  }

  return (
    <div className="user-contributions ">
      <ToastContainer position="top-right" autoClose={5000} />
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">My Contributions</h1>
          <button 
            className="add-button" 
            onClick={handleAddContribution}
          >
            <FaPlus /> Add New Contribution
          </button>
        </div>

        {loading ? (
          <div className="loading">
            <ThreeDots 
              height="80" 
              width="80" 
              color="#6c2bb3" 
              ariaLabel="loading"
              visible={true}
            />
          </div>
        ) : contributions.length === 0 ? (
          <div className="empty-state">
            <h2>No contributions yet</h2>
            <p>Add your first contribution to get started</p>
            <button 
              className="add-button" 
              onClick={handleAddContribution}
            >
              <FaPlus /> Add New Contribution
            </button>
          </div>
        ) : (
          <div className="contributions-grid">
            {contributions.map((item) => (
              <div key={item.id} className="contribution-card">
                <img 
                  src={getImageUrl(item)} 
                  alt={item.title} 
                  className="card-thumbnail" 
                />
                <div className="card-content">
                  <h2 className="card-title">{item.title}</h2>
            
                  
                  <div className="card-footer">
                    <button 
                      className="card-button edit-button"
                      onClick={() => handleEditContribution(item.id)}
                    >
                      <FaEdit /> Edit
                    </button>
                    <button 
                      className="card-button delete-button"
                      onClick={() => confirmDelete(item.id)}
                    >
                      <FaTrash /> Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2 className="modal-title">Confirm Deletion</h2>
            <p className="modal-message">Are you sure you want to delete this contribution? This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-button cancel-button" onClick={cancelDelete}>
                Cancel
              </button>
              <button className="modal-button confirm-button" onClick={handleDeleteContribution}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserContributions