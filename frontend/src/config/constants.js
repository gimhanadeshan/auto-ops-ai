// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
}

// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh'
  },
  
  // Chat endpoints
  CHAT: {
    SEND_MESSAGE: '/api/chat',
    GET_HISTORY: '/api/chat/history'
  },
  
  // Ticket endpoints
  TICKETS: {
    GET_ALL: '/api/tickets',
    GET_BY_ID: (id) => `/api/tickets/${id}`,
    CREATE: '/api/tickets',
    UPDATE: (id) => `/api/tickets/${id}`,
    DELETE: (id) => `/api/tickets/${id}`
  },
  
  // Dashboard endpoints
  DASHBOARD: {
    STATS: '/api/dashboard/stats',
    RECENT_ISSUES: '/api/dashboard/recent-issues'
  },
  
  // Monitoring endpoints
  MONITORING: {
    SYSTEM_METRICS: '/api/monitoring/metrics',
    SERVICES: '/api/monitoring/services',
    LOGS: '/api/monitoring/logs'
  },
  
  // Reports endpoints
  REPORTS: {
    GENERATE: '/api/reports',
    EXPORT: '/api/reports/export'
  },
  
  // Status endpoint
  STATUS: '/api/status'
}

// Route Paths
export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CHAT: '/chat',
  TICKETS: '/tickets',
  MONITORING: '/monitoring',
  REPORTS: '/reports',
  AUTOMATION: '/automation',
  KNOWLEDGE_BASE: '/knowledge-base',
  SETTINGS: '/settings',
  ROOT: '/'
}

// Theme Colors (used as fallback)
export const COLORS = {
  // Primary colors
  primary: {
    50: '#f0fdfa',
    100: '#ccfbf1',
    200: '#99f6e4',
    300: '#5eead4',
    400: '#2dd4bf',
    500: '#14b8a6',
    600: '#0d9488',
    700: '#0f766e',
    800: '#115e59',
    900: '#134e4a'
  },
  
  // Status colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  
  // Neutral colors (dark theme)
  dark: {
    bg: '#0f0f1a',
    bgSecondary: '#1a1a2e',
    bgTertiary: '#16213e',
    border: 'rgba(20, 184, 166, 0.2)',
    text: '#e5e7eb',
    textSecondary: '#9ca3af',
    textMuted: '#6b7280'
  },
  
  // Light colors (light theme)
  light: {
    bg: '#ffffff',
    bgSecondary: '#f9fafb',
    bgTertiary: '#f3f4f6',
    border: 'rgba(107, 114, 128, 0.2)',
    text: '#111827',
    textSecondary: '#4b5563',
    textMuted: '#9ca3af'
  }
}

// Application Settings
export const APP_SETTINGS = {
  APP_NAME: 'Auto-Ops-AI',
  APP_TAGLINE: 'AI-powered IT Support Assistant',
  VERSION: '1.0.0',
  DEFAULT_THEME: 'dark',
  
  // Pagination
  ITEMS_PER_PAGE: 20,
  
  // Chat settings
  MAX_MESSAGE_LENGTH: 2000,
  TYPING_INDICATOR_DELAY: 1000,
  
  // Notification settings
  NOTIFICATION_DURATION: 5000,
  
  // File upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['image/png', 'image/jpeg', 'application/pdf']
}

// Ticket Status
export const TICKET_STATUS = {
  OPEN: 'open',
  IN_PROGRESS: 'in-progress',
  RESOLVED: 'resolved',
  CLOSED: 'closed',
  ESCALATED: 'escalated'
}

// Ticket Priority
export const TICKET_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
}

// User Roles
export const USER_ROLES = {
  ADMIN: 'admin',
  TECHNICIAN: 'technician',
  USER: 'user',
  GUEST: 'guest'
}

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_DATA: 'user',
  THEME: 'theme',
  LANGUAGE: 'language'
}

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  AUTH_ERROR: 'Authentication failed. Please login again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.'
}

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  LOGOUT_SUCCESS: 'Successfully logged out!',
  TICKET_CREATED: 'Ticket created successfully!',
  TICKET_UPDATED: 'Ticket updated successfully!',
  SETTINGS_SAVED: 'Settings saved successfully!'
}
