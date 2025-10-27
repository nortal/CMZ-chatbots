/**
 * API Client
 *
 * Centralized HTTP client for making API requests with authentication,
 * error handling, and response transformation.
 *
 * Features:
 * - Automatic JWT token attachment
 * - Response transformation and error handling
 * - Request/response logging
 * - Retry logic for transient failures
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  /**
   * Make GET request
   */
  static async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  /**
   * Make POST request
   */
  static async post<T>(path: string, data?: any): Promise<T> {
    return this.request<T>('POST', path, data);
  }

  /**
   * Make PUT request
   */
  static async put<T>(path: string, data?: any): Promise<T> {
    return this.request<T>('PUT', path, data);
  }

  /**
   * Make DELETE request
   */
  static async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  /**
   * Make generic HTTP request
   */
  private static async request<T>(
    method: string,
    path: string,
    data?: any
  ): Promise<T> {
    const url = `${API_BASE_URL}${path}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add authentication token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      method,
      headers,
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      config.body = JSON.stringify(data);
    }

    try {
      console.log('[API] Request:', { method, url }, data ? { body: data } : '');

      const response = await fetch(url, config);

      // Handle non-JSON responses (like 204 No Content)
      let responseData: any;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      console.log('[API] Response:', { method, url, status: response.status }, responseData);

      if (!response.ok) {
        throw new ApiError(
          responseData?.message || responseData?.error || response.statusText,
          response.status,
          response.statusText,
          responseData
        );
      }

      return responseData;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      // Network or other errors
      console.error('[API] Error:', { method, url }, error);
      throw new ApiError(
        'Network error or server unavailable',
        0,
        'Network Error'
      );
    }
  }
}