/**
 * API Configuration
 * Centralized configuration for backend API endpoints
 * Supports environment-based URL configuration for AWS deployment
 */

// Get API URL from environment variable or default to localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// API endpoint paths
export const API_ENDPOINTS = {
  // Animal endpoints
  ANIMAL_LIST: '/animal_list',
  ANIMAL_BY_ID: (id: string) => `/animal/${id}`,
  ANIMAL_CONFIG: '/animal_config',

  // Family endpoints
  FAMILY: '/family',
  FAMILY_BY_ID: (id: string) => `/family/${id}`,

  // Chat/Conversation endpoints
  CHAT: '/chat',
  CHAT_HISTORY: '/chat_history',
  CONVO_TURN: '/convo_turn',

  // Auth endpoints
  AUTH_LOGIN: '/auth/login',
  AUTH_LOGOUT: '/auth/logout',

  // User endpoints
  USER: '/user',
  USER_BY_ID: (id: string) => `/user/${id}`,
} as const;

/**
 * Build full API URL
 * @param endpoint - API endpoint path (use API_ENDPOINTS constants)
 * @param queryParams - Optional query parameters
 */
export function buildApiUrl(endpoint: string, queryParams?: Record<string, string>): string {
  const url = new URL(endpoint, API_BASE_URL);

  if (queryParams) {
    Object.entries(queryParams).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  return url.toString();
}

/**
 * Get authentication headers
 * @param userId - Optional user ID for X-User-Id header
 */
export function getAuthHeaders(userId?: string): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Get userId from localStorage if not provided
  const currentUser = userId || localStorage.getItem('currentUser');
  if (currentUser) {
    try {
      const user = JSON.parse(currentUser);
      headers['X-User-Id'] = user.userId || currentUser;
    } catch {
      headers['X-User-Id'] = currentUser;
    }
  } else {
    // Fallback to admin user for testing
    headers['X-User-Id'] = '4fd19775-68bc-470e-a5d4-ceb70552c8d7';
  }

  return headers;
}
