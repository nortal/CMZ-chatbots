/**
 * API Service Layer for CMZ Backend Integration
 * 
 * Provides functions to interact with the hexagonal architecture backend
 * running on localhost:8080
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Types matching our backend OpenAPI schema
export interface Animal {
  animalId?: string;
  name: string;
  species: string;
  status: 'active' | 'inactive' | 'hidden';
  softDelete?: boolean;
  created?: {
    at: string;
    by: {
      actorId: string;
      email: string;
      displayName: string;
    };
  };
  modified?: {
    at: string;
    by: {
      actorId: string;
      email: string;
      displayName: string;
    };
  };
}

export interface AnimalConfig {
  animalConfigId?: string;
  voice?: string;
  personality?: string;
  aiModel?: string;
  temperature?: number;
  topP?: number;
  toolsEnabled?: string[];
  guardrails?: Record<string, unknown>;
  created?: {
    at: string;
    by: {
      actorId: string;
      email: string;
      displayName: string;
    };
  };
  modified?: {
    at: string;
    by: {
      actorId: string;
      email: string;
      displayName: string;
    };
  };
}

/**
 * Generic API request handler with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        errorData.message || 
        `API Error: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Unable to connect to API server');
    }
    throw new Error('API request failed: Unknown error occurred');
  }
}

// Animal API Functions
export const animalApi = {
  /**
   * Get list of all animals
   */
  async listAnimals(): Promise<Animal[]> {
    return apiRequest<Animal[]>('/animal_list');
  },

  /**
   * Get animal details by ID
   */
  async getAnimalDetails(animalId: string): Promise<Animal> {
    if (!animalId?.trim()) {
      throw new Error('Animal ID is required');
    }
    return apiRequest<Animal>(`/animal_details?animalId=${encodeURIComponent(animalId)}`);
  },

  /**
   * Get animal configuration by ID
   */
  async getAnimalConfig(animalId: string): Promise<AnimalConfig> {
    if (!animalId?.trim()) {
      throw new Error('Animal ID is required');
    }
    return apiRequest<AnimalConfig>(`/animal_config?animalId=${encodeURIComponent(animalId)}`);
  },

  /**
   * Update animal configuration
   */
  async updateAnimalConfig(animalId: string, config: Partial<AnimalConfig>): Promise<AnimalConfig> {
    if (!animalId?.trim()) {
      throw new Error('Animal ID is required');
    }
    if (!config || Object.keys(config).length === 0) {
      throw new Error('Configuration updates are required');
    }
    return apiRequest<AnimalConfig>(`/animal_config?animalId=${encodeURIComponent(animalId)}`, {
      method: 'PATCH',
      body: JSON.stringify(config),
    });
  },
};

// Utility functions
export const utils = {
  /**
   * Check if API is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      await apiRequest('/');
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Convert backend Animal to frontend format
   */
  transformAnimalForFrontend(backendAnimal: Animal) {
    return {
      id: backendAnimal.animalId || 'unknown',
      name: backendAnimal.name,
      species: backendAnimal.species,
      active: backendAnimal.status === 'active',
      lastUpdated: backendAnimal.modified?.at || 'Unknown',
      conversations: 0, // Not available from backend yet
    };
  },

  /**
   * Convert frontend config to backend format
   */
  transformConfigForBackend(frontendConfig: any): Partial<AnimalConfig> {
    return {
      personality: frontendConfig.personality,
      voice: frontendConfig.voiceSettings?.tone || 'default',
      aiModel: 'claude-3-sonnet', // Default model
      temperature: frontendConfig.conversationSettings?.enthusiasm || 0.7,
      topP: 1.0,
      toolsEnabled: [],
      guardrails: frontendConfig.guardrails || {},
    };
  },
};

export default animalApi;