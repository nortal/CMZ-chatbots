/**
 * Frontend Safety Service for CMZ Chatbots platform.
 *
 * This service provides a TypeScript interface to the backend safety system,
 * including content validation, guardrails management, and safety analytics.
 *
 * Key Features:
 * - Content validation before sending to AI
 * - Real-time safety feedback for users
 * - Safety analytics and monitoring
 * - Guardrails configuration management
 * - Educational messaging for inappropriate content
 */

// Using the existing API service pattern
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Token management (matching existing pattern)
const TOKEN_KEY = 'cmz_auth_token';

const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

// Generic API request handler (matching existing pattern)
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data: T }> {
  try {
    const token = getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers,
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

    const data = await response.json();
    return { data };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('API request failed: Unknown error occurred');
  }
}

// Type definitions for safety system
export interface ContentValidationRequest {
  content: string;
  context: {
    userId: string;
    conversationId: string;
    animalId: string;
  };
}

export interface ContentValidationResponse {
  valid: boolean;
  result: 'approved' | 'flagged' | 'blocked' | 'escalated';
  riskScore: number;
  requiresEscalation: boolean;
  validationId: string;
  processingTimeMs: number;
  userMessage?: string;
  safeAlternative?: string;
}

export interface SafetyMetrics {
  totalEvents: number;
  totalValidations: number;
  totalFlagged: number;
  totalBlocked: number;
  totalEscalations: number;
  flaggedContentRate: number;
  blockedContentRate: number;
  escalationRate: number;
  avgProcessingTimeMs: number;
  avgRiskScore: number;
  uniqueUsers: number;
  uniqueConversations: number;
  metadata: {
    timeRange: string;
    startTime: string;
    endTime: string;
    animalId?: string;
    totalEvents: number;
    generatedAt: string;
  };
}

export interface SafetyTrend {
  timestamp: string;
  value: number;
  eventCount: number;
}

export interface SafetyTrends {
  metricType: string;
  timeRange: string;
  granularity: string;
  animalId?: string;
  dataPoints: SafetyTrend[];
  metadata: {
    startTime: string;
    endTime: string;
    bucketCount: number;
    generatedAt: string;
  };
}

export interface RuleEffectiveness {
  triggerCount: number;
  escalationCount: number;
  effectivenessScore: number;
  averageRiskScore: number;
  uniqueUserCount: number;
  recentTriggers: Array<{
    timestamp: string;
    riskScore: number;
    escalationRequired: boolean;
  }>;
}

export interface RuleEffectivenessAnalysis {
  timeRange: string;
  animalId?: string;
  ruleEffectiveness: Record<string, RuleEffectiveness>;
  summary: {
    totalRulesAnalyzed: number;
    totalTriggers: number;
    totalEscalations: number;
    overallEffectiveness: number;
  };
  generatedAt: string;
}

export interface GuardrailsRule {
  ruleId: string;
  type: 'ALWAYS' | 'NEVER' | 'ENCOURAGE' | 'DISCOURAGE';
  rule: string;
  priority: number;
  isActive: boolean;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  examples: string[];
}

export interface GuardrailsConfig {
  configId: string;
  animalId?: string;
  name: string;
  description: string;
  isActive: boolean;
  version: number;
  rules: GuardrailsRule[];
  createdBy: string;
  createdAt: string;
  modifiedAt: string;
}

export interface SafetyStatus {
  isEnabled: boolean;
  healthStatus: 'healthy' | 'degraded' | 'critical' | 'offline';
  lastCheck: string;
  services: {
    openai: 'online' | 'offline' | 'degraded';
    guardrails: 'online' | 'offline' | 'degraded';
    analytics: 'online' | 'offline' | 'degraded';
  };
  recentActivity: {
    validationsLastHour: number;
    flaggedLastHour: number;
    avgResponseTime: number;
  };
}

/**
 * Main GuardrailsService class for frontend safety operations
 */
export class GuardrailsService {
  constructor() {
    // No dependencies needed - uses internal apiRequest function
  }

  /**
   * Validate content before sending to AI
   */
  async validateContent(request: ContentValidationRequest): Promise<ContentValidationResponse> {
    try {
      const response = await apiRequest<ContentValidationResponse>(
        '/api/v1/guardrails/validate',
        {
          method: 'POST',
          body: JSON.stringify({
            content: request.content,
            context: request.context
          })
        }
      );

      return response.data;
    } catch (error) {
      console.error('Content validation failed:', error);

      // Return safe fallback response
      return {
        valid: false,
        result: 'escalated',
        riskScore: 1.0,
        requiresEscalation: true,
        validationId: `error_${Date.now()}`,
        processingTimeMs: 0,
        userMessage: 'We\'re having trouble checking your message right now. Please try again.'
      };
    }
  }

  /**
   * Quick safety check for user input
   */
  async quickSafetyCheck(
    content: string,
    userId?: string,
    conversationId?: string,
    animalId?: string
  ): Promise<{ isSafe: boolean; userMessage?: string; safeAlternative?: string }> {
    if (!content || content.trim().length === 0) {
      return { isSafe: true };
    }

    const result = await this.validateContent({
      content,
      context: { userId, conversationId, animalId }
    });

    return {
      isSafe: result.valid && result.result !== 'blocked',
      userMessage: result.userMessage,
      safeAlternative: result.safeAlternative
    };
  }

  /**
   * Get effective guardrails configuration for an animal
   */
  async getEffectiveGuardrails(animalId?: string): Promise<GuardrailsConfig> {
    try {
      const response = await apiRequest<GuardrailsConfig>(
        `/api/v1/guardrails/effective${animalId ? `?animalId=${animalId}` : ''}`,
        {
          method: 'GET'
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get effective guardrails:', error);
      throw new Error('Unable to load safety configuration');
    }
  }

  /**
   * Get safety metrics for monitoring dashboard
   */
  async getSafetyMetrics(
    timeRange: '1h' | '24h' | '7d' | '30d' = '24h',
    animalId?: string
  ): Promise<SafetyMetrics> {
    try {
      const params = new URLSearchParams({ time_range: timeRange });
      if (animalId) params.append('animal_id', animalId);

      const response = await apiRequest<SafetyMetrics>(
        `/api/v1/analytics/safety/metrics?${params}`,
        {
          method: 'GET'
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get safety metrics:', error);
      throw new Error('Unable to load safety metrics');
    }
  }

  /**
   * Get safety trends for dashboard charts
   */
  async getSafetyTrends(
    metricType: 'total_content_validated' | 'flagged_content_rate' | 'validation_latency',
    timeRange: '1h' | '24h' | '7d' | '30d' = '7d',
    granularity: '15m' | '1h' | '1d' = '1h',
    animalId?: string
  ): Promise<SafetyTrends> {
    try {
      const params = new URLSearchParams({
        metric_type: metricType,
        time_range: timeRange,
        granularity: granularity
      });
      if (animalId) params.append('animal_id', animalId);

      const response = await apiRequest<SafetyTrends>(
        `/api/v1/analytics/safety/trends?${params}`,
        {
          method: 'GET'
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get safety trends:', error);
      throw new Error('Unable to load safety trends');
    }
  }

  /**
   * Get rule effectiveness analysis
   */
  async getRuleEffectiveness(
    timeRange: '7d' | '30d' = '7d',
    animalId?: string
  ): Promise<RuleEffectivenessAnalysis> {
    try {
      const params = new URLSearchParams({ time_range: timeRange });
      if (animalId) params.append('animal_id', animalId);

      const response = await apiRequest<RuleEffectivenessAnalysis>(
        `/api/v1/analytics/safety/rule-effectiveness?${params}`,
        {
          method: 'GET'
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get rule effectiveness:', error);
      throw new Error('Unable to load rule effectiveness data');
    }
  }

  /**
   * Get current safety system status
   */
  async getSafetyStatus(): Promise<SafetyStatus> {
    try {
      // This would be a separate health check endpoint
      // For now, we'll implement a simple status check
      const [metricsResult, guardrailsResult] = await Promise.allSettled([
        this.getSafetyMetrics('1h'),
        this.getEffectiveGuardrails()
      ]);

      const isHealthy = metricsResult.status === 'fulfilled' && guardrailsResult.status === 'fulfilled';

      return {
        isEnabled: true,
        healthStatus: isHealthy ? 'healthy' : 'degraded',
        lastCheck: new Date().toISOString(),
        services: {
          openai: isHealthy ? 'online' : 'degraded',
          guardrails: guardrailsResult.status === 'fulfilled' ? 'online' : 'offline',
          analytics: metricsResult.status === 'fulfilled' ? 'online' : 'offline'
        },
        recentActivity: {
          validationsLastHour: metricsResult.status === 'fulfilled' ?
            metricsResult.value.totalValidations : 0,
          flaggedLastHour: metricsResult.status === 'fulfilled' ?
            metricsResult.value.totalFlagged : 0,
          avgResponseTime: metricsResult.status === 'fulfilled' ?
            metricsResult.value.avgProcessingTimeMs : 0
        }
      };
    } catch (error) {
      console.error('Failed to get safety status:', error);

      return {
        isEnabled: false,
        healthStatus: 'critical',
        lastCheck: new Date().toISOString(),
        services: {
          openai: 'offline',
          guardrails: 'offline',
          analytics: 'offline'
        },
        recentActivity: {
          validationsLastHour: 0,
          flaggedLastHour: 0,
          avgResponseTime: 0
        }
      };
    }
  }

  /**
   * Create or update guardrails configuration (admin only)
   */
  async createGuardrailsConfig(config: Omit<GuardrailsConfig, 'configId' | 'createdAt' | 'modifiedAt'>): Promise<GuardrailsConfig> {
    try {
      const response = await apiRequest<GuardrailsConfig>(
        '/api/v1/guardrails/config',
        {
          method: 'POST',
          body: JSON.stringify(config)
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to create guardrails config:', error);
      throw new Error('Unable to create guardrails configuration');
    }
  }

  /**
   * Utility method to determine if content needs safety validation
   */
  shouldValidateContent(content: string): boolean {
    // Skip validation for very short content
    if (!content || content.trim().length < 3) {
      return false;
    }

    // Skip validation for simple greetings
    const simpleGreetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye'];
    const contentLower = content.toLowerCase().trim();

    if (simpleGreetings.includes(contentLower)) {
      return false;
    }

    // Validate everything else
    return true;
  }

  /**
   * Format safety messages for display to users
   */
  formatSafetyMessage(response: ContentValidationResponse): string {
    if (response.userMessage) {
      return response.userMessage;
    }

    switch (response.result) {
      case 'approved':
        return '';
      case 'flagged':
        return 'Let\'s keep our conversation educational and fun!';
      case 'blocked':
        return 'I can\'t help with that topic. Let\'s talk about something fun and educational about animals instead!';
      case 'escalated':
        return 'Let me get a zookeeper to help answer your question!';
      default:
        return 'Let\'s keep our conversation focused on learning about animals!';
    }
  }

  /**
   * Get safety level indicator for UI
   */
  getSafetyLevelIndicator(riskScore: number): {
    level: 'safe' | 'warning' | 'danger';
    color: string;
    message: string;
  } {
    if (riskScore < 0.3) {
      return {
        level: 'safe',
        color: '#10B981', // green
        message: 'Content looks good!'
      };
    } else if (riskScore < 0.7) {
      return {
        level: 'warning',
        color: '#F59E0B', // yellow
        message: 'Content may need review'
      };
    } else {
      return {
        level: 'danger',
        color: '#EF4444', // red
        message: 'Content flagged for safety'
      };
    }
  }
}

// Export singleton instance
let guardrailsServiceInstance: GuardrailsService | null = null;

export const getGuardrailsService = (): GuardrailsService => {
  if (!guardrailsServiceInstance) {
    guardrailsServiceInstance = new GuardrailsService();
  }
  return guardrailsServiceInstance;
};

// Enhanced Guardrails interfaces for detailed feedback
import {
  DetailedValidationResponse,
  ContentValidationRequest,
  TriggeredRule,
  RuleAnalyticsResponse,
  EducationalGuidance,
  GuardrailsApiError
} from '../types/GuardrailTypes';

/**
 * Enhanced Guardrails Service for detailed rule feedback.
 */
export class EnhancedGuardrailsService {
  /**
   * Validate content with detailed rule feedback.
   */
  async validateContentDetailed(
    content: string,
    context: {
      userId: string;
      conversationId: string;
      animalId: string;
      ageGroup?: string;
    }
  ): Promise<DetailedValidationResponse> {
    const request: ContentValidationRequest = {
      content,
      context: {
        userId: context.userId,
        conversationId: context.conversationId,
        animalId: context.animalId,
        ageGroup: context.ageGroup as any
      }
    };

    try {
      const result = await apiRequest<DetailedValidationResponse>(
        '/api/v1/guardrails/validate',
        {
          method: 'POST',
          body: JSON.stringify(request),
        }
      );

      return result.data;
    } catch (error) {
      console.error('Enhanced validation failed:', error);

      // Return fallback response for backward compatibility
      return {
        valid: true,
        result: 'approved',
        riskScore: 0,
        requiresEscalation: false,
        validationId: `fallback_${Date.now()}`,
        timestamp: new Date().toISOString(),
        processingTimeMs: 0,
        triggeredRules: {
          totalTriggered: 0,
          highestSeverity: 'none',
          customGuardrails: []
        },
        summary: {
          requiresEscalation: false,
          blockingViolations: 0,
          warningViolations: 0,
          ageGroupApproved: 'elementary'
        }
      };
    }
  }

  /**
   * Get rule effectiveness analytics.
   */
  async getRuleAnalytics(
    ruleId: string,
    timeWindow: '1h' | '24h' = '24h',
    includeDetails: boolean = false
  ): Promise<RuleAnalyticsResponse> {
    const params = new URLSearchParams({
      timeWindow,
      includeDetails: includeDetails.toString()
    });

    const result = await apiRequest<RuleAnalyticsResponse>(
      `/api/v1/guardrails/rules/${ruleId}/analytics?${params}`,
      { method: 'GET' }
    );

    return result.data;
  }

  /**
   * Get educational guidance for a triggered rule.
   */
  async getEducationalGuidance(
    rule: TriggeredRule,
    context: {
      ageGroup?: string;
      animalId?: string;
    }
  ): Promise<EducationalGuidance> {
    // This would be implemented when User Story 2 is developed
    // For now, return default guidance
    return {
      topic: 'Animal Safety',
      response: 'Let\'s learn about how we keep animals safe and happy!',
      suggestions: [
        'What do animals need to stay healthy?',
        'How do zoo keepers care for animals?',
        'What makes animals feel safe?'
      ],
      alternativeQuestions: [
        'Tell me about animal habitats',
        'How do animals communicate?',
        'What do different animals eat?'
      ],
      learningObjectives: [
        'Understand animal welfare',
        'Learn about responsible animal care',
        'Explore positive animal interactions'
      ]
    };
  }

  /**
   * Test content validation (for Safety Management interface).
   */
  async testContentValidation(
    content: string,
    options: {
      animalId?: string;
      ageGroup?: string;
      includeAnalytics?: boolean;
    } = {}
  ): Promise<DetailedValidationResponse> {
    const context = {
      userId: 'test_user',
      conversationId: `test_${Date.now()}`,
      animalId: options.animalId || 'test_animal',
      ageGroup: options.ageGroup
    };

    return this.validateContentDetailed(content, context);
  }

  /**
   * Get comprehensive rule effectiveness summary.
   */
  async getAllRulesEffectiveness(
    timeWindow: '1h' | '24h' = '24h'
  ): Promise<RuleAnalyticsResponse[]> {
    // This would fetch analytics for all rules
    // For now, return empty array (will be implemented in User Story 3)
    return [];
  }

  /**
   * Handle validation errors with user-friendly messages.
   */
  private handleValidationError(error: any): GuardrailsApiError {
    if (error.response?.data) {
      return error.response.data;
    }

    return {
      error: 'Validation service temporarily unavailable',
      code: 'SERVICE_UNAVAILABLE',
      details: [{
        code: 'NETWORK_ERROR',
        message: 'Please try again in a moment',
        details: { originalError: error.message }
      }]
    };
  }
}

// Global instance for enhanced service
let enhancedGuardrailsServiceInstance: EnhancedGuardrailsService | null = null;

export const getEnhancedGuardrailsService = (): EnhancedGuardrailsService => {
  if (!enhancedGuardrailsServiceInstance) {
    enhancedGuardrailsServiceInstance = new EnhancedGuardrailsService();
  }
  return enhancedGuardrailsServiceInstance;
};

export default GuardrailsService;