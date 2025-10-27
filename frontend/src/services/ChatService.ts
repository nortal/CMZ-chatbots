/**
 * ChatService - POST Polling Implementation for Lambda Compatibility
 *
 * Replaces Server-Sent Events (SSE) streaming with synchronous POST requests
 * to enable AWS Lambda deployment and load balancer compatibility.
 *
 * Key Features:
 * - Synchronous POST request/response pattern
 * - Session management with localStorage persistence
 * - Error handling with retry logic
 * - Lambda-compatible timeouts (30 seconds)
 * - Load balancer friendly (stateless)
 */

import {
  ChatRequest,
  ChatResponse,
  ChatError,
  ConnectionStatus,
  ChatConfig
} from '../types/chat';

export class ChatService {
  private config: ChatConfig;
  private currentSessionId: string | null = null;

  constructor(config?: Partial<ChatConfig>) {
    this.config = {
      apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8080',
      timeout: 30000, // 30 seconds for Lambda compatibility
      maxRetries: 3,
      retryDelay: 1000,
      ...config
    };

    // Restore session from localStorage if available
    this.restoreSession();
  }

  /**
   * Send a message and receive complete response via POST /convo_turn
   * Replaces SSE streaming with synchronous request/response
   */
  async sendMessage(
    message: string,
    animalId: string,
    sessionId?: string
  ): Promise<ChatResponse> {
    const effectiveSessionId = sessionId || this.currentSessionId;

    // Backend expects: message, animalId, sessionId, userId
    const request = {
      message: message.trim(),
      animalId,
      sessionId: effectiveSessionId || `session_${Date.now()}`,
      userId: 'frontend_user'
    };

    try {
      const response = await this.makeRequest('/convo_turn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw await this.createErrorFromResponse(response);
      }

      const backendResponse = await response.json();

      // Transform backend response format to frontend ChatResponse format
      const chatResponse: ChatResponse = {
        reply: backendResponse.response || backendResponse.reply || 'No response received',
        sessionId: backendResponse.conversationId || backendResponse.sessionId || 'unknown',
        turnId: backendResponse.turnId || `${Date.now()}`,
        timestamp: backendResponse.timestamp || new Date().toISOString(),
        metadata: {
          animalId: backendResponse.animalId || animalId,
          annotations: [],
          hasKnowledge: false,
          tokens: undefined,
          model: undefined,
          latencyMs: undefined
        }
      };

      // Update session ID for continuity
      if (chatResponse.sessionId) {
        this.setSessionId(chatResponse.sessionId);
      }

      return chatResponse;

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw this.createTimeoutError();
      }
      throw error;
    }
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.currentSessionId;
  }

  /**
   * Set session ID and persist to localStorage
   */
  setSessionId(sessionId: string): void {
    this.currentSessionId = sessionId;
    localStorage.setItem('cmz_chat_session', sessionId);
  }

  /**
   * Reset current session and clear localStorage
   */
  resetSession(): void {
    this.currentSessionId = null;
    localStorage.removeItem('cmz_chat_session');
  }

  /**
   * Check backend health and return connection status
   */
  async checkConnection(): Promise<ConnectionStatus> {
    try {
      const response = await this.makeRequest('/system_health', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      return response.ok ? 'connected' : 'error';
    } catch (error) {
      console.error('Connection check failed:', error);
      return 'disconnected';
    }
  }

  /**
   * Get conversation history for current session
   */
  async getConversationHistory(sessionId?: string): Promise<any> {
    const effectiveSessionId = sessionId || this.currentSessionId;

    if (!effectiveSessionId) {
      throw new Error('No session ID available for history retrieval');
    }

    const response = await this.makeRequest(
      `/convo_history?sessionId=${encodeURIComponent(effectiveSessionId)}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      }
    );

    if (!response.ok) {
      throw await this.createErrorFromResponse(response);
    }

    return response.json();
  }

  /**
   * Delete conversation history
   */
  async deleteConversation(sessionId?: string): Promise<void> {
    const effectiveSessionId = sessionId || this.currentSessionId;

    if (!effectiveSessionId) {
      throw new Error('No session ID available for deletion');
    }

    const response = await this.makeRequest(
      `/convo_history?sessionId=${encodeURIComponent(effectiveSessionId)}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      }
    );

    if (!response.ok && response.status !== 404) {
      throw await this.createErrorFromResponse(response);
    }

    // Clear session if we deleted current conversation
    if (effectiveSessionId === this.currentSessionId) {
      this.resetSession();
    }
  }

  // Private helper methods

  private async makeRequest(
    endpoint: string,
    options: RequestInit,
    retryCount = 0
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(`${this.config.apiUrl}${endpoint}`, {
        ...options,
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response;

    } catch (error) {
      clearTimeout(timeoutId);

      // Retry logic for network errors
      if (retryCount < this.config.maxRetries! && this.shouldRetry(error)) {
        await this.delay(this.config.retryDelay! * (retryCount + 1));
        return this.makeRequest(endpoint, options, retryCount + 1);
      }

      throw error;
    }
  }

  private shouldRetry(error: unknown): boolean {
    if (error instanceof Error) {
      // Retry on network errors but not on timeout
      return error.name === 'TypeError' && error.message.includes('fetch');
    }
    return false;
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async createErrorFromResponse(response: Response): Promise<ChatError> {
    let message = 'Unknown error occurred';
    let type: ChatError['type'] = 'server';

    try {
      const errorData = await response.json();
      message = errorData.message || errorData.detail || message;
    } catch {
      message = response.statusText || message;
    }

    // Classify error type based on status code
    if (response.status === 401 || response.status === 403) {
      type = 'auth';
    } else if (response.status === 400) {
      type = 'validation';
    } else if (response.status === 429) {
      type = 'rate_limit';
    } else if (response.status >= 500) {
      type = 'server';
    }

    return {
      message,
      status: response.status,
      type,
      details: {
        code: response.status.toString()
      }
    };
  }

  private createTimeoutError(): ChatError {
    return {
      message: 'Request timed out. Please try again.',
      status: 408,
      type: 'network',
      details: {
        code: 'TIMEOUT'
      }
    };
  }

  private getAuthToken(): string {
    // Try multiple token storage keys for compatibility
    return localStorage.getItem('authToken') ||
           localStorage.getItem('cmz_token') ||
           '';
  }

  private restoreSession(): void {
    const savedSession = localStorage.getItem('cmz_chat_session');
    if (savedSession) {
      this.currentSessionId = savedSession;
    }
  }
}

// Export singleton instance for convenience
export const chatService = new ChatService();

// Export class for custom configurations
export default ChatService;