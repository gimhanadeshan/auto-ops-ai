import { useState, useEffect } from 'react';
import { 
  Users, 
  Shield, 
  UserCheck, 
  UserX, 
  Edit2, 
  Trash2,
  Search,
  Filter,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import userService from '../services/userService';
import '../styles/components/UserManagement.css';

const ROLES = [
  { value: 'staff', label: 'Staff', color: '#6c757d' },
  { value: 'contractor', label: 'Contractor', color: '#17a2b8' },
  { value: 'manager', label: 'Manager', color: '#ffc107' },
  { value: 'support_l1', label: 'Support L1', color: '#28a745' },
  { value: 'support_l2', label: 'Support L2', color: '#20c997' },
  { value: 'support_l3', label: 'Support L3', color: '#17a2b8' },
  { value: 'it_admin', label: 'IT Admin', color: '#fd7e14' },
  { value: 'system_admin', label: 'System Admin', color: '#dc3545' }
];

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [selectedRole, setSelectedRole] = useState('');
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, [filterRole, filterStatus]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (filterRole) params.role = filterRole;
      if (filterStatus !== '') params.is_active = filterStatus === 'active';
      
      const data = await userService.getUsers(params);
      setUsers(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const data = await userService.getRoles();
      setRoles(data);
    } catch (err) {
      console.error('Error fetching roles:', err);
    }
  };

  const handleUpdateRole = async () => {
    if (!editingUser || !selectedRole) return;

    try {
      await userService.updateUserRole(editingUser.id, selectedRole);
      setSuccessMessage(`Successfully updated role for ${editingUser.email}`);
      setShowRoleModal(false);
      setEditingUser(null);
      setSelectedRole('');
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleToggleStatus = async (user) => {
    try {
      await userService.updateUserStatus(user.id, !user.is_active);
      setSuccessMessage(`Successfully ${user.is_active ? 'deactivated' : 'activated'} ${user.email}`);
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user status');
    }
  };

  const openRoleModal = (user) => {
    setEditingUser(user);
    setSelectedRole(user.role);
    setShowRoleModal(true);
  };

  const filteredUsers = (users || []).filter(user => {
    const matchesSearch = 
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getRoleLabel = (roleValue) => {
    const role = ROLES.find(r => r.value === roleValue);
    return role ? role.label : roleValue;
  };

  const getRoleColor = (roleValue) => {
    const role = ROLES.find(r => r.value === roleValue);
    return role ? role.color : '#6c757d';
  };

  return (
    <div className="user-management">
      <div className="page-header">
        <div className="header-content">
          <Users className="header-icon" size={32} />
          <div>
            <h1>User Management</h1>
            <p>Manage users, roles, and access control</p>
          </div>
        </div>
        <button className="btn-refresh" onClick={fetchUsers} disabled={loading}>
          <RefreshCw size={18} className={loading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <CheckCircle size={18} />
          {successMessage}
        </div>
      )}

      <div className="filters-section">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by email or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter size={18} />
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
          >
            <option value="">All Roles</option>
            {ROLES.map(role => (
              <option key={role.value} value={role.value}>{role.label}</option>
            ))}
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <div className="users-table-container">
        {loading ? (
          <div className="loading-state">
            <RefreshCw className="spinning" size={32} />
            <p>Loading users...</p>
          </div>
        ) : (
          <table className="users-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Permissions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>
                    <div className="user-info">
                      <div className="user-avatar">
                        {user.full_name?.charAt(0) || user.email.charAt(0)}
                      </div>
                      <span>{user.full_name || 'N/A'}</span>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span 
                      className="role-badge"
                      style={{ backgroundColor: getRoleColor(user.role) }}
                    >
                      <Shield size={14} />
                      {getRoleLabel(user.role)}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? (
                        <>
                          <UserCheck size={14} />
                          Active
                        </>
                      ) : (
                        <>
                          <UserX size={14} />
                          Inactive
                        </>
                      )}
                    </span>
                  </td>
                  <td>
                    <div className="permissions-list">
                      {user.permissions && user.permissions.length > 0 ? (
                        <span className="permission-count">
                          {user.permissions.length} permissions
                        </span>
                      ) : (
                        <span className="no-permissions">No permissions</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="icon-btn"
                        onClick={() => openRoleModal(user)}
                        title="Change Role"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        className={`icon-btn ${user.is_active ? 'delete' : 'activate'}`}
                        onClick={() => handleToggleStatus(user)}
                        title={user.is_active ? 'Deactivate' : 'Activate'}
                      >
                        {user.is_active ? <Trash2 size={16} /> : <UserCheck size={16} />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && filteredUsers.length === 0 && (
          <div className="empty-state">
            <Users size={48} />
            <p>No users found</p>
          </div>
        )}
      </div>

      {showRoleModal && (
        <div className="modal-overlay" onClick={() => setShowRoleModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Change User Role</h2>
            <p className="modal-description">
              Update role for <strong>{editingUser?.email}</strong>
            </p>

            <div className="form-group">
              <label>Select New Role</label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="role-select"
              >
                {ROLES.map(role => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>

            {selectedRole && roles.find(r => r.role === selectedRole) && (
              <div className="role-permissions">
                <h4>Permissions for {getRoleLabel(selectedRole)}</h4>
                <ul>
                  {roles.find(r => r.role === selectedRole)?.permissions.map(perm => (
                    <li key={perm}>
                      <CheckCircle size={14} />
                      {perm.replace(/_/g, ' ')}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setShowRoleModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn-confirm"
                onClick={handleUpdateRole}
                disabled={!selectedRole || selectedRole === editingUser?.role}
              >
                Update Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserManagement;
