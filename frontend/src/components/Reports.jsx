import { useState } from 'react'
import { BarChart3, TrendingUp, Calendar, Download, Filter } from 'lucide-react'
import '../styles/components/Reports.css'

function Reports() {
  const [dateRange, setDateRange] = useState('7days')
  const [reportType, setReportType] = useState('tickets')

  const ticketStats = {
    total: 245,
    resolved: 198,
    open: 32,
    escalated: 15,
    avgResolution: '2.8 hours',
    satisfactionRate: '94%'
  }

  const categoryData = [
    { category: 'VPN Issues', count: 45, percentage: 18 },
    { category: 'Performance', count: 38, percentage: 15 },
    { category: 'Software Crashes', count: 32, percentage: 13 },
    { category: 'Hardware', count: 28, percentage: 11 },
    { category: 'Network', count: 25, percentage: 10 },
    { category: 'Access Issues', count: 22, percentage: 9 },
    { category: 'Other', count: 55, percentage: 24 }
  ]

  const trendsData = [
    { week: 'Week 1', tickets: 48 },
    { week: 'Week 2', tickets: 52 },
    { week: 'Week 3', tickets: 45 },
    { week: 'Week 4', tickets: 58 }
  ]

  const handleExport = () => {
    alert('Exporting report as PDF...')
  }

  return (
    <div className="reports-container">
      <div className="reports-header">
        <div>
          <h1>Reports & Analytics</h1>
          <p>Comprehensive insights into system performance and ticket trends</p>
        </div>
        <div className="header-actions">
          <button className="filter-btn">
            <Filter size={18} />
            <span>Filters</span>
          </button>
          <button onClick={handleExport} className="export-btn">
            <Download size={18} />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      <div className="report-controls">
        <div className="control-group">
          <label>Date Range:</label>
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
            <option value="today">Today</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        <div className="control-group">
          <label>Report Type:</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option value="tickets">Ticket Summary</option>
            <option value="performance">Performance</option>
            <option value="users">User Activity</option>
            <option value="system">System Health</option>
          </select>
        </div>
      </div>

      <div className="stats-overview">
        <div className="stat-box">
          <div className="stat-label">Total Tickets</div>
          <div className="stat-value">{ticketStats.total}</div>
          <div className="stat-change positive">+12% from last period</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Resolved</div>
          <div className="stat-value">{ticketStats.resolved}</div>
          <div className="stat-change positive">+8% resolution rate</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Open Tickets</div>
          <div className="stat-value">{ticketStats.open}</div>
          <div className="stat-change neutral">-2% from last period</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Avg Resolution</div>
          <div className="stat-value">{ticketStats.avgResolution}</div>
          <div className="stat-change positive">15% faster</div>
        </div>
      </div>

      <div className="reports-grid">
        <div className="report-card">
          <div className="card-header">
            <h3>
              <BarChart3 size={20} />
              Tickets by Category
            </h3>
          </div>
          <div className="chart-container">
            {categoryData.map((item, idx) => (
              <div key={idx} className="bar-item">
                <div className="bar-label">
                  <span>{item.category}</span>
                  <span className="bar-count">{item.count}</span>
                </div>
                <div className="bar-graph">
                  <div 
                    className="bar-fill" 
                    style={{ width: `${item.percentage * 4}%` }}
                  ></div>
                  <span className="bar-percentage">{item.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="report-card">
          <div className="card-header">
            <h3>
              <TrendingUp size={20} />
              Weekly Trends
            </h3>
          </div>
          <div className="trend-chart">
            {trendsData.map((item, idx) => (
              <div key={idx} className="trend-bar">
                <div 
                  className="trend-fill" 
                  style={{ height: `${(item.tickets / 60) * 100}%` }}
                ></div>
                <div className="trend-label">{item.week}</div>
                <div className="trend-value">{item.tickets}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="report-card">
          <div className="card-header">
            <h3>
              <Calendar size={20} />
              Resolution Time Distribution
            </h3>
          </div>
          <div className="distribution-chart">
            <div className="dist-item">
              <span className="dist-label">{'< 1 hour'}</span>
              <div className="dist-bar">
                <div className="dist-fill" style={{ width: '65%' }}></div>
              </div>
              <span className="dist-value">65%</span>
            </div>
            <div className="dist-item">
              <span className="dist-label">1-4 hours</span>
              <div className="dist-bar">
                <div className="dist-fill" style={{ width: '25%' }}></div>
              </div>
              <span className="dist-value">25%</span>
            </div>
            <div className="dist-item">
              <span className="dist-label">4-24 hours</span>
              <div className="dist-bar">
                <div className="dist-fill" style={{ width: '8%' }}></div>
              </div>
              <span className="dist-value">8%</span>
            </div>
            <div className="dist-item">
              <span className="dist-label">{'> 24 hours'}</span>
              <div className="dist-bar">
                <div className="dist-fill" style={{ width: '2%' }}></div>
              </div>
              <span className="dist-value">2%</span>
            </div>
          </div>
        </div>

        <div className="report-card">
          <div className="card-header">
            <h3>Performance Metrics</h3>
          </div>
          <div className="metrics-list">
            <div className="metric-item">
              <span className="metric-name">First Response Time</span>
              <span className="metric-value">12 min</span>
            </div>
            <div className="metric-item">
              <span className="metric-name">Customer Satisfaction</span>
              <span className="metric-value">{ticketStats.satisfactionRate}</span>
            </div>
            <div className="metric-item">
              <span className="metric-name">AI Resolution Rate</span>
              <span className="metric-value">68%</span>
            </div>
            <div className="metric-item">
              <span className="metric-name">Escalation Rate</span>
              <span className="metric-value">6%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports
