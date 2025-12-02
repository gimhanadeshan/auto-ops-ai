import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, RefreshCw, AlertCircle, Zap, CheckCircle, Clock, XCircle, Loader } from 'lucide-react'
import './TicketList.css'

function TicketList() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:8000/api/v1/tickets')
      if (!response.ok) throw new Error('Failed to fetch tickets')
      const data = await response.json()
      setTickets(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityClass = (priority) => {
    const priorityMap = {
      1: 'critical',
      2: 'high', 
      3: 'medium',
      4: 'low'
    }
    return priorityMap[priority] || 'medium'
  }

  const getPriorityLabel = (priority) => {
    const labels = {
      1: 'Critical',
      2: 'High',
      3: 'Medium', 
      4: 'Low'
    }
    return labels[priority] || 'Medium'
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      'open': { label: 'Open', class: 'status-open' },
      'in_progress': { label: 'In Progress', class: 'status-progress' },
      'resolved': { label: 'Resolved', class: 'status-resolved' },
      'closed': { label: 'Closed', class: 'status-closed' }
    }
    return statusMap[status] || { label: status, class: 'status-open' }
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

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'all') return true
    if (filter === 'open') return ticket.status === 'open'
    if (filter === 'critical') return ticket.priority === 1
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
          <Link to="/" className="back-btn">
            <ArrowLeft size={18} />
            <span>Back to Chat</span>
          </Link>
          <h1>Support Tickets</h1>
        </div>
        <button onClick={fetchTickets} className="refresh-btn">
          <RefreshCw size={18} />
          <span>Refresh</span>
        </button>
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
          className={`filter-tab ${filter === 'critical' ? 'active' : ''}`}
          onClick={() => setFilter('critical')}
        >
          Critical ({tickets.filter(t => t.priority === 1).length})
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
                  {ticket.category && (
                    <span className="ticket-category">
                      {ticket.category}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default TicketList
