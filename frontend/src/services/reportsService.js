import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Reports Service
 * Handles report generation and export
 */
export const reportsService = {
  /**
   * Generate report
   * @param {Object} params - Report parameters
   */
  async generate(params = {}) {
    return httpClient.post(API_ENDPOINTS.REPORTS.GENERATE, params)
  },

  /**
   * Export report
   * @param {string} format - Export format (pdf, csv, xlsx)
   * @param {Object} params - Export parameters
   */
  async export(format, params = {}) {
    return httpClient.post(API_ENDPOINTS.REPORTS.EXPORT, {
      format,
      ...params
    })
  }
}
