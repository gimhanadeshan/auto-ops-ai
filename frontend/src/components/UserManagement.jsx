import { useState, useEffect } from 'react'
import { Users, UserPlus, Shield, Edit, Trash2, Search, Filter, CheckCircle, XCircle, AlertCircle, Mail, User as UserIcon, Lock } from 'lucide-react'
import { authService, authorizationService, userService } from '../services'
import '../styles/components/UserManagement.css'

function UserManagement({ currentUser }) {
  const [users, setUsers] = useState([])
  const [filteredUsers, setFilteredUsers] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterTier, setFilterTier] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [capabilities, setCapabilities] = useState(null)

  useEffect(() => {
    loadCapabilities()
    loadUsers()
  }, [])

  useEffect(() => {
    filterUsers()
  }, [searchQuery, filterTier, filterStatus, users])

  const loadCapabilities = async () => {
    try {
      const caps = await authorizationService.getUserCapabilities()
      setCapabilities(caps)
    } catch (err) {
      console.error('Failed to load capabilities:', err)
    }
  }

  const loadUsers = async () => {
    try {
      setLoading(true)
      const data = await userService.getAllUsers()
      setUsers(data)
      setError(null)
    } catch (err) {
      setError('Failed to load users: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const filterUsers = () => {
    let filtered = [...users]

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(user => 
        user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Tier filter
    if (filterTier !== 'all') {
      filtered = filtered.filter(user => user.tier === filterTier)
    }

    // Status filter
    if (filterStatus !== 'all') {
      const isActive = filterStatus === 'active'
      filtered = filtered.filter(user => user.is_active === isActive)
    }

    setFilteredUsers(filtered)
  }

  const handleCreateUser = () => {
    setShowCreateModal(true)
  }

  const handleEditUser = (user) => {
    setSelectedUser(user)
    setShowEditModal(true)
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      await userService.deleteUser(userId)
      setUsers(users.filter(u => u.id !== userId))
    } catch (err) {
      alert('Failed to delete user: ' + err.message)
    }
  }

  const handleToggleStatus = async (userId) => {
    try {
      const user = users.find(u => u.id === userId)
      const newStatus = !user.is_active
      const updatedUser = await userService.toggleUserStatus(userId, newStatus)
      setUsers(users.map(u => u.id === userId ? updatedUser : u))
    } catch (err) {
      alert('Failed to toggle user status: ' + err.message)
    }
  }

  const getTierColor = (tier) => {
    return authorizationService.getTierColor(tier)
  }

  const getTierBadge = (tier) => {
    return authorizationService.formatTier(tier)
  }

  if (capabilities && capabilities.tier !== 'admin') {
    return (
      <div className="access-denied">
        <AlertCircle size={48} />
        <h2>Access Denied</h2>
        <p>You need administrator privileges to access user management.</p>
      </div>
    )
  }

  return (
    <div className="user-management">
      <div className="page-header">
        <div className="header-left">
          <Users size={32} />
          <div>
            <h1>User Management</h1>
            <p>Manage users, roles, and permissions</p>
          </div>
        </div>
        <button className="btn-primary" onClick={handleCreateUser}>
          <UserPlus size={18} />
          Create User
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      <div className="filters-section">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter size={18} />
          <select 
            value={filterTier} 
            onChange={(e) => setFilterTier(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Tiers</option>
            <option value="contractor">Contractor</option>
            <option value="staff">Staff</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>

          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{users.length}</div>
          <div className="stat-label">Total Users</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{users.filter(u => u.is_active).length}</div>
          <div className="stat-label">Active Users</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{users.filter(u => u.tier === 'admin').length}</div>
          <div className="stat-label">Administrators</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{users.filter(u => !u.is_active).length}</div>
          <div className="stat-label">Inactive Users</div>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      ) : (
        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Tier</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>
                    <div className="user-cell">
                      <div className="user-avatar">
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                      <span className="user-name">{user.name}</span>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`tier-badge ${user.tier}`}>
                      <Shield size={14} />
                      {getTierBadge(user.tier)}
                    </span>
                  </td>
                  <td>
                    <button 
                      className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}
                      onClick={() => handleToggleStatus(user.id)}
                    >
                      {user.is_active ? (
                        <>
                          <CheckCircle size={14} />
                          Active
                        </>
                      ) : (
                        <>
                          <XCircle size={14} />
                          Inactive
                        </>
                      )}
                    </button>
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon" 
                        onClick={() => handleEditUser(user)}
                        title="Edit User"
                      >
                        <Edit size={16} />
                      </button>
                      <button 
                        className="btn-icon btn-danger" 
                        onClick={() => handleDeleteUser(user.id)}
                        title="Delete User"
                        disabled={user.id === currentUser.id}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredUsers.length === 0 && (
            <div className="empty-state">
              <Users size={48} />
              <p>No users found matching your filters.</p>
            </div>
          )}
        </div>
      )}

      {showCreateModal && (
        <CreateUserModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={(newUser) => {
            setUsers([...users, newUser])
            setShowCreateModal(false)
          }}
        />
      )}

      {showEditModal && selectedUser && (
        <EditUserModal 
          user={selectedUser}
          currentUser={currentUser}
          onClose={() => {
            setShowEditModal(false)
            setSelectedUser(null)
          }}
          onSuccess={(updatedUser) => {
            setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u))
            setShowEditModal(false)
            setSelectedUser(null)
          }}
        />
      )}
    </div>
  )
}

function CreateUserModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    confirmPassword: '',
    tier: 'staff'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    try {
      setLoading(true)
      const newUser = await authService.register({
        email: formData.email,
        name: formData.name,
        password: formData.password,
        tier: formData.tier
      })
      onSuccess(newUser)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New User</h2>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="user-form">
          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label>
                <UserIcon size={16} />
                Full Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-group">
              <label>
                <Mail size={16} />
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john.doe@company.com"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                <Lock size={16} />
                Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Min 6 characters"
                required
              />
            </div>

            <div className="form-group">
              <label>
                <Lock size={16} />
                Confirm Password
              </label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Re-enter password"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>
              <Shield size={16} />
              User Tier (Role)
            </label>
            <select
              value={formData.tier}
              onChange={(e) => setFormData({ ...formData, tier: e.target.value })}
              required
            >
              <option value="contractor">Contractor - Limited access, external users</option>
              <option value="staff">Staff - Regular employees</option>
              <option value="manager">Manager - Department managers</option>
              <option value="admin">Admin - IT administrators</option>
            </select>
            <small className="form-hint">
              {formData.tier === 'contractor' && '⚠️ Contractors require approval for all actions'}
              {formData.tier === 'staff' && '✅ Can execute SAFE and LOW risk actions'}
              {formData.tier === 'manager' && '✅ Can execute SAFE, LOW, and MEDIUM risk actions'}
              {formData.tier === 'admin' && '✅ Full system access, all risk levels'}
            </small>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function EditUserModal({ user, currentUser, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: user.name,
    tier: user.tier,
    is_active: user.is_active
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
      setLoading(true)
      const updatedUser = await userService.updateUser(user.id, formData)
      onSuccess(updatedUser)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const isSelfEdit = user.id === currentUser.id

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit User</h2>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="user-form">
          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {isSelfEdit && (
            <div className="alert alert-warning">
              <AlertCircle size={20} />
              You are editing your own account. Be careful when changing your tier.
            </div>
          )}

          <div className="form-group">
            <label>
              <Mail size={16} />
              Email (Read-only)
            </label>
            <input
              type="email"
              value={user.email}
              disabled
              className="input-disabled"
            />
          </div>

          <div className="form-group">
            <label>
              <UserIcon size={16} />
              Full Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>
              <Shield size={16} />
              User Tier (Role)
            </label>
            <select
              value={formData.tier}
              onChange={(e) => setFormData({ ...formData, tier: e.target.value })}
              required
            >
              <option value="contractor">Contractor - Limited access</option>
              <option value="staff">Staff - Regular employees</option>
              <option value="manager">Manager - Department managers</option>
              <option value="admin">Admin - IT administrators</option>
            </select>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              <span>Active Account</span>
            </label>
            <small className="form-hint">
              {formData.is_active 
                ? '✅ User can login and access the system' 
                : '⚠️ User will be blocked from logging in'}
            </small>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UserManagement
