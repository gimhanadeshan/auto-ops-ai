import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Authorization Service
 * Handles permission checks and role-based access control
 */
export const authorizationService = {
  /**
   * Check if action is authorized
   * @param {Object} actionRequest - Action details
   * @param {string} actionRequest.action_type - Type of action
   * @param {string} actionRequest.action_description - Description
   * @param {string} actionRequest.risk_level - Risk level (safe, low, medium, high, critical)
   * @param {string} [actionRequest.target_resource] - Target resource
   * @param {boolean} [actionRequest.requires_confirmation] - Whether confirmation is needed
   */
  async authorizeAction(actionRequest) {
    return httpClient.post(API_ENDPOINTS.AUTHORIZATION.AUTHORIZE_ACTION, actionRequest)
  },

  /**
   * Get current user's capabilities and permissions
   */
  async getUserCapabilities() {
    return httpClient.get(API_ENDPOINTS.AUTHORIZATION.CAPABILITIES)
  },

  /**
   * Check if user has a specific permission
   * @param {string} permissionName - Permission name to check
   */
  async checkPermission(permissionName) {
    return httpClient.get(`${API_ENDPOINTS.AUTHORIZATION.CHECK_PERMISSION}/${permissionName}`)
  },

  /**
   * Get audit log entries
   * @param {Object} [filters] - Optional filters
   * @param {string} [filters.user_id] - Filter by user ID
   * @param {number} [filters.limit] - Maximum entries to return
   */
  async getAuditLog(filters = {}) {
    const params = new URLSearchParams()
    if (filters.user_id) params.append('user_id', filters.user_id)
    if (filters.limit) params.append('limit', filters.limit)
    
    const queryString = params.toString()
    const url = queryString 
      ? `${API_ENDPOINTS.AUTHORIZATION.AUDIT_LOG}?${queryString}`
      : API_ENDPOINTS.AUTHORIZATION.AUDIT_LOG
    
    return httpClient.get(url)
  },

  /**
   * Get all permissions in the system
   */
  async getAllPermissions() {
    return httpClient.get(API_ENDPOINTS.AUTHORIZATION.ALL_PERMISSIONS)
  },

  /**
   * Get all roles and their permissions (Admin only)
   */
  async getAllRoles() {
    return httpClient.get(API_ENDPOINTS.AUTHORIZATION.ROLES)
  },

  /**
   * Helper: Check if user can execute a specific risk level
   * @param {Array<string>} canExecuteRisks - Array of risk levels user can execute
   * @param {string} riskLevel - Risk level to check
   */
  canExecuteRisk(canExecuteRisks, riskLevel) {
    return canExecuteRisks.includes(riskLevel.toLowerCase())
  },

  /**
   * Helper: Format tier name for display
   * @param {string} tier - User tier
   */
  formatTier(tier) {
    const tierMap = {
      'contractor': 'Contractor',
      'staff': 'Staff',
      'manager': 'Manager',
      'admin': 'Administrator'
    }
    return tierMap[tier] || tier
  },

  /**
   * Helper: Get tier badge color
   * @param {string} tier - User tier
   */
  getTierColor(tier) {
    const colorMap = {
      'contractor': '#6c757d',  // Gray
      'staff': '#0d6efd',        // Blue
      'manager': '#198754',      // Green
      'admin': '#dc3545'         // Red
    }
    return colorMap[tier] || '#6c757d'
  },

  /**
   * Helper: Get risk level badge color
   * @param {string} riskLevel - Risk level
   */
  getRiskColor(riskLevel) {
    const colorMap = {
      'safe': '#28a745',      // Green
      'low': '#17a2b8',       // Cyan
      'medium': '#ffc107',    // Yellow
      'high': '#fd7e14',      // Orange
      'critical': '#dc3545'   // Red
    }
    return colorMap[riskLevel.toLowerCase()] || '#6c757d'
  }
}
