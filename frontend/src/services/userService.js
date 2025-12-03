import { httpClient } from './httpClient'

/**
 * User Management Service (Admin only)
 * Handles all user management API calls
 */
export const userService = {
  /**
   * Get all users (admin only)
   */
  async getAllUsers() {
    return httpClient.get('/api/v1/users')
  },

  /**
   * Create new user (admin only)
   * @param {Object} userData - User data
   * @param {string} userData.email - User email
   * @param {string} userData.name - User full name
   * @param {string} userData.password - User password
   * @param {string} userData.tier - User tier (contractor, staff, manager, admin)
   */
  async createUser(userData) {
    return httpClient.post('/api/v1/users', userData)
  },

  /**
   * Update user (admin only)
   * @param {number} userId - User ID
   * @param {Object} updateData - Data to update
   */
  async updateUser(userId, updateData) {
    return httpClient.put(`/api/v1/users/${userId}`, updateData)
  },

  /**
   * Toggle user active status (admin only)
   * @param {number} userId - User ID
   * @param {boolean} isActive - Active status
   */
  async toggleUserStatus(userId, isActive) {
    return httpClient.patch(`/api/v1/users/${userId}/status`, { is_active: isActive })
  },

  /**
   * Delete user (admin only)
   * @param {number} userId - User ID
   */
  async deleteUser(userId) {
    return httpClient.delete(`/api/v1/users/${userId}`)
  }
}
