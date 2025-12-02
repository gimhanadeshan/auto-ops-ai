import { useState, useEffect } from 'react'
import { Activity, Cpu, HardDrive, Server, Wifi, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react'
import '../styles/components/SystemMonitoring.css'

function SystemMonitoring() {
  const [refreshing, setRefreshing] = useState(false)
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 45,
    memory: 62,
    disk: 78,
    network: 35
  })

  const [services, setServices] = useState([
    { name: 'API Server', status: 'running', port: '8000', uptime: '5d 12h', health: 'healthy' },
    { name: 'Database', status: 'running', port: '5432', uptime: '12d 3h', health: 'healthy' },
    { name: 'AI Engine', status: 'running', port: '8001', uptime: '3d 8h', health: 'healthy' },
    { name: 'Redis Cache', status: 'running', port: '6379', uptime: '8d 15h', health: 'healthy' },
    { name: 'Message Queue', status: 'running', port: '5672', uptime: '6d 22h', health: 'healthy' },
    { name: 'Backup Service', status: 'running', port: 'N/A', uptime: '10d 5h', health: 'healthy' }
  ])

  const [logs, setLogs] = useState([
    { time: '12:45:23', level: 'info', message: 'System health check completed successfully' },
    { time: '12:44:15', level: 'info', message: 'Backup completed: 2.3 GB transferred' },
    { time: '12:42:08', level: 'warning', message: 'High memory usage detected (85%)' },
    { time: '12:40:00', level: 'info', message: 'Database optimization completed' },
    { time: '12:38:45', level: 'info', message: 'AI model cache refreshed' }
  ])

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.min(100, Math.max(0, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.min(100, Math.max(0, prev.memory + (Math.random() - 0.5) * 5)),
        disk: Math.min(100, Math.max(0, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.min(100, Math.max(0, prev.network + (Math.random() - 0.5) * 20))
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    setTimeout(() => setRefreshing(false), 1000)
  }

  const getMetricColor = (value) => {
    if (value < 50) return 'good'
    if (value < 80) return 'warning'
    return 'critical'
  }

  const MetricCard = ({ icon: Icon, title, value, unit, color }) => (
    <div className={`metric-card ${color}`}>
      <div className="metric-icon">
        <Icon size={28} />
      </div>
      <div className="metric-info">
        <span className="metric-title">{title}</span>
        <div className="metric-value">
          <span className="value">{Math.round(value)}</span>
          <span className="unit">{unit}</span>
        </div>
      </div>
      <div className="metric-bar">
        <div className="metric-fill" style={{ width: `${value}%` }}></div>
      </div>
    </div>
  )

  return (
    <div className="monitoring-container">
      <div className="monitoring-header">
        <div>
          <h1>System Monitoring</h1>
          <p>Real-time system health and performance metrics</p>
        </div>
        <button 
          onClick={handleRefresh} 
          className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
        >
          <RefreshCw size={20} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="metrics-grid">
        <MetricCard
          icon={Cpu}
          title="CPU Usage"
          value={systemMetrics.cpu}
          unit="%"
          color={getMetricColor(systemMetrics.cpu)}
        />
        <MetricCard
          icon={Activity}
          title="Memory Usage"
          value={systemMetrics.memory}
          unit="%"
          color={getMetricColor(systemMetrics.memory)}
        />
        <MetricCard
          icon={HardDrive}
          title="Disk Usage"
          value={systemMetrics.disk}
          unit="%"
          color={getMetricColor(systemMetrics.disk)}
        />
        <MetricCard
          icon={Wifi}
          title="Network Activity"
          value={systemMetrics.network}
          unit="%"
          color={getMetricColor(systemMetrics.network)}
        />
      </div>

      <div className="monitoring-content">
        <div className="services-section">
          <div className="section-header">
            <h2>
              <Server size={20} />
              Running Services
            </h2>
          </div>
          <div className="services-table">
            <table>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Status</th>
                  <th>Port</th>
                  <th>Uptime</th>
                  <th>Health</th>
                </tr>
              </thead>
              <tbody>
                {services.map((service, idx) => (
                  <tr key={idx}>
                    <td className="service-name">{service.name}</td>
                    <td>
                      <span className={`status-badge ${service.status}`}>
                        {service.status === 'running' ? (
                          <CheckCircle size={14} />
                        ) : (
                          <AlertTriangle size={14} />
                        )}
                        {service.status}
                      </span>
                    </td>
                    <td className="port">{service.port}</td>
                    <td className="uptime">{service.uptime}</td>
                    <td>
                      <span className={`health-badge ${service.health}`}>
                        {service.health}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="logs-section">
          <div className="section-header">
            <h2>
              <Activity size={20} />
              System Logs
            </h2>
          </div>
          <div className="logs-container">
            {logs.map((log, idx) => (
              <div key={idx} className={`log-entry ${log.level}`}>
                <span className="log-time">{log.time}</span>
                <span className={`log-level ${log.level}`}>{log.level.toUpperCase()}</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemMonitoring
