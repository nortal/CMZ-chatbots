/**
 * Assistant Service API Client
 *
 * Provides API communication for Animal Assistant Management System
 * Handles CRUD operations for assistants, personalities, and guardrails
 *
 * T030 - User Story 1: Create and Deploy Live Animal Assistant
 */

import {
  AnimalAssistant,
  Personality,
  Guardrail,
  CreateAssistantRequest,
  UpdateAssistantRequest,
  CreatePersonalityRequest,
  CreateGuardrailRequest,
  Animal,
  ApiResponse
} from '../types/AssistantTypes';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Token management from existing API service
const TOKEN_KEY = 'cmz_auth_token';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Generic API request handler with error handling
 */
async function assistantApiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        ...headers,
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error ||
        errorData.message ||
        `API Error: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Assistant API request failed: Unknown error occurred');
  }
}

/**
 * Assistant Management API
 */
export const assistantApi = {
  /**
   * Create a new animal assistant
   */
  async createAssistant(data: CreateAssistantRequest): Promise<AnimalAssistant> {
    return assistantApiRequest<AnimalAssistant>('/assistants', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get assistant by ID
   */
  async getAssistant(assistantId: string): Promise<AnimalAssistant> {
    if (!assistantId?.trim()) {
      throw new Error('Assistant ID is required');
    }
    return assistantApiRequest<AnimalAssistant>(`/assistants/${encodeURIComponent(assistantId)}`);
  },

  /**
   * Update existing assistant
   */
  async updateAssistant(assistantId: string, data: UpdateAssistantRequest): Promise<AnimalAssistant> {
    if (!assistantId?.trim()) {
      throw new Error('Assistant ID is required');
    }
    return assistantApiRequest<AnimalAssistant>(`/assistants/${encodeURIComponent(assistantId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete assistant
   */
  async deleteAssistant(assistantId: string): Promise<void> {
    if (!assistantId?.trim()) {
      throw new Error('Assistant ID is required');
    }
    return assistantApiRequest<void>(`/assistants/${encodeURIComponent(assistantId)}`, {
      method: 'DELETE',
    });
  },

  /**
   * List all assistants
   */
  async listAssistants(): Promise<{ assistants: AnimalAssistant[] }> {
    return assistantApiRequest<{ assistants: AnimalAssistant[] }>('/assistants');
  },

  /**
   * Get assistant by animal ID
   */
  async getAssistantByAnimal(animalId: string): Promise<AnimalAssistant> {
    if (!animalId?.trim()) {
      throw new Error('Animal ID is required');
    }
    return assistantApiRequest<AnimalAssistant>(`/assistants/by-animal/${encodeURIComponent(animalId)}`);
  },

  /**
   * Refresh assistant prompt (regenerate merged prompt)
   */
  async refreshAssistantPrompt(assistantId: string): Promise<AnimalAssistant> {
    if (!assistantId?.trim()) {
      throw new Error('Assistant ID is required');
    }
    return assistantApiRequest<AnimalAssistant>(`/assistants/${encodeURIComponent(assistantId)}/refresh`, {
      method: 'POST',
    });
  },
};

/**
 * Personality Management API
 */
export const personalityApi = {
  /**
   * Create a new personality
   */
  async createPersonality(data: CreatePersonalityRequest): Promise<Personality> {
    return assistantApiRequest<Personality>('/personalities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get personality by ID
   */
  async getPersonality(personalityId: string): Promise<Personality> {
    if (!personalityId?.trim()) {
      throw new Error('Personality ID is required');
    }
    return assistantApiRequest<Personality>(`/personalities/${encodeURIComponent(personalityId)}`);
  },

  /**
   * Update existing personality
   */
  async updatePersonality(personalityId: string, data: CreatePersonalityRequest): Promise<Personality> {
    if (!personalityId?.trim()) {
      throw new Error('Personality ID is required');
    }
    return assistantApiRequest<Personality>(`/personalities/${encodeURIComponent(personalityId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete personality
   */
  async deletePersonality(personalityId: string): Promise<void> {
    if (!personalityId?.trim()) {
      throw new Error('Personality ID is required');
    }
    return assistantApiRequest<void>(`/personalities/${encodeURIComponent(personalityId)}`, {
      method: 'DELETE',
    });
  },

  /**
   * List all personalities
   */
  async listPersonalities(): Promise<{ personalities: Personality[] }> {
    return assistantApiRequest<{ personalities: Personality[] }>('/personalities');
  },
};

/**
 * Guardrail Management API
 */
export const guardrailApi = {
  /**
   * Create a new guardrail
   */
  async createGuardrail(data: CreateGuardrailRequest): Promise<Guardrail> {
    return assistantApiRequest<Guardrail>('/guardrails', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get guardrail by ID
   */
  async getGuardrail(guardrailId: string): Promise<Guardrail> {
    if (!guardrailId?.trim()) {
      throw new Error('Guardrail ID is required');
    }
    return assistantApiRequest<Guardrail>(`/guardrails/${encodeURIComponent(guardrailId)}`);
  },

  /**
   * Update existing guardrail
   */
  async updateGuardrail(guardrailId: string, data: CreateGuardrailRequest): Promise<Guardrail> {
    if (!guardrailId?.trim()) {
      throw new Error('Guardrail ID is required');
    }
    return assistantApiRequest<Guardrail>(`/guardrails/${encodeURIComponent(guardrailId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete guardrail
   */
  async deleteGuardrail(guardrailId: string): Promise<void> {
    if (!guardrailId?.trim()) {
      throw new Error('Guardrail ID is required');
    }
    return assistantApiRequest<void>(`/guardrails/${encodeURIComponent(guardrailId)}`, {
      method: 'DELETE',
    });
  },

  /**
   * List all guardrails
   */
  async listGuardrails(): Promise<{ guardrails: Guardrail[] }> {
    return assistantApiRequest<{ guardrails: Guardrail[] }>('/guardrails');
  },
};

/**
 * Helper functions for assistant management
 */
export const assistantUtils = {
  /**
   * Validate assistant creation data
   */
  validateAssistantData(data: CreateAssistantRequest): string[] {
    const errors: string[] = [];

    if (!data.animalId?.trim()) {
      errors.push('Animal ID is required');
    }
    if (!data.personalityId?.trim()) {
      errors.push('Personality ID is required');
    }
    if (!data.guardrailId?.trim()) {
      errors.push('Guardrail ID is required');
    }
    if (data.knowledgeBaseFileIds && data.knowledgeBaseFileIds.length > 50) {
      errors.push('Maximum of 50 knowledge base files allowed');
    }

    return errors;
  },

  /**
   * Validate personality creation data
   */
  validatePersonalityData(data: CreatePersonalityRequest): string[] {
    const errors: string[] = [];

    if (!data.name?.trim()) {
      errors.push('Personality name is required');
    }
    if (data.name && (data.name.length < 1 || data.name.length > 100)) {
      errors.push('Personality name must be 1-100 characters');
    }
    if (!data.description?.trim()) {
      errors.push('Description is required');
    }
    if (data.description && (data.description.length < 1 || data.description.length > 500)) {
      errors.push('Description must be 1-500 characters');
    }
    if (!data.personalityText?.trim()) {
      errors.push('Personality text is required');
    }
    if (data.personalityText && (data.personalityText.length < 100 || data.personalityText.length > 5000)) {
      errors.push('Personality text must be 100-5000 characters');
    }

    return errors;
  },

  /**
   * Validate guardrail creation data
   */
  validateGuardrailData(data: CreateGuardrailRequest): string[] {
    const errors: string[] = [];

    if (!data.name?.trim()) {
      errors.push('Guardrail name is required');
    }
    if (data.name && (data.name.length < 1 || data.name.length > 100)) {
      errors.push('Guardrail name must be 1-100 characters');
    }
    if (!data.description?.trim()) {
      errors.push('Description is required');
    }
    if (data.description && (data.description.length < 1 || data.description.length > 500)) {
      errors.push('Description must be 1-500 characters');
    }
    if (!data.guardrailText?.trim()) {
      errors.push('Guardrail text is required');
    }
    if (data.guardrailText && (data.guardrailText.length < 50 || data.guardrailText.length > 2000)) {
      errors.push('Guardrail text must be 50-2000 characters');
    }

    return errors;
  },

  /**
   * Format assistant for display
   */
  formatAssistantForDisplay(assistant: AnimalAssistant) {
    return {
      ...assistant,
      statusDisplay: assistant.status === 'ACTIVE' ? 'Active' :
                    assistant.status === 'INACTIVE' ? 'Inactive' : 'Error',
      lastUpdated: new Date(assistant.modified.at).toLocaleDateString(),
      promptLength: assistant.mergedPrompt.length,
      knowledgeFileCount: assistant.knowledgeBaseFileIds.length,
    };
  },
};

export default assistantApi;