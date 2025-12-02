import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  TrendingDown,
  AlertCircle, 
  CheckCircle, 
  Clock, 
  Zap,
  Server,
  Users,
  Activity,
  ArrowRight,
  FileText,
  MessageSquare
} from 'lucide-react'
import '../styles/components/Dashboard.css'

function Dashboard({ user }) {
  const [stats, setStats] = useState({
    totalTickets: 0,
    openTickets: 0,
    resolvedTickets: 0,
    escalatedTickets: 0,
    avgResolutionTime: '0h',
    systemHealth: 'Good'
  })

  const [recentIssues, setRecentIssues] = useState([])
  const [systemStatus, setSystemStatus] = useState([
    { name: 'API Server', status: 'online', uptime: '99.9%' },
    { name: 'Database', status: 'online', uptime: '99.8%' },
    { name: 'AI Service', status: 'online', uptime: '99.5%' },
    { name: 'Backup Service', status: 'online', uptime: '100%' }
  ])

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Mock data - replace with actual API call
      setStats({
        totalTickets: 156,
        openTickets: 23,
        resolvedTickets: 128,
        escalatedTickets: 5,
        avgResolutionTime: '2.5h',
        systemHealth: 'Good'
      })

      setRecentIssues([
        { id: 'T-001', title: 'VPN Connection Issue', priority: 'high', status: 'open', time: '5m ago' },
        { id: 'T-002', title: 'Slow Laptop Performance', priority: 'medium', status: 'in-progress', time: '15m ago' },
        { id: 'T-003', title: 'Printer Not Working', priority: 'low', status: 'open', time: '1h ago' }
      ])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  const StatCard = ({ title, value, icon: Icon, trend, trendValue, color }) => (
    <div className={`stat-card ${color}`}>
      <div className="stat-header">
        <div className="stat-icon">
          <Icon size={24} />
        </div>
        {trend && (
          <div className={`stat-trend ${trend}`}>
            {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{trendValue}</span>
          </div>
        )}
      </div>
      <div className="stat-body">
        <h3>{value}</h3>
        <p>{title}</p>
      </div>
    </div>
  )

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Welcome back, {user?.name || 'User'}!</h1>
          <p>Here's what's happening with your IT support system today.</p>
        </div>
        <Link to="/chat" className="quick-action-btn">
          <MessageSquare size={20} />
          <span>Start New Chat</span>
        </Link>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Tickets"
          value={stats.totalTickets}
          icon={FileText}
          trend="up"
          trendValue="+12%"
          color="blue"
        />
        <StatCard
          title="Open Tickets"
          value={stats.openTickets}
          icon={Clock}
          color="orange"
        />
        <StatCard
          title="Resolved Today"
          value={stats.resolvedTickets}
          icon={CheckCircle}
          trend="up"
          trendValue="+8%"
          color="green"
        />
        <StatCard
          title="Escalated"
          value={stats.escalatedTickets}
          icon={AlertCircle}
          trend="down"
          trendValue="-3%"
          color="red"
        />
      </div>

      <div className="dashboard-content">
        <div className="content-section">
          <div className="section-header">
            <h2>Recent Issues</h2>
            <Link to="/tickets" className="view-all-link">
              View All <ArrowRight size={16} />
            </Link>
          </div>
          <div className="issues-list">
            {recentIssues.map((issue) => (
              <div key={issue.id} className="issue-item">
                <div className="issue-info">
                  <span className="issue-id">{issue.id}</span>
                  <span className="issue-title">{issue.title}</span>
                </div>
                <div className="issue-meta">
                  <span className={`priority-badge ${issue.priority}`}>
                    {issue.priority}
                  </span>
                  <span className={`status-badge ${issue.status}`}>
                    {issue.status}
                  </span>
                  <span className="issue-time">{issue.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="content-section">
          <div className="section-header">
            <h2>System Status</h2>
            <Link to="/monitoring" className="view-all-link">
              View Details <ArrowRight size={16} />
            </Link>
          </div>
          <div className="system-status-list">
            {systemStatus.map((service, idx) => (
              <div key={idx} className="status-item">
                <div className="status-info">
                  <Server size={18} />
                  <span className="service-name">{service.name}</span>
                </div>
                <div className="status-details">
                  <span className="uptime">Uptime: {service.uptime}</span>
                  <span className={`status-indicator ${service.status}`}>
                    <span className="status-dot"></span>
                    {service.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="quick-actions-panel">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/chat" className="action-card">
            <MessageSquare size={28} />
            <span>Report Issue</span>
          </Link>
          <Link to="/tickets" className="action-card">
            <FileText size={28} />
            <span>View Tickets</span>
          </Link>
          <Link to="/monitoring" className="action-card">
            <Activity size={28} />
            <span>System Monitor</span>
          </Link>
          <Link to="/reports" className="action-card">
            <Zap size={28} />
            <span>View Reports</span>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
