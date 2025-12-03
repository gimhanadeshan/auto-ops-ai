import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Monitoring Service
 * Handles all system monitoring API calls
 */
export const monitoringService = {
  /**
   * Get system metrics
   */
  async getMetrics() {
    return httpClient.get(API_ENDPOINTS.MONITORING.SYSTEM_METRICS)
  },

  /**
   * Get services status
   */
  async getServices() {
    return httpClient.get(API_ENDPOINTS.MONITORING.SERVICES)
  },

  /**
   * Get system logs
   * @param {Object} params - Query parameters
   */
  async getLogs(params = {}) {
    return httpClient.get(API_ENDPOINTS.MONITORING.LOGS, params)
  }
}
