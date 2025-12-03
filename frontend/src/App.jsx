import { useState, useEffect, useRef } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { fetchBackendStatus, sendChatMessage, resetChatConversation } from './api'
import TicketList from './components/TicketList'
import Login from './components/Login'
import Register from './components/Register'
import './App.css'

function ChatPage({ user, onLogout }) {
  const [backendStatus, setBackendStatus] = useState(null)
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: `👋 Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentTicket, setCurrentTicket] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Check backend status
    fetchBackendStatus()
      .then(data => setBackendStatus(data))
      .catch(err => console.error('Backend status check failed:', err))
    
    // Reset conversation on the backend when chat page loads
    // This ensures a fresh start when user refreshes or navigates to chat
    if (user?.email) {
      resetChatConversation(user.email)
        .then(() => console.log('Conversation reset for fresh start'))
        .catch(err => console.warn('Could not reset conversation:', err))
    }
  }, [user?.email])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage(messages.concat(userMessage), user.email, currentTicket)
      
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        ticketId: response.ticket_id,
        action: response.action,
        priorityInfo: response.priority_info,
        needsClarification: response.needs_clarification
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update ticket ID if created
      if (response.ticket_id && !currentTicket) {
        setCurrentTicket(response.ticket_id)
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ Error: ${error.message}. Please check if the backend is running.`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <div className="app-icon">🤖</div>
          <div className="header-text">
            <h1>Auto-Ops-AI</h1>
            <p className="tagline">AI-powered IT Support Assistant</p>
          </div>
        </div>
        <div className="header-status">
          <span className="user-badge">
            👤 {user.name} ({user.tier})
          </span>
          <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            {backendStatus ? 'Online' : 'Offline'}
          </span>
          <button onClick={onLogout} className="logout-btn">
            🚪 Logout
          </button>
        </div>
      </header>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="message-bubble">
                <div className="message-header">
                  <span className="message-sender">
                    {msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                  </span>
                  <span className="message-time">
                    {formatTimestamp(msg.timestamp)}
                  </span>
                </div>
                <div className="message-text">
                  {msg.content}
                </div>
                {msg.ticketId && (
                  <div className="message-badges">
                    <span className="badge ticket-badge">
                      📋 Ticket #{msg.ticketId}
                    </span>
                    {msg.action && (
                      <span className={`badge action-badge ${msg.action}`}>
                        {msg.action === 'escalated' ? '⚠️ Escalated' :
                         msg.action === 'troubleshooting' ? '🔧 Troubleshooting' :
                         msg.action === 'clarifying' ? '❓ Clarifying' : msg.action}
                      </span>
                    )}
                    {msg.priorityInfo && (
                      <span className={`badge priority-badge ${msg.priorityInfo.priority_label?.toLowerCase()}`}>
                        ⚡ {msg.priorityInfo.priority_label}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message-wrapper assistant">
              <div className="message-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <div className="input-section">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe your IT issue... (e.g., 'My laptop is slow')"
              className="message-input"
              rows={2}
              disabled={loading}
            />
            <button 
              onClick={handleSend} 
              disabled={loading || !input.trim()}
              className="send-btn"
            >
              📤 Send
            </button>
          </div>
          <div className="input-hint">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>

      <footer className="app-footer">
        <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer" className="footer-link">
          📚 API Docs
        </a>
        <Link to="/tickets" className="footer-link">
          🎫 View Tickets
        </Link>
      </footer>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />} />
        <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
        <Route path="/" element={user ? <ChatPage user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/tickets" element={user ? <TicketList /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App
