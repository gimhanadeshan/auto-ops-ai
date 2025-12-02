import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, User, Shield, CheckCircle, AlertTriangle, UserPlus } from 'lucide-react'
import './Auth.css'

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    confirmPassword: '',
    tier: 'staff'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          name: formData.name,
          password: formData.password,
          tier: formData.tier
        })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Registration failed')
      }

      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 2000)
      
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="success-message">
            <span className="success-icon">
              <CheckCircle size={64} strokeWidth={2} />
            </span>
            <h2>Registration Successful!</h2>
            <p>Redirecting to login...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-container">
      <div className="tech-background">
        <div className="grid-lines"></div>
        <div className="floating-particles">
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
        </div>
        <div className="scan-line"></div>
      </div>
      <div className="auth-card register-card">
        <div className="auth-header">
          <div className="auth-icon">
            <Bot size={48} strokeWidth={2} />
          </div>
          <h1>Auto-Ops-AI</h1>
          <p>AI-powered IT Support Assistant</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form register-form">
          <h2>Create Account</h2>

          {error && (
            <div className="error-alert">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-grid">
            <div className="form-group">
              <label>
                <User size={16} />
                <span>Full Name</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-group">
              <label>
                <Mail size={16} />
                <span>Email</span>
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="john.doe@company.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label>
                <Shield size={16} />
                <span>User Tier</span>
              </label>
              <select
                name="tier"
                value={formData.tier}
                onChange={handleChange}
                className="tier-select"
              >
                <option value="staff">Staff</option>
                <option value="manager">Manager</option>
                <option value="contractor">Contractor</option>
              </select>
              <small>Managers get higher priority on tickets</small>
            </div>

            <div className="form-group">
              <label>
                <Lock size={16} />
                <span>Password</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                autoComplete="new-password"
                minLength={6}
              />
              <small>Minimum 6 characters</small>
            </div>

            <div className="form-group form-group-full">
              <label>
                <Lock size={16} />
                <span>Confirm Password</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
            </div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            <UserPlus size={18} />
            <span>{loading ? 'Creating Account...' : 'Register'}</span>
          </button>

          <div className="auth-switch">
            Already have an account? <button type="button" onClick={() => navigate('/login')} className="link-btn">Login</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Register
