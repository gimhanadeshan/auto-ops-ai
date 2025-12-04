import { useState, useEffect, useRef } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { fetchBackendStatus, sendChatMessage, resetChatConversation } from './api'
import { Bot, User, Send, FileText, AlertCircle, Zap, Wrench, HelpCircle, Mic, MicOff } from 'lucide-react'
import { STORAGE_KEYS } from './config/constants'
import { voiceService } from './services/voiceService'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import TicketList from './components/TicketList'
import SystemMonitoring from './components/SystemMonitoring'
import Reports from './components/Reports'
import Settings from './components/Settings'
import AutomationPage from './components/AutomationPage'
import ErrorCodesPage from './components/ErrorCodesPage'
import QuickActionsPage from './components/QuickActionsPage'
import KnowledgeBasePage from './components/KnowledgeBasePage'
import Login from './components/Login'
import Register from './components/Register'
import './styles/App.css'

function ChatPage({ user }) {
  const [backendStatus, setBackendStatus] = useState(null)
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentTicket, setCurrentTicket] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const messagesEndRef = useRef(null)
  const interimTranscriptRef = useRef('')

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    fetchBackendStatus()
      .then(data => setBackendStatus(data))
      .catch(err => console.error('Backend status check failed:', err))
    
    // Don't auto-reset conversation - allow continuing previous chats
    // User can start new chat via "New Chat" button if needed

    // Initialize voice service
    setVoiceSupported(voiceService.checkSupport())
    
    // Set up voice recognition callbacks
    voiceService.onResult((result) => {
      if (result.final) {
        // Final transcript - set it in input field
        setInput(result.final)
        setInterimTranscript('')
        interimTranscriptRef.current = ''
        setIsListening(false)
      } else {
        // Interim transcript - show it temporarily
        setInterimTranscript(result.interim)
        interimTranscriptRef.current = result.interim
      }
    })

    voiceService.onError((error) => {
      setIsListening(false)
      setInterimTranscript('')
      interimTranscriptRef.current = ''
      // Show error message to user
      const errorMessage = {
        role: 'assistant',
        content: `Voice input error: ${error}`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    })

    voiceService.onStart(() => {
      setIsListening(true)
      setInterimTranscript('Listening...')
      interimTranscriptRef.current = 'Listening...'
    })

    voiceService.onEnd(() => {
      setIsListening(false)
      const currentInterim = interimTranscriptRef.current
      if (currentInterim && !currentInterim.includes('Listening')) {
        // Keep the interim transcript if it's actual speech
        setInput(prev => prev + (prev ? ' ' : '') + currentInterim)
      }
      setInterimTranscript('')
      interimTranscriptRef.current = ''
    })

    // Cleanup on unmount
    return () => {
      if (voiceService.getListeningState()) {
        voiceService.stopListening()
      }
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
      
      if (response.ticket_id && !currentTicket) {
        setCurrentTicket(response.ticket_id)
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}. Please check if the backend is running.`,
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

  const handleVoiceToggle = () => {
    if (isListening) {
      voiceService.stopListening()
    } else {
      try {
        voiceService.startListening()
      } catch (error) {
        console.error('Error starting voice input:', error)
        const errorMessage = {
          role: 'assistant',
          content: `Unable to start voice input: ${error.message}. Please check your microphone permissions.`,
          timestamp: new Date().toISOString(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    }
  }

  const handleNewChat = () => {
    // Reset to new chat
    setMessages([
      { 
        role: 'assistant', 
        content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
        timestamp: new Date().toISOString()
      }
    ])
    setCurrentTicket(null)
    
    // Reset backend conversation
    if (user?.email) {
      resetChatConversation(user.email)
        .catch(err => console.warn('Could not reset conversation:', err))
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-header-left">
          <Bot size={28} />
          <div>
            <h2>AI Support Chat</h2>
            <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
              <span className="status-dot"></span>
              {backendStatus ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="chat-header-right">
          <button
            onClick={handleNewChat}
            className="new-chat-btn"
            title="Start new chat"
          >
            New Chat
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-sender">
                  {msg.role === 'user' ? (
                    <><User size={14} /> You</>
                  ) : (
                    <><Bot size={14} /> AI Assistant</>
                  )}
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
                    <FileText size={12} /> Ticket #{msg.ticketId}
                  </span>
                  {msg.action && (
                    <span className={`badge action-badge ${msg.action}`}>
                      {msg.action === 'escalated' ? <><AlertCircle size={12} /> Escalated</> :
                       msg.action === 'troubleshooting' ? <><Wrench size={12} /> Troubleshooting</> :
                       msg.action === 'clarifying' ? <><HelpCircle size={12} /> Clarifying</> : msg.action}
                    </span>
                  )}
                  {msg.priorityInfo && (
                    <span className={`badge priority-badge ${msg.priorityInfo.priority_label?.toLowerCase()}`}>
                      <Zap size={12} /> {msg.priorityInfo.priority_label}
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
        {isListening && (
          <div className="voice-listening-indicator">
            <div className="voice-pulse"></div>
            <span>{interimTranscript || 'Listening... Speak now'}</span>
          </div>
        )}
        <div className="input-section">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isListening ? "Listening..." : "Describe your IT issue... (e.g., 'My laptop is slow')"}
            className="message-input"
            rows={2}
            disabled={loading || isListening}
          />
          {voiceSupported && (
            <button
              onClick={handleVoiceToggle}
              disabled={loading}
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}
          <button 
            onClick={handleSend} 
            disabled={loading || !input.trim() || isListening}
            className="send-btn"
          >
            <Send size={18} />
            <span>Send</span>
          </button>
        </div>
        <div className="input-hint">
          {voiceSupported ? (
            <>
              Press Enter to send, Shift+Enter for new line • Click <Mic size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> to use voice input
            </>
          ) : (
            'Press Enter to send, Shift+Enter for new line'
          )}
        </div>
      </div>
    </div>
  )
}

function MainLayout({ user, onLogout }) {
  return (
    <div className="main-layout">
      <Sidebar user={user} onLogout={onLogout} />
      <div className="main-content">
        <Routes>
          <Route path="/dashboard" element={<Dashboard user={user} />} />
          <Route path="/quick-actions" element={<QuickActionsPage />} />
          <Route path="/chat" element={<ChatPage user={user} />} />
          <Route path="/tickets" element={<TicketList />} />
          <Route path="/monitoring" element={<SystemMonitoring />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/automation" element={<AutomationPage />} />
          <Route path="/error-codes" element={<ErrorCodesPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="/settings" element={<Settings user={user} />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA)
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Failed to parse stored user data:', error)
        localStorage.removeItem(STORAGE_KEYS.USER_DATA)
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      }
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_DATA)
    setUser(null)
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'var(--color-bg-primary)',
        color: 'var(--color-text-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <Router>
      {!user ? (
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      ) : (
        <MainLayout user={user} onLogout={handleLogout} />
      )}
    </Router>
  )
}

export default App
