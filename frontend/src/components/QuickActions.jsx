import { useState, useEffect, useMemo } from 'react'
import {
  Activity,
  HardDrive,
  Wifi,
  RefreshCw,
  Trash2,
  Terminal,
  CheckCircle,
  AlertCircle,
  X,
  Copy,
  Info,
  Search,
  Clock,
  Globe,
  Shield,
  MapPin,
  Monitor,
  List,
  Users,
  Folder,
  Server,
  Cpu,
  Play,
  Settings,
  FileText,
  Star,
  XCircle,
  Download
} from 'lucide-react'
import { monitoringService } from '../services/monitoringService'
import { staticDataService } from '../services/staticDataService'
import '../styles/components/QuickActions.css'

const STORAGE_KEY_RECENTLY_USED = 'quickActions_recentlyUsed'

// Icon mapping from string names to React components
const iconMap = {
  Activity, HardDrive, Wifi, RefreshCw, Trash2, Terminal,
  CheckCircle, AlertCircle, X, Copy, Info, Search, Clock,
  Globe, Shield, MapPin, Monitor, List, Users, Folder,
  Server, Cpu, Play, Settings, FileText, Star, XCircle
}

// Detect user's operating system
const detectOS = () => {
  const userAgent = window.navigator.userAgent.toLowerCase()
  const platform = window.navigator.platform.toLowerCase()
  
  if (platform.includes('win') || userAgent.includes('windows')) {
    return 'windows'
  } else if (platform.includes('mac') || userAgent.includes('macintosh') || userAgent.includes('mac os x')) {
    return 'mac'
  } else if (platform.includes('linux') || userAgent.includes('linux')) {
    return 'linux'
  }
  return 'unknown'
}

// Get command for current OS
const getCommandForOS = (commands, os) => {
  if (!commands || typeof commands !== 'object') return null
  
  // Try to get command for detected OS first
  const cmd = commands[os] || commands[os.charAt(0).toUpperCase() + os.slice(1)]
  if (cmd) return cmd
  
  // Fallback to any available command
  return Object.values(commands)[0] || null
}

function QuickActions({ hideHeader = false }) {
  const [loading, setLoading] = useState(null)
  const [result, setResult] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [modalContent, setModalContent] = useState(null)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [pendingAction, setPendingAction] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [recentlyUsed, setRecentlyUsed] = useState([])
  const [actionsData, setActionsData] = useState(null)
  const [loadingData, setLoadingData] = useState(true)

  // Load actions data from backend
  useEffect(() => {
    const loadActionsData = async () => {
      try {
        setLoadingData(true)
        console.log('Loading quick actions from backend...')
        const data = await staticDataService.getQuickActions()
        console.log('Quick actions data loaded:', data)
        if (data && data.actions && Array.isArray(data.actions)) {
          setActionsData(data)
          console.log(`Loaded ${data.actions.length} actions`)
        } else {
          console.error('Invalid data structure:', data)
          setActionsData(null)
        }
      } catch (error) {
        console.error('Failed to load quick actions data:', error)
        console.error('Error details:', error.message, error.stack)
        setActionsData(null)
      } finally {
        setLoadingData(false)
      }
    }
    loadActionsData()
  }, [])

  // Load recently used actions from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY_RECENTLY_USED)
    if (stored) {
      try {
        setRecentlyUsed(JSON.parse(stored))
      } catch (e) {
        console.error('Failed to load recently used actions:', e)
      }
    }
  }, [])

  // Save to recently used when action is executed
  const trackAction = (actionId) => {
    const updated = [actionId, ...recentlyUsed.filter(id => id !== actionId)].slice(0, 5)
    setRecentlyUsed(updated)
    localStorage.setItem(STORAGE_KEY_RECENTLY_USED, JSON.stringify(updated))
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      showResult('success', 'Copied to clipboard!')
    } catch (err) {
      showResult('error', 'Failed to copy')
    }
  }

  // Download a script file that opens terminal and runs command
  const downloadTerminalScript = (command, platform) => {
    let scriptContent = ''
    let filename = ''
    let mimeType = ''

    if (platform === 'windows') {
      // Create a batch file
      filename = 'run-command.bat'
      mimeType = 'application/x-bat'
      scriptContent = `@echo off\nchcp 65001 > nul\ncmd /k "${command}"\npause\n`
    } else if (platform === 'mac') {
      // Create a shell script
      filename = 'run-command.sh'
      mimeType = 'text/plain'
      scriptContent = `#!/bin/bash\n${command}\nread -p "Press Enter to close..."\n`
    } else if (platform === 'linux') {
      // Create a shell script
      filename = 'run-command.sh'
      mimeType = 'text/plain'
      scriptContent = `#!/bin/bash\n${command}\nread -p "Press Enter to close..."\n`
    } else {
      showResult('error', 'Unable to create script for your operating system')
      return
    }

    // Create blob and download
    const blob = new Blob([scriptContent], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    showResult('success', `Downloaded ${filename}. Double-click to run in terminal.`)
  }

  // Attempt to open terminal with command (works in limited scenarios)
  const openTerminalWithCommand = async (command, platform) => {
    const detectedOS = detectOS()
    const os = platform || detectedOS
    const cmd = command

    try {
      if (os === 'windows') {
        // For Windows, try to use PowerShell or CMD
        // Create a temporary batch file and execute it
        const batchContent = `@echo off\nchcp 65001 > nul\n${cmd}\npause\n`
        const blob = new Blob([batchContent], { type: 'application/x-bat' })
        const url = URL.createObjectURL(blob)
        
        // Try to open with Windows shell
        // Note: This may not work in all browsers due to security restrictions
        const link = document.createElement('a')
        link.href = url
        link.download = 'run-command.bat'
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        showResult('success', 'Downloaded batch file. Double-click to run in terminal, or use PowerShell/CMD.')
      } else if (os === 'mac') {
        // For Mac, use AppleScript via data URI (limited support)
        // Better approach: download script file
        downloadTerminalScript(cmd, 'mac')
      } else if (os === 'linux') {
        // For Linux, download shell script
        downloadTerminalScript(cmd, 'linux')
      } else {
        // Fallback: download script
        downloadTerminalScript(cmd, detectedOS)
      }
    } catch (error) {
      console.error('Failed to open terminal:', error)
      // Fallback to downloading script
      downloadTerminalScript(cmd, os)
    }
  }

  const showResult = (type, message) => {
    setResult({ type, message })
    setTimeout(() => setResult(null), 3000)
  }

  const showInstructions = (title, content, command = null) => {
    setModalContent({ title, content, command })
    setShowModal(true)
  }

  const confirmAction = (actionId, actionHandler) => {
    setPendingAction({ id: actionId, handler: actionHandler })
    setShowConfirmation(true)
  }

  const executePendingAction = async () => {
    if (pendingAction && pendingAction.handler) {
      setShowConfirmation(false)
      await pendingAction.handler()
      setPendingAction(null)
    }
  }

  const cancelAction = () => {
    setShowConfirmation(false)
    setPendingAction(null)
  }

  // Wrap action handlers to track usage
  const wrapAction = (actionId, handler, requiresConfirmation = false) => {
    if (requiresConfirmation) {
      return () => confirmAction(actionId, () => {
        trackAction(actionId)
        handler()
      })
    }
    return () => {
      trackAction(actionId)
      handler()
    }
  }

  // Handler functions
  const handleSystemCheck = async () => {
    setLoading('system-check')
    try {
      const response = await monitoringService.checkSystemHealth()
      if (response && response.issues_detected > 0) {
        showResult('warning', `Found ${response.issues_detected} system issue${response.issues_detected > 1 ? 's' : ''}. Check monitoring page for details.`)
      } else {
        showResult('success', 'System check completed. All systems healthy!')
      }
    } catch (error) {
      console.error('System check error:', error)
      showResult('error', error.message || 'Failed to run system check. Please try again.')
    } finally {
      setLoading(null)
    }
  }

  // Build handlers dynamically from backend data
  const buildHandlers = () => {
    if (!actionsData) return {}
    
    const handlersObj = {}
    
    actionsData.actions.forEach(action => {
      if (action.type === 'api' && action.id === 'system-check') {
        handlersObj[action.id] = () => confirmAction('system-check', handleSystemCheck)
      } else if (action.type === 'instructions' && action.instructions) {
        handlersObj[action.id] = () => {
          const inst = action.instructions
          showInstructions(inst.title, inst.description, inst.commands)
        }
      }
    })
    
    return handlersObj
  }

  // Define all action handlers - built dynamically from backend data
  const handlers = useMemo(() => buildHandlers(), [actionsData])

  // Process actions data from backend
  const allActions = useMemo(() => {
    if (!actionsData || !actionsData.actions) {
      console.log('No actionsData or actionsData.actions:', actionsData)
      return []
    }
    
    const processed = actionsData.actions.map(action => ({
      ...action,
      icon: iconMap[action.icon] || Activity, // Fallback to Activity if icon not found
      requiresConfirmation: action.requiresConfirmation || false
    }))
    
    console.log('Processed actions:', processed.length, processed)
    return processed
  }, [actionsData])

  // Category labels and icons from backend
  const categories = useMemo(() => {
    if (!actionsData || !actionsData.categories) {
      return {
        network: { label: 'Network & Connectivity', icon: Wifi },
        system: { label: 'System Diagnostics', icon: Monitor },
        security: { label: 'Security & Permissions', icon: Shield },
        storage: { label: 'Storage Management', icon: HardDrive },
        performance: { label: 'Performance Tools', icon: Cpu }
      }
    }
    
    const cats = {}
    Object.entries(actionsData.categories).forEach(([key, value]) => {
      cats[key] = {
        label: value.label,
        icon: iconMap[value.icon] || Monitor
      }
    })
    return cats
  }, [actionsData])

  // Filter actions based on search query
  const filteredActions = useMemo(() => {
    if (!searchQuery.trim()) return allActions
    const query = searchQuery.toLowerCase()
    return allActions.filter(action => 
      action.label.toLowerCase().includes(query) ||
      action.description.toLowerCase().includes(query) ||
      action.category.toLowerCase().includes(query)
    )
  }, [searchQuery, allActions])

  // Group actions by category
  const actionsByCategory = useMemo(() => {
    const grouped = {}
    filteredActions.forEach(action => {
      if (!grouped[action.category]) {
        grouped[action.category] = []
      }
      grouped[action.category].push(action)
    })
    return grouped
  }, [filteredActions])

  // Get recently used actions (limit to 5)
  const recentActions = useMemo(() => {
    if (!allActions || allActions.length === 0) return []
    return recentlyUsed
      .map(id => allActions.find(a => a.id === id))
      .filter(Boolean)
      .slice(0, 5)
  }, [recentlyUsed, allActions])

  // Execute action with tracking
  const executeAction = (action) => {
    const handler = handlers[action.id]
    if (handler) {
      if (action.requiresConfirmation) {
        confirmAction(action.id, async () => {
          trackAction(action.id)
          await handler()
        })
      } else {
        trackAction(action.id)
        handler()
      }
    }
  }

  // Show loading state while fetching data
  if (loadingData) {
    return (
      <div className="quick-actions-widget">
        <div className="widget-header">
          <div>
            <h2>Quick Actions</h2>
            <p>Loading actions...</p>
          </div>
        </div>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spinning" />
        </div>
      </div>
    )
  }

  // Show error state if data failed to load or is invalid
  if (!actionsData || !actionsData.actions || !Array.isArray(actionsData.actions) || actionsData.actions.length === 0) {
    return (
      <div className="quick-actions-widget">
        {!hideHeader && (
          <div className="widget-header">
            <div>
              <h2>Quick Actions</h2>
              <p>Common troubleshooting actions</p>
            </div>
          </div>
        )}
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <AlertCircle size={48} style={{ marginBottom: '16px', color: 'var(--color-danger)' }} />
          <h3>No Actions Available</h3>
          <p>
            {!actionsData 
              ? 'Failed to load quick actions data from the server. Please check your connection and try again.'
              : 'Quick actions data is empty or invalid.'}
          </p>
          {actionsData && (
            <p style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
              Debug: actionsData exists but actions array is {!actionsData.actions ? 'missing' : `empty (length: ${actionsData.actions?.length})`}
            </p>
          )}
          <button 
            onClick={() => {
              setLoadingData(true)
              staticDataService.getQuickActions()
                .then(data => {
                  console.log('Retry loaded data:', data)
                  if (data && data.actions && Array.isArray(data.actions)) {
                    setActionsData(data)
                  } else {
                    console.error('Invalid data structure on retry:', data)
                    setActionsData(null)
                  }
                  setLoadingData(false)
                })
                .catch(error => {
                  console.error('Failed to load quick actions on retry:', error)
                  setActionsData(null)
                  setLoadingData(false)
                })
            }}
            style={{ marginTop: '16px', padding: '8px 16px' }}
          >
            <RefreshCw size={16} style={{ marginRight: '8px' }} />
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="quick-actions-widget">
      {!hideHeader && (
        <div className="widget-header">
          <div>
            <h2>Quick Actions</h2>
            <p>Common troubleshooting actions</p>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="quick-actions-search">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search actions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="search-clear-btn"
              title="Clear search"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {result && (
        <div className={`action-result ${result.type}`}>
          {result.type === 'success' && <CheckCircle size={16} />}
          {result.type === 'error' && <AlertCircle size={16} />}
          {result.type === 'warning' && <AlertCircle size={16} />}
          <span>{result.message}</span>
        </div>
      )}

      {/* Recently Used Section */}
      {recentActions.length > 0 && !searchQuery && (
        <div className="actions-section">
          <div className="section-header">
            <Clock size={20} />
            <h3>Recently Used</h3>
          </div>
          <div className="actions-grid">
            {recentActions.map((action) => {
              const Icon = action.icon
              const isLoading = loading === action.id
              
              return (
                <button
                  key={action.id}
                  onClick={() => executeAction(action)}
                  disabled={isLoading}
                  className={`action-button ${action.color} ${isLoading ? 'loading' : ''}`}
                  title={action.description}
                >
                  <div className="action-icon">
                    {isLoading ? (
                      <RefreshCw size={24} className="spinning" />
                    ) : (
                      <Icon size={24} />
                    )}
                  </div>
                  <span className="action-label">{action.label}</span>
                  <Star size={14} className="recent-indicator" />
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Categorized Sections */}
      {Object.entries(categories).map(([categoryKey, categoryInfo]) => {
        const categoryActions = actionsByCategory[categoryKey] || []
        if (categoryActions.length === 0) return null

        const CategoryIcon = categoryInfo.icon

        return (
          <div key={categoryKey} className="actions-section">
            <div className="section-header">
              <CategoryIcon size={20} />
              <h3>{categoryInfo.label}</h3>
              <span className="action-count">({categoryActions.length})</span>
            </div>
            <div className="actions-grid">
              {categoryActions.map((action) => {
                const Icon = action.icon
                const isLoading = loading === action.id
                
                return (
                  <button
                    key={action.id}
                    onClick={() => executeAction(action)}
                    disabled={isLoading}
                    className={`action-button ${action.color} ${isLoading ? 'loading' : ''}`}
                    title={action.description}
                  >
                    <div className="action-icon">
                      {isLoading ? (
                        <RefreshCw size={24} className="spinning" />
                      ) : (
                        <Icon size={24} />
                      )}
                    </div>
                    <span className="action-label">{action.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        )
      })}

      {/* No results message */}
      {searchQuery && Object.keys(actionsByCategory).length === 0 && (
        <div className="no-results">
          <Search size={48} />
          <p>No actions found matching "{searchQuery}"</p>
          <button onClick={() => setSearchQuery('')} className="clear-search-btn">
            Clear Search
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirmation && pendingAction && (
        <div className="modal-overlay" onClick={cancelAction}>
          <div className="confirmation-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="confirmation-header">
              <AlertCircle size={24} className="confirmation-icon" />
              <h3>Confirm Action</h3>
            </div>
            <div className="confirmation-body">
              <p>{allActions.find(a => a.id === pendingAction.id)?.confirmationMessage || 'Are you sure you want to proceed?'}</p>
            </div>
            <div className="confirmation-actions">
              <button className="confirm-btn-cancel" onClick={cancelAction}>
                Cancel
              </button>
              <button className="confirm-btn-ok" onClick={executePendingAction}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Instructions Modal */}
      {showModal && modalContent && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{modalContent.title}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-description">{modalContent.content}</p>
              {modalContent.command && (
                <div className="commands-list">
                  {Object.entries(modalContent.command).map(([platform, cmd]) => {
                    const detectedOS = detectOS()
                    const isCurrentOS = platform.toLowerCase() === detectedOS
                    
                    return (
                      <div key={platform} className={`command-item ${isCurrentOS ? 'current-os' : ''}`}>
                        <div className="command-header">
                          <div className="platform-info">
                            <span className="platform-label">
                              {platform.charAt(0).toUpperCase() + platform.slice(1)}
                              {isCurrentOS && <span className="os-badge">Your OS</span>}
                            </span>
                          </div>
                          <div className="command-actions">
                            <button
                              className="copy-command-btn"
                              onClick={() => copyToClipboard(cmd)}
                              title="Copy command to clipboard"
                            >
                              <Copy size={14} />
                              Copy
                            </button>
                            <button
                              className="open-terminal-btn"
                              onClick={() => openTerminalWithCommand(cmd, platform.toLowerCase())}
                              title="Open terminal with this command"
                            >
                              <Terminal size={14} />
                              Open Terminal
                            </button>
                            <button
                              className="download-script-btn"
                              onClick={() => downloadTerminalScript(cmd, platform.toLowerCase())}
                              title="Download script file to run later"
                            >
                              <Download size={14} />
                              Download
                            </button>
                          </div>
                        </div>
                        <code className="command-code">{cmd}</code>
                      </div>
                    )
                  })}
                </div>
              )}
              <div className="modal-info">
                <Info size={16} />
                <span>
                  <strong>Tips:</strong> Click "Copy" to copy the command, "Open Terminal" to download and run it, 
                  or "Download" to save a script file for later. Some commands may require administrator/sudo privileges.
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default QuickActions
