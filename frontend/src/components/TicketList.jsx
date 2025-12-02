import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, RefreshCw, AlertCircle, Zap, CheckCircle, Clock, XCircle, Loader, Plus, X, Edit2, Trash2 } from 'lucide-react'
import { ticketService } from '../services/ticketService'
import { 
  TICKET_PRIORITY, 
  TICKET_PRIORITY_LABELS, 
  TICKET_PRIORITY_TO_API,
  API_PRIORITY_TO_NUMBER,
  TICKET_CATEGORY, 
  TICKET_CATEGORY_LABELS,
  TICKET_STATUS,
  TICKET_STATUS_LABELS,
  STORAGE_KEYS 
} from '../config/constants'
import '../styles/components/TicketList.css'

function TicketList() {
  // Get initial user email
  const getUserEmail = () => {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA)
    if (userData) {
      try {
        const user = JSON.parse(userData)
        return user.email || ''
      } catch {
        return ''
      }
    }
    return ''
  }

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [editingTicket, setEditingTicket] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: TICKET_PRIORITY.MEDIUM,
    category: TICKET_CATEGORY.OTHER,
    user_email: getUserEmail()
  })

  useEffect(() => {
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const data = await ticketService.getAll()
      setTickets(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityClass = (priority) => {
    // Handle both string (from API) and number (from frontend)
    if (typeof priority === 'string') {
      return priority
    }
    const priorityMap = {
      1: 'critical',
      2: 'high', 
      3: 'medium',
      4: 'low'
    }
    return priorityMap[priority] || 'medium'
  }

  const getPriorityLabel = (priority) => {
    // Handle both string (from API) and number (from frontend)
    if (typeof priority === 'string') {
      const num = API_PRIORITY_TO_NUMBER[priority]
      return TICKET_PRIORITY_LABELS[num] || 'Medium'
    }
    return TICKET_PRIORITY_LABELS[priority] || 'Medium'
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      'open': { label: 'Open', class: 'status-open' },
      'in_progress': { label: 'In Progress', class: 'status-progress' },
      'assigned_to_human': { label: 'Assigned to Human', class: 'status-assigned' },
      'resolved': { label: 'Resolved', class: 'status-resolved' },
      'closed': { label: 'Closed', class: 'status-closed' }
    }
    return statusMap[status] || { label: TICKET_STATUS_LABELS[status] || status, class: 'status-open' }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    return date.toLocaleDateString()
  }

  const handleCreateTicket = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      // Convert priority number to API string
      const ticketData = {
        ...formData,
        priority: TICKET_PRIORITY_TO_API[formData.priority]
      }
      await ticketService.create(ticketData)
      await fetchTickets()
      setShowCreateModal(false)
      // Reset form but keep user email
      setFormData({
        title: '',
        description: '',
        priority: TICKET_PRIORITY.MEDIUM,
        category: TICKET_CATEGORY.OTHER,
        user_email: getUserEmail()
      })
    } catch (err) {
      alert('Error creating ticket: ' + err.message)
    } finally {
      setCreating(false)
    }
  }

  const handleEditTicket = (ticket) => {
    setEditingTicket(ticket)
    setFormData({
      title: ticket.title,
      description: ticket.description,
      priority: API_PRIORITY_TO_NUMBER[ticket.priority] || TICKET_PRIORITY.MEDIUM,
      category: ticket.category || TICKET_CATEGORY.OTHER,
      status: ticket.status || TICKET_STATUS.OPEN,
      user_email: ticket.user_email
    })
    setShowEditModal(true)
  }

  const handleUpdateTicket = async (e) => {
    e.preventDefault()
    setUpdating(true)
    try {
      // Convert priority number to API string
      const ticketData = {
        title: formData.title,
        description: formData.description,
        priority: TICKET_PRIORITY_TO_API[formData.priority],
        category: formData.category,
        status: formData.status,
        user_email: formData.user_email
      }
      await ticketService.update(editingTicket.id, ticketData)
      await fetchTickets()
      setShowEditModal(false)
      setEditingTicket(null)
      // Reset form with user email
      setFormData({
        title: '',
        description: '',
        priority: TICKET_PRIORITY.MEDIUM,
        category: TICKET_CATEGORY.OTHER,
        status: TICKET_STATUS.OPEN,
        user_email: getUserEmail()
      })
    } catch (err) {
      alert('Error updating ticket: ' + err.message)
    } finally {
      setUpdating(false)
    }
  }

  const handleDeleteTicket = async (ticketId) => {
    if (!confirm('Are you sure you want to delete this ticket?')) return
    
    try {
      await ticketService.delete(ticketId)
      await fetchTickets()
    } catch (err) {
      alert('Error deleting ticket: ' + err.message)
    }
  }

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'all') return true
    if (filter === 'open') return ticket.status === 'open'
    if (filter === 'in_progress') return ticket.status === 'in_progress'
    if (filter === 'assigned_to_human') return ticket.status === 'assigned_to_human'
    if (filter === 'resolved') return ticket.status === 'resolved'
    if (filter === 'closed') return ticket.status === 'closed'
    if (filter === 'critical') return ticket.priority === 'critical' || ticket.priority === 1
    return true
  })

  if (loading) {
    return (
      <div className="ticket-list-container">
        <div className="loading-spinner">
          <Loader className="spinner" size={50} />
          <p>Loading tickets...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="ticket-list-container">
        <div className="error-message">
          <AlertCircle className="error-icon" size={48} />
          <p>{error}</p>
          <button onClick={fetchTickets} className="retry-btn">
            <RefreshCw size={18} />
            <span>Retry</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="ticket-list-container">
      <div className="ticket-header">
        <div className="header-left">
          <h1>Support Tickets</h1>
        </div>
        <div className="header-actions">
          <button onClick={() => setShowCreateModal(true)} className="create-ticket-btn">
            <Plus size={18} />
            <span>Create Ticket</span>
          </button>
          <button onClick={fetchTickets} className="refresh-btn">
            <RefreshCw size={18} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="filter-tabs">
        <button 
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({tickets.length})
        </button>
        <button 
          className={`filter-tab ${filter === 'open' ? 'active' : ''}`}
          onClick={() => setFilter('open')}
        >
          Open ({tickets.filter(t => t.status === 'open').length})
        </button>
        <button 
          className={`filter-tab ${filter === 'in_progress' ? 'active' : ''}`}
          onClick={() => setFilter('in_progress')}
        >
          In Progress ({tickets.filter(t => t.status === 'in_progress').length})
        </button>
        <button 
          className={`filter-tab ${filter === 'assigned_to_human' ? 'active' : ''}`}
          onClick={() => setFilter('assigned_to_human')}
        >
          Assigned ({tickets.filter(t => t.status === 'assigned_to_human').length})
        </button>
        <button 
          className={`filter-tab ${filter === 'resolved' ? 'active' : ''}`}
          onClick={() => setFilter('resolved')}
        >
          Resolved ({tickets.filter(t => t.status === 'resolved').length})
        </button>
        <button 
          className={`filter-tab ${filter === 'closed' ? 'active' : ''}`}
          onClick={() => setFilter('closed')}
        >
          Closed ({tickets.filter(t => t.status === 'closed').length})
        </button>
        <button 
          className={`filter-tab ${filter === 'critical' ? 'active' : ''}`}
          onClick={() => setFilter('critical')}
        >
          Critical ({tickets.filter(t => t.priority === 'critical' || t.priority === 1).length})
        </button>
      </div>

      {filteredTickets.length === 0 ? (
        <div className="empty-state">
          <XCircle className="empty-icon" size={64} />
          <h3>No tickets found</h3>
          <p>No tickets match the current filter</p>
        </div>
      ) : (
        <div className="tickets-grid">
          {filteredTickets.map(ticket => {
            const status = getStatusBadge(ticket.status)
            const priorityClass = getPriorityClass(ticket.priority)
            const priorityLabel = getPriorityLabel(ticket.priority)

            return (
              <div key={ticket.id} className={`ticket-card priority-${priorityClass}`}>
                <div className="ticket-card-header">
                  <div className="ticket-id">#{ticket.id}</div>
                  <div className="ticket-badges">
                    <span className={`badge ${status.class}`}>
                      {ticket.status === 'resolved' ? <CheckCircle size={12} /> :
                       ticket.status === 'in_progress' ? <Clock size={12} /> :
                       <AlertCircle size={12} />}
                      <span>{status.label}</span>
                    </span>
                    <span className={`badge priority-badge-${priorityClass}`}>
                      <Zap size={12} />
                      <span>{priorityLabel}</span>
                    </span>
                  </div>
                </div>

                <div className="ticket-card-body">
                  <h3 className="ticket-title">{ticket.title}</h3>
                  <p className="ticket-description">
                    {ticket.description.length > 150 
                      ? ticket.description.substring(0, 150) + '...'
                      : ticket.description
                    }
                  </p>
                </div>

                <div className="ticket-card-footer">
                  <div className="ticket-meta">
                    <span className="ticket-user">{ticket.user_email.split('@')[0]}</span>
                    <span className="ticket-time">{formatDate(ticket.created_at)}</span>
                  </div>
                  <div className="ticket-actions">
                    {ticket.category && (
                      <span className="ticket-category">
                        {TICKET_CATEGORY_LABELS[ticket.category] || ticket.category}
                      </span>
                    )}
                    <button 
                      className="ticket-action-btn edit-btn"
                      onClick={() => handleEditTicket(ticket)}
                      title="Edit ticket"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button 
                      className="ticket-action-btn delete-btn"
                      onClick={() => handleDeleteTicket(ticket.id)}
                      title="Delete ticket"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Ticket</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleCreateTicket} className="ticket-form">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  placeholder="Brief description of the issue"
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  placeholder="Detailed description of the issue"
                  rows="5"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="priority">Priority</label>
                  <select
                    id="priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                  >
                    <option value={TICKET_PRIORITY.LOW}>Low</option>
                    <option value={TICKET_PRIORITY.MEDIUM}>Medium</option>
                    <option value={TICKET_PRIORITY.HIGH}>High</option>
                    <option value={TICKET_PRIORITY.CRITICAL}>Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <select
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    <option value={TICKET_CATEGORY.USER_ERROR}>User Error</option>
                    <option value={TICKET_CATEGORY.SYSTEM_ISSUE}>System Issue</option>
                    <option value={TICKET_CATEGORY.FEATURE_REQUEST}>Feature Request</option>
                    <option value={TICKET_CATEGORY.OTHER}>Other</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="user_email">Email *</label>
                <input
                  id="user_email"
                  type="email"
                  value={formData.user_email}
                  onChange={(e) => setFormData({...formData, user_email: e.target.value})}
                  required
                  placeholder="user@example.com"
                  readOnly
                />
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="btn-submit">
                  {creating ? 'Creating...' : 'Create Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Ticket #{editingTicket?.id}</h2>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleUpdateTicket} className="ticket-form">
              <div className="form-group">
                <label htmlFor="edit-title">Title *</label>
                <input
                  id="edit-title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  placeholder="Brief description of the issue"
                />
              </div>
              <div className="form-group">
                <label htmlFor="edit-description">Description *</label>
                <textarea
                  id="edit-description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  placeholder="Detailed description of the issue"
                  rows="5"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-priority">Priority</label>
                  <select
                    id="edit-priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                  >
                    <option value={TICKET_PRIORITY.LOW}>Low</option>
                    <option value={TICKET_PRIORITY.MEDIUM}>Medium</option>
                    <option value={TICKET_PRIORITY.HIGH}>High</option>
                    <option value={TICKET_PRIORITY.CRITICAL}>Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="edit-status">Status</label>
                  <select
                    id="edit-status"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <option value={TICKET_STATUS.OPEN}>Open</option>
                    <option value={TICKET_STATUS.IN_PROGRESS}>In Progress</option>
                    <option value={TICKET_STATUS.ASSIGNED_TO_HUMAN}>Assigned to Human</option>
                    <option value={TICKET_STATUS.RESOLVED}>Resolved</option>
                    <option value={TICKET_STATUS.CLOSED}>Closed</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-category">Category</label>
                  <select
                    id="edit-category"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    <option value={TICKET_CATEGORY.USER_ERROR}>User Error</option>
                    <option value={TICKET_CATEGORY.SYSTEM_ISSUE}>System Issue</option>
                    <option value={TICKET_CATEGORY.FEATURE_REQUEST}>Feature Request</option>
                    <option value={TICKET_CATEGORY.OTHER}>Other</option>
                  </select>
                </div>
                <div className="form-group"></div>
              </div>
              <div className="form-group">
                <label htmlFor="edit-user_email">Email *</label>
                <input
                  id="edit-user_email"
                  type="email"
                  value={formData.user_email}
                  onChange={(e) => setFormData({...formData, user_email: e.target.value})}
                  required
                  placeholder="user@example.com"
                  readOnly
                />
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowEditModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" disabled={updating} className="btn-submit">
                  {updating ? 'Updating...' : 'Update Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default TicketList
