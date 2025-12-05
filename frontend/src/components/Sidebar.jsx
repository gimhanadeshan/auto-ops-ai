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
  Shield,
  Bell,
  Database,
  Zap,
  AlertCircle,
  Rocket,
  Users,
  FileCheck
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import '../styles/components/Sidebar.css'

function Sidebar({ user, onLogout }) {
  // Check if user is admin
  const isAdmin = user?.role === 'system_admin' || user?.role === 'it_admin';

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/quick-actions', icon: Rocket, label: 'Quick Actions' },
    { path: '/chat', icon: MessageSquare, label: 'AI Support Chat' },
    { path: '/tickets', icon: FileText, label: 'Tickets' },
    { path: '/monitoring', icon: Activity, label: 'System Monitoring' },
    { path: '/reports', icon: BarChart3, label: 'Reports & Analytics' },
    { path: '/automation', icon: Zap, label: 'Automation Rules' },
    { path: '/error-codes', icon: AlertCircle, label: 'Error Codes' },
    { path: '/knowledge-base', icon: Database, label: 'Knowledge Base' },
    ...(isAdmin ? [
      { path: '/users', icon: Users, label: 'User Management', adminOnly: true },
      { path: '/audit-logs', icon: FileCheck, label: 'Audit Logs', adminOnly: true }
    ] : []),
    { path: '/settings', icon: Settings, label: 'Settings' }
  ]

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
          <span className="user-tier">
            <Shield size={12} />
            {user?.tier || 'Standard'}
          </span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''} ${item.adminOnly ? 'admin-only' : ''}`}
            title={item.adminOnly ? 'Admin Only' : item.label}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
            {item.adminOnly && <Shield size={14} className="admin-badge" />}
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
