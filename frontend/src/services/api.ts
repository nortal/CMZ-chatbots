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
  systemPrompt?: string;
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
   * Update animal basic info (name, species, status)
   */
  async updateAnimal(animalId: string, updates: Partial<Animal>): Promise<Animal> {
    if (!animalId?.trim()) {
      throw new Error('Animal ID is required');
    }
    if (!updates || Object.keys(updates).length === 0) {
      throw new Error('Animal updates are required');
    }
    return apiRequest<Animal>(`/animal/${encodeURIComponent(animalId)}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
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
   * Convert backend Animal to frontend format
   */
  transformAnimalForFrontend(backendAnimal: Animal) {
    return {
      id: backendAnimal.animalId || 'unknown',
      animalId: backendAnimal.animalId || 'unknown',  // Ensure animalId is always present
      name: backendAnimal.name,
      species: backendAnimal.species,
      active: backendAnimal.status === 'active',
      lastUpdated: backendAnimal.modified?.at || 'Unknown',
      conversations: 0, // Not available from backend yet
      status: backendAnimal.status || 'active',
      softDelete: backendAnimal.softDelete || false,
      // Add default conversation settings to prevent frontend errors
      conversationSettings: {
        maxResponseLength: 300,
        educationalFocus: true,
        allowPersonalQuestions: true,
        scientificAccuracy: 'moderate' as const,
        ageAppropriate: true
      },
      // Add default voice settings
      voiceSettings: {
        tone: 'friendly' as const,
        formality: 'friendly' as const,
        enthusiasm: 7
      },
      // Initialize empty arrays for optional properties
      knowledgeBase: [],
      guardrails: {}
    };
  },

  /**
   * Convert frontend config to backend format
   */
  transformConfigForBackend(frontendConfig: any): Partial<AnimalConfig> {
    return {
      personality: frontendConfig.personality,
      systemPrompt: frontendConfig.systemPrompt, // Added systemPrompt field
      voice: frontendConfig.voiceSettings?.tone || 'default',
      aiModel: 'claude-3-sonnet', // Default model
      temperature: frontendConfig.conversationSettings?.enthusiasm || 0.7,
      topP: 1.0,
      toolsEnabled: [],
      guardrails: frontendConfig.guardrails || {},
    };
  },
};

// Auth API Functions
export const authApi = {
  /**
   * Login user with email/password
   */
  async login(email: string, password: string): Promise<{ token: string; expiresIn: number }> {
    if (!email?.trim()) {
      throw new Error('Email is required');
    }
    if (!password?.trim()) {
      throw new Error('Password is required');
    }
    
    return apiRequest<{ token: string; expiresIn: number }>('/auth', {
      method: 'POST',
      body: JSON.stringify({
        username: email, // Backend expects 'username' field
        password: password
      })
    });
  },

  /**
   * Refresh JWT token
   */
  async refreshToken(): Promise<{ token: string; expiresIn: number }> {
    return apiRequest<{ token: string; expiresIn: number }>('/auth/refresh', {
      method: 'POST'
    });
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    return apiRequest<void>('/auth/logout', {
      method: 'POST'
    });
  }
};

// User API Functions
export const userApi = {
  /**
   * Get current user information from token
   */
  async getCurrentUser(token: string): Promise<any> {
    return apiRequest<any>('/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }
};

export default animalApi;