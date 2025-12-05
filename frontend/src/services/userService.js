/**
 * User Management Service
 * Handles user CRUD operations, role management, and permissions
 */
import { httpClient } from './httpClient';

const API_BASE = '/api/v1/admin';

/**
 * Get all users with optional filtering
 */
export const getUsers = async (params = {}) => {
  const { skip = 0, limit = 100, role = null, is_active = null } = params;
  
  const queryParams = new URLSearchParams({ skip, limit });
  if (role) queryParams.append('role', role);
  if (is_active !== null) queryParams.append('is_active', is_active);
  
  const response = await httpClient.get(`${API_BASE}/users?${queryParams}`);
  return response;
};

/**
 * Get a specific user by ID
 */
export const getUserById = async (userId) => {
  const response = await httpClient.get(`${API_BASE}/users/${userId}`);
  return response;
};

/**
 * Update user role
 */
export const updateUserRole = async (userId, role) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}/role`, { role });
  return response;
};

/**
 * Update user status (activate/deactivate)
 */
export const updateUserStatus = async (userId, isActive) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}/status`, { 
    is_active: isActive 
  });
  return response;
};

/**
 * Get all available roles and their permissions
 */
export const getRoles = async () => {
  const response = await httpClient.get(`${API_BASE}/roles`);
  return response;
};

export default {
  getUsers,
  getUserById,
  updateUserRole,
  updateUserStatus,
  getRoles
};
