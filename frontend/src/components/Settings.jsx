import { useState } from 'react'
import { User, Bell, Shield, Moon, Sun, Database, Zap, Save } from 'lucide-react'
import '../styles/components/Settings.css'

function Settings({ user }) {
  const [darkMode, setDarkMode] = useState(true)
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    ticketUpdates: true,
    systemAlerts: true
  })
  const [aiSettings, setAiSettings] = useState({
    autoResolve: false,
    confidenceThreshold: 75,
    escalationDelay: 30
  })

  const handleSave = () => {
    alert('Settings saved successfully!')
  }

  return (
    <div className="settings-container">
      <div className="settings-header">
        <div>
          <h1>Settings</h1>
          <p>Customize your experience and system preferences</p>
        </div>
        <button onClick={handleSave} className="save-btn">
          <Save size={20} />
          <span>Save Changes</span>
        </button>
      </div>

      <div className="settings-content">
        {/* Profile Settings */}
        <div className="settings-section">
          <div className="section-title">
            <User size={22} />
            <h2>Profile Settings</h2>
          </div>
          <div className="settings-grid">
            <div className="setting-item">
              <label>Full Name</label>
              <input type="text" defaultValue={user?.name || ''} placeholder="Enter your name" />
            </div>
            <div className="setting-item">
              <label>Email</label>
              <input type="email" defaultValue={user?.email || ''} placeholder="your@email.com" />
            </div>
            <div className="setting-item">
              <label>Role</label>
              <input type="text" value={user?.tier || 'Standard'} disabled />
            </div>
            <div className="setting-item">
              <label>Department</label>
              <select defaultValue="it">
                <option value="it">IT Support</option>
                <option value="dev">Development</option>
                <option value="ops">Operations</option>
                <option value="admin">Administration</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="settings-section">
          <div className="section-title">
            <Bell size={22} />
            <h2>Notification Preferences</h2>
          </div>
          <div className="settings-list">
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">Email Notifications</span>
                <span className="toggle-desc">Receive updates via email</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notifications.email}
                  onChange={(e) => setNotifications({...notifications, email: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">Push Notifications</span>
                <span className="toggle-desc">Browser push notifications</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notifications.push}
                  onChange={(e) => setNotifications({...notifications, push: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">Ticket Updates</span>
                <span className="toggle-desc">Notify on ticket status changes</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notifications.ticketUpdates}
                  onChange={(e) => setNotifications({...notifications, ticketUpdates: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">System Alerts</span>
                <span className="toggle-desc">Critical system notifications</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={notifications.systemAlerts}
                  onChange={(e) => setNotifications({...notifications, systemAlerts: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        {/* AI Settings */}
        <div className="settings-section">
          <div className="section-title">
            <Zap size={22} />
            <h2>AI Assistant Settings</h2>
          </div>
          <div className="settings-list">
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">Auto-Resolve Tickets</span>
                <span className="toggle-desc">Allow AI to automatically resolve simple issues</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={aiSettings.autoResolve}
                  onChange={(e) => setAiSettings({...aiSettings, autoResolve: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="range-item">
              <div className="range-info">
                <span className="range-label">AI Confidence Threshold</span>
                <span className="range-value">{aiSettings.confidenceThreshold}%</span>
              </div>
              <input 
                type="range" 
                min="50" 
                max="100" 
                value={aiSettings.confidenceThreshold}
                onChange={(e) => setAiSettings({...aiSettings, confidenceThreshold: parseInt(e.target.value)})}
                className="range-slider"
              />
              <span className="range-desc">Minimum confidence level for AI actions</span>
            </div>
            <div className="range-item">
              <div className="range-info">
                <span className="range-label">Escalation Delay (minutes)</span>
                <span className="range-value">{aiSettings.escalationDelay}</span>
              </div>
              <input 
                type="range" 
                min="5" 
                max="120" 
                step="5"
                value={aiSettings.escalationDelay}
                onChange={(e) => setAiSettings({...aiSettings, escalationDelay: parseInt(e.target.value)})}
                className="range-slider"
              />
              <span className="range-desc">Time before escalating to human</span>
            </div>
          </div>
        </div>

        {/* Appearance */}
        <div className="settings-section">
          <div className="section-title">
            {darkMode ? <Moon size={22} /> : <Sun size={22} />}
            <h2>Appearance</h2>
          </div>
          <div className="settings-list">
            <div className="toggle-item">
              <div className="toggle-info">
                <span className="toggle-label">Dark Mode</span>
                <span className="toggle-desc">Use dark theme across the app</span>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        {/* Security */}
        <div className="settings-section">
          <div className="section-title">
            <Shield size={22} />
            <h2>Security & Privacy</h2>
          </div>
          <div className="settings-buttons">
            <button className="action-button secondary">
              Change Password
            </button>
            <button className="action-button secondary">
              Two-Factor Authentication
            </button>
            <button className="action-button secondary">
              Privacy Settings
            </button>
            <button className="action-button danger">
              Delete Account
            </button>
          </div>
        </div>

        {/* Data Management */}
        <div className="settings-section">
          <div className="section-title">
            <Database size={22} />
            <h2>Data Management</h2>
          </div>
          <div className="settings-buttons">
            <button className="action-button secondary">
              Export Data
            </button>
            <button className="action-button secondary">
              Clear Cache
            </button>
            <button className="action-button danger">
              Clear All Data
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
