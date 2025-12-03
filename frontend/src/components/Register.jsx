import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, User, Shield, CheckCircle, AlertTriangle, UserPlus, Info, Briefcase, Users as UsersIcon, UserCog } from 'lucide-react'
import { authService, authorizationService } from '../services'
import '../styles/components/Auth.css'

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
  const [passwordStrength, setPasswordStrength] = useState(0)
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })

    // Calculate password strength
    if (name === 'password') {
      let strength = 0
      if (value.length >= 6) strength++
      if (value.length >= 10) strength++
      if (/[A-Z]/.test(value)) strength++
      if (/[0-9]/.test(value)) strength++
      if (/[^A-Za-z0-9]/.test(value)) strength++
      setPasswordStrength(Math.min(strength, 4))
    }
  }

  const getPasswordStrengthLabel = () => {
    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
    return labels[passwordStrength] || 'Very Weak'
  }

  const getPasswordStrengthColor = () => {
    const colors = ['#ef4444', '#f97316', '#fbbf24', '#10b981', '#059669']
    return colors[passwordStrength] || '#ef4444'
  }

  const getTierInfo = (tier) => {
    const info = {
      contractor: {
        description: 'Limited access for external users',
        permissions: 'View own tickets, execute SAFE actions (with approval)',
        icon: Lock
      },
      staff: {
        description: 'Regular employee access',
        permissions: 'View all tickets, execute SAFE and LOW risk actions',
        icon: UsersIcon
      },
      manager: {
        description: 'Department manager privileges',
        permissions: 'Update all tickets, execute up to MEDIUM risk actions, edit knowledge base',
        icon: Briefcase
      }
    }
    return info[tier] || info.staff
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
      await authService.register({
        email: formData.email,
        name: formData.name,
        password: formData.password,
        tier: formData.tier
      })

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
            <Bot size={48} strokeWidth={1.5} />
          </div>
          <h1>Auto-Ops AI</h1>
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
                <Lock size={16} />
                <span>Password</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 6 characters"
                required
                autoComplete="new-password"
                minLength={6}
              />
              {formData.password && (
                <div className="password-strength">
                  <div className="strength-bar">
                    <div 
                      className="strength-fill" 
                      style={{ 
                        width: `${(passwordStrength / 4) * 100}%`,
                        backgroundColor: getPasswordStrengthColor()
                      }}
                    />
                  </div>
                  <span style={{ color: getPasswordStrengthColor() }}>
                    {getPasswordStrengthLabel()}
                  </span>
                </div>
              )}
            </div>

            <div className="form-group">
              <label>
                <Lock size={16} />
                <span>Confirm Password</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter password"
                required
                autoComplete="new-password"
              />
              {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                <small className="error-hint">Passwords do not match</small>
              )}
            </div>

            <div className="form-group form-group-full tier-selection">
              <label>
                <Shield size={16} />
                <span>User Tier (Role)</span>
              </label>
              <div className="tier-options">
                {['contractor', 'staff', 'manager'].map(tier => {
                  const TierIcon = getTierInfo(tier).icon
                  return (
                    <div 
                      key={tier}
                      className={`tier-option ${formData.tier === tier ? 'selected' : ''}`}
                      onClick={() => setFormData({ ...formData, tier })}
                    >
                      <div className="tier-header">
                        <TierIcon size={20} className="tier-icon" />
                        <span className="tier-name">{authorizationService.formatTier(tier)}</span>
                        {formData.tier === tier && <CheckCircle size={16} className="check-icon" />}
                      </div>
                      <p className="tier-description">{getTierInfo(tier).description}</p>
                      <small className="tier-permissions">
                        <Info size={12} /> {getTierInfo(tier).permissions}
                      </small>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            <UserPlus size={18} />
            <span>{loading ? 'Creating Account...' : 'Create Account'}</span>
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
