import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  Activity, 
  BarChart3, 
  Settings, 
  LogOut, 
  Bot,
  User,
  Users,
  Shield,
  Bell,
  Database,
  Zap
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import { authorizationService } from '../services'
import '../styles/components/Sidebar.css'

function Sidebar({ user, capabilities, onLogout }) {
  const baseNavItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/chat', icon: MessageSquare, label: 'AI Support Chat' },
    { path: '/tickets', icon: FileText, label: 'Tickets' },
    { path: '/monitoring', icon: Activity, label: 'System Monitoring' },
    { path: '/reports', icon: BarChart3, label: 'Reports & Analytics' },
    { path: '/automation', icon: Zap, label: 'Automation Rules' },
    { path: '/knowledge-base', icon: Database, label: 'Knowledge Base' },
  ]

  // Add admin-only items
  const navItems = [
    ...baseNavItems,
    ...(capabilities?.tier === 'admin' ? [
      { path: '/users', icon: Users, label: 'User Management', adminOnly: true }
    ] : []),
    { path: '/settings', icon: Settings, label: 'Settings' }
  ]

  const getTierColor = () => {
    if (!user?.tier) return '#6c757d'
    return authorizationService.getTierColor(user.tier)
  }

  const formatTier = () => {
    if (!user?.tier) return 'Standard'
    return authorizationService.formatTier(user.tier)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <Bot size={32} strokeWidth={2} />
          <div className="logo-text">
            <h2>Auto-Ops-AI</h2>
            <span className="tagline">IT Support System</span>
          </div>
        </div>
      </div>

      <div className="sidebar-user">
        <div className="user-avatar">
          <User size={20} />
        </div>
        <div className="user-info">
          <span className="user-name">{user?.name || 'Guest'}</span>
          <span 
            className="user-tier"
            style={{ 
              backgroundColor: getTierColor(),
              color: 'white',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
              fontSize: '0.75rem'
            }}
          >
            <Shield size={12} />
            {formatTier()}
          </span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `nav-item ${isActive ? 'active' : ''} ${item.adminOnly ? 'admin-only' : ''}`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
            {item.adminOnly && <span className="admin-badge">Admin</span>}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <ThemeToggle />
        <button onClick={onLogout} className="logout-btn">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
