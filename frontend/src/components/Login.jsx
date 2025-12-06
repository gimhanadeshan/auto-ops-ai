import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, LogIn, AlertTriangle } from 'lucide-react'
import { authService } from '../services/authService'
import '../styles/components/Auth.css'

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const data = await authService.login({ email, password })
      
      // Store token and user info
      console.log('✓ Login successful:', data)
      localStorage.setItem('token', data.access_token)
      console.log('✓ Token stored in localStorage')
      localStorage.setItem('user', JSON.stringify(data.user))
      console.log('✓ User data stored')
      
      // Verify token was stored
      const storedToken = localStorage.getItem('token')
      console.log('✓ Verification - Token in storage:', storedToken ? 'YES' : 'NO')
      
      onLogin(data.user)
      navigate('/')
      
    } catch (err) {
      console.error('✗ Login error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
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
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon">
            <Bot size={48} strokeWidth={2} />
          </div>
          <h1>Auto-Ops-AI</h1>
          <p>AI-powered IT Support Assistant</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Login</h2>

          {error && (
            <div className="error-alert">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label>
              <Mail size={16} />
              <span>Email</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@company.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label>
              <Lock size={16} />
              <span>Password</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            <LogIn size={18} />
            <span>{loading ? 'Logging in...' : 'Login'}</span>
          </button>

          <div className="auth-switch">
            Don't have an account? <button type="button" onClick={() => navigate('/register')} className="link-btn">Register</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Login
