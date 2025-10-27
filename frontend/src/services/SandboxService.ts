/**
 * SandboxService API Client
 *
 * Provides methods for interacting with sandbox assistant endpoints.
 * Handles authentication, error handling, and data transformation.
 *
 * Features:
 * - Create, list, retrieve, and delete sandbox assistants
 * - Test conversations with sandbox configurations
 * - Promote sandbox configurations to live assistants
 * - Automatic token management and error handling
 *
 * T047 - User Story 2: Test Assistant Changes Safely
 */

import { ApiClient } from './ApiClient';

// Types
export interface CreateSandboxRequest {
  animalId?: string;
  personalityId: string;
  guardrailId: string;
  knowledgeBaseFileIds?: string[];
}

export interface SandboxResponse {
  sandboxId: string;
  animalId?: string;
  personalityId: string;
  guardrailId: string;
  knowledgeBaseFileIds?: string[];
  createdBy: string;
  expiresAt: string;
  conversationCount: number;
  lastConversationAt?: string;
  isPromoted: boolean;
  promotedAt?: string;
  created: {
    at: string;
    by: string;
  };
  modified?: {
    at: string;
    by: string;
  };
}

export interface SandboxListResponse {
  sandboxes: SandboxResponse[];
}

export interface ChatRequest {
  message: string;
  context?: {
    userId?: string;
    sessionId?: string;
  };
}

export interface ChatResponse {
  response: string;
  conversationId: string;
  usage?: {
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  };
  metadata?: {
    model?: string;
    personality?: string;
    guardrails?: string[];
    isSandbox?: boolean;
    sandboxId?: string;
  };
}

export interface PromoteSandboxRequest {
  // Currently no additional fields required
}

export interface PromoteSandboxResponse {
  message: string;
  sandboxId: string;
  assistantId: string;
  promotedAt: string;
}

export interface DeleteSandboxResponse {
  message: string;
  sandboxId: string;
}

/**
 * Service for sandbox assistant management
 */
export class SandboxService {
  private static readonly BASE_PATH = '/api/sandbox';

  /**
   * Create a new sandbox assistant
   */
  static async createSandbox(request: CreateSandboxRequest): Promise<SandboxResponse> {
    try {
      const response = await ApiClient.post<SandboxResponse>(
        this.BASE_PATH,
        request
      );

      return response;
    } catch (error) {
      console.error('Error creating sandbox:', error);
      throw this.handleError(error, 'Failed to create sandbox assistant');
    }
  }

  /**
   * List all active sandbox assistants
   */
  static async listSandboxes(filters?: {
    userId?: string;
    assistantId?: string;
  }): Promise<SandboxListResponse> {
    try {
      const queryParams = new URLSearchParams();

      if (filters?.userId) {
        queryParams.append('userId', filters.userId);
      }
      if (filters?.assistantId) {
        queryParams.append('assistantId', filters.assistantId);
      }

      const url = queryParams.toString()
        ? `${this.BASE_PATH}?${queryParams}`
        : this.BASE_PATH;

      const response = await ApiClient.get<SandboxListResponse>(url);

      return response;
    } catch (error) {
      console.error('Error listing sandboxes:', error);
      throw this.handleError(error, 'Failed to load sandbox list');
    }
  }

  /**
   * Get sandbox assistant details by ID
   */
  static async getSandbox(sandboxId: string): Promise<SandboxResponse> {
    try {
      const response = await ApiClient.get<SandboxResponse>(
        `${this.BASE_PATH}/${sandboxId}`
      );

      return response;
    } catch (error) {
      console.error('Error getting sandbox:', error);

      if (error instanceof Error && error.message.includes('404')) {
        throw new Error('Sandbox not found or may have expired');
      }
      if (error instanceof Error && error.message.includes('410')) {
        throw new Error('Sandbox has expired');
      }

      throw this.handleError(error, 'Failed to load sandbox details');
    }
  }

  /**
   * Test conversation with sandbox assistant
   */
  static async testSandboxChat(
    sandboxId: string,
    chatRequest: ChatRequest
  ): Promise<ChatResponse> {
    try {
      const response = await ApiClient.post<ChatResponse>(
        `${this.BASE_PATH}/${sandboxId}/chat`,
        chatRequest
      );

      return response;
    } catch (error) {
      console.error('Error testing sandbox chat:', error);

      if (error instanceof Error && error.message.includes('404')) {
        throw new Error('Sandbox not found or may have expired');
      }
      if (error instanceof Error && error.message.includes('410')) {
        throw new Error('Sandbox has expired');
      }

      throw this.handleError(error, 'Failed to get AI response');
    }
  }

  /**
   * Promote sandbox configuration to live assistant
   */
  static async promoteSandbox(
    sandboxId: string,
    request?: PromoteSandboxRequest
  ): Promise<PromoteSandboxResponse> {
    try {
      const response = await ApiClient.post<PromoteSandboxResponse>(
        `${this.BASE_PATH}/${sandboxId}/promote`,
        request || {}
      );

      return response;
    } catch (error) {
      console.error('Error promoting sandbox:', error);

      if (error instanceof Error && error.message.includes('404')) {
        throw new Error('Sandbox not found or may have expired');
      }
      if (error instanceof Error && error.message.includes('410')) {
        throw new Error('Sandbox has expired');
      }
      if (error instanceof Error && error.message.includes('409')) {
        throw new Error('Sandbox has already been promoted');
      }

      throw this.handleError(error, 'Failed to promote sandbox to live assistant');
    }
  }

  /**
   * Delete sandbox assistant
   */
  static async deleteSandbox(sandboxId: string): Promise<DeleteSandboxResponse> {
    try {
      const response = await ApiClient.delete<DeleteSandboxResponse>(
        `${this.BASE_PATH}/${sandboxId}`
      );

      return response;
    } catch (error) {
      console.error('Error deleting sandbox:', error);

      if (error instanceof Error && error.message.includes('404')) {
        throw new Error('Sandbox not found or may have expired');
      }

      throw this.handleError(error, 'Failed to delete sandbox');
    }
  }

  /**
   * Check if sandbox is expired based on expiresAt timestamp
   */
  static isExpired(expiresAt: string): boolean {
    const now = new Date();
    const expires = new Date(expiresAt);
    return now >= expires;
  }

  /**
   * Calculate time remaining in milliseconds
   */
  static getTimeRemaining(expiresAt: string): number {
    const now = new Date();
    const expires = new Date(expiresAt);
    return Math.max(0, expires.getTime() - now.getTime());
  }

  /**
   * Format time remaining as MM:SS
   */
  static formatTimeRemaining(expiresAt: string): string {
    const remaining = this.getTimeRemaining(expiresAt);

    if (remaining === 0) {
      return 'Expired';
    }

    const totalSeconds = Math.floor(remaining / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  /**
   * Get TTL progress percentage (0-100)
   */
  static getTTLProgress(expiresAt: string): number {
    const totalDuration = 30 * 60 * 1000; // 30 minutes in milliseconds
    const remaining = this.getTimeRemaining(expiresAt);
    const elapsed = totalDuration - remaining;

    return Math.min(100, Math.max(0, (elapsed / totalDuration) * 100));
  }

  /**
   * Determine sandbox status based on conversations and expiry
   */
  static getSandboxStatus(sandbox: SandboxResponse): 'draft' | 'tested' | 'expired' {
    if (this.isExpired(sandbox.expiresAt)) {
      return 'expired';
    }

    if (sandbox.conversationCount > 0) {
      return 'tested';
    }

    return 'draft';
  }

  /**
   * Validate sandbox creation request
   */
  static validateCreateRequest(request: CreateSandboxRequest): string[] {
    const errors: string[] = [];

    if (!request.personalityId?.trim()) {
      errors.push('Personality is required');
    }

    if (!request.guardrailId?.trim()) {
      errors.push('Guardrail is required');
    }

    if (request.knowledgeBaseFileIds && request.knowledgeBaseFileIds.length > 10) {
      errors.push('Maximum 10 knowledge base files allowed');
    }

    return errors;
  }

  /**
   * Validate chat request
   */
  static validateChatRequest(request: ChatRequest): string[] {
    const errors: string[] = [];

    if (!request.message?.trim()) {
      errors.push('Message is required');
    }

    if (request.message && request.message.length > 4000) {
      errors.push('Message too long (maximum 4000 characters)');
    }

    return errors;
  }

  /**
   * Handle API errors with user-friendly messages
   */
  private static handleError(error: unknown, defaultMessage: string): Error {
    if (error instanceof Error) {
      // Check for specific API error messages
      if (error.message.includes('validation')) {
        return new Error('Invalid request data. Please check your input.');
      }

      if (error.message.includes('unauthorized') || error.message.includes('401')) {
        return new Error('Authentication required. Please log in again.');
      }

      if (error.message.includes('forbidden') || error.message.includes('403')) {
        return new Error('You do not have permission to perform this action.');
      }

      if (error.message.includes('rate limit')) {
        return new Error('Too many requests. Please wait a moment and try again.');
      }

      if (error.message.includes('500')) {
        return new Error('Server error. Please try again later.');
      }

      // Return original error message if it's descriptive
      if (error.message.length > 10 && error.message.length < 200) {
        return error;
      }
    }

    return new Error(defaultMessage);
  }
}

// Export types for use in components
export type {
  CreateSandboxRequest,
  SandboxResponse,
  SandboxListResponse,
  ChatRequest,
  ChatResponse,
  PromoteSandboxRequest,
  PromoteSandboxResponse,
  DeleteSandboxResponse
};