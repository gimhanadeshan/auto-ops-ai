import { useState, useEffect, useRef } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom'
import { fetchBackendStatus, sendChatMessage, resetChatConversation, sendChatMessageWithImage } from './api'
import { Bot, User, Send, FileText, AlertCircle, Zap, Wrench, HelpCircle, Mic, MicOff, Image, X } from 'lucide-react'
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
import UserManagement from './components/UserManagement'
import AuditLogs from './components/AuditLogs'
import Login from './components/Login'
import Register from './components/Register'
import './styles/App.css'

function ChatPage({ user }) {
  const location = useLocation()  // Track navigation to detect when coming from tickets
  const [backendStatus, setBackendStatus] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentTicket, setCurrentTicket] = useState(null)
  const [currentSessionId, setCurrentSessionId] = useState(null)  // Track session ID
  const [isListening, setIsListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [initKey, setInitKey] = useState(0)  // Force re-initialization
  const messagesEndRef = useRef(null)
  const interimTranscriptRef = useRef('')
  const fileInputRef = useRef(null)

  // Storage keys for chat persistence
  const CHAT_STORAGE_KEY = `auto_ops_chat_${user?.email || 'guest'}`
  const SESSION_STORAGE_KEY = `auto_ops_session_${user?.email || 'guest'}`
  const TICKET_STORAGE_KEY = `auto_ops_ticket_${user?.email || 'guest'}`
  const RESUME_TICKET_KEY = `auto_ops_resume_ticket_${user?.email || 'guest'}`

  // Initialize messages from localStorage (resume context is handled in separate useEffect)
  useEffect(() => {
    // Skip if we have a resume context - let the other useEffect handle it
    const resumeContext = localStorage.getItem(RESUME_TICKET_KEY)
    if (resumeContext) {
      return  // Will be handled by the navigation useEffect
    }

    // Normal initialization - check for saved messages
    const savedMessages = localStorage.getItem(CHAT_STORAGE_KEY)
    const savedSession = localStorage.getItem(SESSION_STORAGE_KEY)
    const savedTicket = localStorage.getItem(TICKET_STORAGE_KEY)

    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        if (parsed && parsed.length > 0) {
          setMessages(parsed)
          if (savedSession) setCurrentSessionId(savedSession)
          if (savedTicket) setCurrentTicket(parseInt(savedTicket))
          return
        }
      } catch (e) {
        console.warn('Failed to parse saved messages:', e)
      }
    }

    // Default welcome message if no saved messages
    setMessages([
      { 
        role: 'assistant', 
        content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
        timestamp: new Date().toISOString()
      }
    ])
  }, [user?.email, location.key])  // Re-run when navigating to chat page

  // Check for resume context on every render (in case navigation doesn't trigger useEffect)
  useEffect(() => {
    const resumeContext = localStorage.getItem(RESUME_TICKET_KEY)
    if (resumeContext) {
      // We have a resume context - process it immediately
      try {
        const context = JSON.parse(resumeContext)
        // Clear the resume context immediately
        localStorage.removeItem(RESUME_TICKET_KEY)
        
        // Clear old saved chat
        localStorage.removeItem(CHAT_STORAGE_KEY)
        localStorage.removeItem(SESSION_STORAGE_KEY)
        localStorage.removeItem(TICKET_STORAGE_KEY)
        
        // Reset backend conversation to prevent cross-ticket contamination
        if (user?.email) {
          resetChatConversation(user.email).catch(err => {
            console.warn('Failed to reset backend conversation:', err)
          })
        }
        
        // Set ticket context
        setCurrentTicket(context.ticketId)
        setCurrentSessionId(null)
        
        if (context.resumeChat && context.existingMessages?.length > 0) {
          // Resume existing chat - load the previous messages
          const formattedMessages = context.existingMessages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.created_at || new Date().toISOString(),
            ticketId: context.ticketId
          }))
          
          // Add continuation message
          formattedMessages.push({
            role: 'assistant',
            content: `Continuing conversation for Ticket #${context.ticketId}: "${context.ticketTitle}"\n\nHow can I help you further with this issue?`,
            timestamp: new Date().toISOString(),
            ticketId: context.ticketId
          })
          
          setMessages(formattedMessages)
          localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(formattedMessages))
          localStorage.setItem(TICKET_STORAGE_KEY, context.ticketId.toString())
        } else if (context.isManualTicket) {
          // Manual ticket - start fresh
          const welcomeMessage = {
            role: 'assistant',
            content: `Hi! I'm here to help with Ticket #${context.ticketId}: "${context.ticketTitle}"\n\n**Issue Description:**\n${context.ticketDescription}\n\n**Priority:** ${context.ticketPriority}\n\nLet me help you troubleshoot this issue. Could you provide more details about when this problem started or any error messages you've seen?`,
            timestamp: new Date().toISOString(),
            ticketId: context.ticketId
          }
          setMessages([welcomeMessage])
          localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify([welcomeMessage]))
          localStorage.setItem(TICKET_STORAGE_KEY, context.ticketId.toString())
        }
      } catch (e) {
        console.warn('Failed to parse resume context:', e)
        localStorage.removeItem(RESUME_TICKET_KEY)
      }
    }
  }, [location])  // Run on every navigation

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      // Don't save image previews to avoid localStorage quota issues
      const messagesToSave = messages.map(msg => ({
        ...msg,
        imagePreview: msg.imagePreview ? '[image attached]' : undefined
      }))
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messagesToSave))
    }
  }, [messages])

  // Save session and ticket to localStorage
  useEffect(() => {
    if (currentSessionId) {
      localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId)
    }
  }, [currentSessionId])

  useEffect(() => {
    if (currentTicket) {
      localStorage.setItem(TICKET_STORAGE_KEY, currentTicket.toString())
    }
  }, [currentTicket])

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
      const response = await sendChatMessage(messages.concat(userMessage), user.email, currentTicket, currentSessionId)
      
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
      
      // Track session and ticket from response
      if (response.session_id && !currentSessionId) {
        setCurrentSessionId(response.session_id)
      }
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
      handleSendAll()
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
    const welcomeMessage = { 
      role: 'assistant', 
      content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    }
    setMessages([welcomeMessage])
    setCurrentTicket(null)
    setCurrentSessionId(null)  // Reset session ID for new chat
    clearSelectedImage()
    
    // Clear localStorage for fresh start
    localStorage.removeItem(CHAT_STORAGE_KEY)
    localStorage.removeItem(SESSION_STORAGE_KEY)
    localStorage.removeItem(TICKET_STORAGE_KEY)
    localStorage.removeItem(RESUME_TICKET_KEY)
    
    // Reset backend conversation and get new session ID
    if (user?.email) {
      resetChatConversation(user.email)
        .then(response => {
          if (response?.session_id) {
            setCurrentSessionId(response.session_id)
          }
        })
        .catch(err => console.warn('Could not reset conversation:', err))
    }
  }

  // Image upload handlers
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
    if (!validTypes.includes(file.type)) {
      const errorMessage = {
        role: 'assistant',
        content: 'Please select a valid image file (PNG, JPG, JPEG, WEBP, or GIF).',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    // Validate file size (max 10MB before compression)
    if (file.size > 10 * 1024 * 1024) {
      const errorMessage = {
        role: 'assistant',
        content: 'Image is too large. Please select an image under 10MB.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    setSelectedImage(file)
    
    // Create preview URL
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const clearSelectedImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSendWithImage = async () => {
    if (!selectedImage || loading) return

    const userMessage = {
      role: 'user',
      content: input.trim() || 'Please analyze this image and help me troubleshoot the issue.',
      timestamp: new Date().toISOString(),
      imagePreview: imagePreview // Store preview for display
    }

    setMessages(prev => [...prev, userMessage])
    const messageText = input.trim()
    setInput('')
    clearSelectedImage()
    setLoading(true)

    try {
      const response = await sendChatMessageWithImage(
        selectedImage,
        messageText,
        user.email,
        currentTicket,
        currentSessionId
      )
      
      // Build response content with image analysis
      let responseContent = response.message
      if (response.image_analysis) {
        const analysis = response.image_analysis
        responseContent = `**📸 Image Analysis Results:**\n\n`
        responseContent += `**Problem Identified:** ${analysis.issue_description || 'Analysis in progress...'}\n\n`
        if (analysis.extracted_text) {
          responseContent += `**Text/Error Found:** ${analysis.extracted_text}\n\n`
        }
        responseContent += `---\n\n${response.message}`
      }

      const assistantMessage = {
        role: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
        ticketId: response.ticket_id,
        action: response.action,
        priorityInfo: response.priority_info,
        imageAnalysis: response.image_analysis
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Track session and ticket
      if (response.session_id && !currentSessionId) {
        setCurrentSessionId(response.session_id)
      }
      if (response.ticket_id && !currentTicket) {
        setCurrentTicket(response.ticket_id)
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error analyzing image: ${error.message}. Please check if the backend is running.`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // Modified handleSend to also handle image uploads
  const handleSendAll = async () => {
    if (selectedImage) {
      await handleSendWithImage()
    } else {
      await handleSend()
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
            <div className="chat-status-row">
              <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
                <span className="status-dot"></span>
                {backendStatus ? 'Online' : 'Offline'}
              </span>
              {currentTicket && (
                <span className="active-ticket-indicator">
                  <FileText size={12} />
                  Ticket #{currentTicket}
                </span>
              )}
            </div>
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
                {msg.imagePreview && (
                  <div className="message-image-preview">
                    <img src={msg.imagePreview} alt="Uploaded" />
                  </div>
                )}
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
        {imagePreview && (
          <div className="image-preview-container">
            <img src={imagePreview} alt="Selected" className="image-preview" />
            <button 
              onClick={clearSelectedImage} 
              className="clear-image-btn"
              title="Remove image"
            >
              <X size={16} />
            </button>
            <span className="image-preview-label">Image attached</span>
          </div>
        )}
        <div className="input-section">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageSelect}
            accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || isListening}
            className={`image-upload-btn ${selectedImage ? 'has-image' : ''}`}
            title="Upload image (screenshot, error message, device photo)"
          >
            <Image size={20} />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={selectedImage ? "Describe the issue shown in the image (optional)..." : isListening ? "Listening..." : "Describe your IT issue... (e.g., 'My laptop is slow')"}
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
            onClick={handleSendAll} 
            disabled={loading || (!input.trim() && !selectedImage) || isListening}
            className="send-btn"
          >
            <Send size={18} />
            <span>Send</span>
          </button>
        </div>
        <div className="input-hint">
          {voiceSupported ? (
            <>
              Press Enter to send, Shift+Enter for new line • Click <Mic size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> for voice • Click <Image size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> to upload image
            </>
          ) : (
            <>
              Press Enter to send, Shift+Enter for new line • Click <Image size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> to upload image
            </>
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
          <Route path="/users" element={<UserManagement />} />
          <Route path="/audit-logs" element={<AuditLogs user={user} />} />
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
