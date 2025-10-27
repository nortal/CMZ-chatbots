/**
 * TypeScript interfaces for Enhanced Guardrails Feedback system.
 *
 * These interfaces provide type safety for the detailed rule-level feedback
 * functionality, ensuring frontend-backend contract compliance.
 */

// Base types for guardrail rules
export type RuleType = 'ALWAYS' | 'NEVER' | 'ENCOURAGE' | 'DISCOURAGE';

export type RuleSeverity = 'low' | 'medium' | 'high' | 'critical';

export type RuleCategory =
  | 'safety'
  | 'educational'
  | 'age-appropriate'
  | 'behavioral'
  | 'content-quality'
  | 'privacy';

export type ValidationResult = 'approved' | 'flagged' | 'blocked' | 'escalated';

export type AgeGroup = 'elementary' | 'middle' | 'high' | 'adult' | 'none';

export type ModerationCategory =
  | 'hate'
  | 'hate/threatening'
  | 'harassment'
  | 'harassment/threatening'
  | 'self-harm'
  | 'self-harm/intent'
  | 'self-harm/instructions'
  | 'sexual'
  | 'sexual/minors'
  | 'violence'
  | 'violence/graphic';

// Triggered rule interface
export interface TriggeredRule {
  ruleId: string;
  ruleText: string;
  ruleType: RuleType;
  category: RuleCategory;
  severity: RuleSeverity;
  confidenceScore: number;
  triggerContext?: string;
  userMessage?: string;
  detectedAt: string; // ISO8601 timestamp
  priority?: number;
}

// OpenAI moderation category
export interface OpenAIModerationCategory {
  category: ModerationCategory;
  severity: RuleSeverity;
  confidenceScore: number;
  rawScore: number;
  detectedAt: string; // ISO8601 timestamp
}

// OpenAI moderation result
export interface OpenAIModerationResult {
  flagged: boolean;
  model: string;
  categories: OpenAIModerationCategory[];
}

// Triggered rules summary
export interface TriggeredRulesSummary {
  totalTriggered: number;
  highestSeverity: RuleSeverity | 'none';
  openaiModeration?: OpenAIModerationResult;
  customGuardrails: TriggeredRule[];
}

// Validation summary
export interface ValidationSummary {
  requiresEscalation: boolean;
  blockingViolations: number;
  warningViolations: number;
  ageGroupApproved: AgeGroup;
}

// Enhanced validation response
export interface DetailedValidationResponse {
  // Backward compatibility fields
  valid: boolean;
  result: ValidationResult;
  riskScore: number;
  requiresEscalation: boolean;
  userMessage?: string;
  safeAlternative?: string;

  // Enhanced fields
  validationId: string;
  timestamp: string; // ISO8601 timestamp
  processingTimeMs: number;
  triggeredRules: TriggeredRulesSummary;
  summary: ValidationSummary;
}

// Content validation request
export interface ContentValidationRequest {
  content: string;
  context: {
    userId: string;
    conversationId: string;
    animalId: string;
    ageGroup?: AgeGroup;
  };
}

// UI-specific interfaces for component props

export interface TriggeredRulesDisplayProps {
  validationResult: DetailedValidationResponse;
  sortBy?: 'severity' | 'confidence' | 'timestamp';
  groupBy?: 'none' | 'severity' | 'type' | 'category';
  showAnalytics?: boolean;
  onRuleClick?: (rule: TriggeredRule) => void;
}

export interface CollapsibleRuleCardProps {
  rule: TriggeredRule;
  isExpanded: boolean;
  onToggle: () => void;
  showDetails?: boolean;
  showContext?: boolean;
}

export interface RuleAnalyticsProps {
  timeWindow?: '1h' | '24h';
  refreshInterval?: number;
  showTrends?: boolean;
}

// Utility types for sorting and filtering

export interface RuleSortOptions {
  field: 'severity' | 'confidence' | 'timestamp' | 'category';
  direction: 'asc' | 'desc';
}

export interface RuleFilterOptions {
  severities?: RuleSeverity[];
  categories?: RuleCategory[];
  types?: RuleType[];
  minConfidence?: number;
  maxConfidence?: number;
}

// Analytics interfaces (for User Story 3)

export interface RuleEffectivenessMetrics {
  ruleId: string;
  timeWindow: string;
  totalTriggers: number;
  averageConfidence: number;
  effectivenessScore: number;
  triggerTrend: 'stable' | 'increasing' | 'decreasing';
  severityBreakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  flaggedForReview?: boolean;
  reviewReason?: string;
}

export interface HourlyRuleData {
  hour: string; // ISO8601 timestamp
  triggers: number;
  avgConfidence: number;
}

export interface RuleAnalyticsResponse {
  ruleId: string;
  timeWindow: string;
  totalTriggers: number;
  averageConfidence: number;
  effectivenessScore: number;
  triggerTrend: 'stable' | 'increasing' | 'decreasing';
  severityBreakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  hourlyData?: HourlyRuleData[];
  flaggedForReview?: boolean;
  reviewReason?: string;
}

// Educational guidance interfaces (for User Story 2)

export interface EducationalGuidance {
  topic: string;
  response: string;
  suggestions: string[];
  alternativeQuestions: string[];
  learningObjectives: string[];
}

export interface EducationalGuidanceProps {
  rule: TriggeredRule;
  guidance: EducationalGuidance;
  onSuggestionClick?: (suggestion: string) => void;
}

// Safety management interface enhancements

export interface SafetyTestingContext {
  testContent: string;
  selectedAnimal?: string;
  ageGroup?: AgeGroup;
  validationHistory: DetailedValidationResponse[];
  currentValidation?: DetailedValidationResponse;
}

export interface SafetyManagementState {
  isLoading: boolean;
  error?: string;
  testingContext: SafetyTestingContext;
  showAdvancedOptions: boolean;
  selectedRuleFilter: RuleFilterOptions;
  sortOptions: RuleSortOptions;
}

// Event handlers for user interactions

export interface SafetyManagementHandlers {
  onContentTest: (content: string, context: ContentValidationRequest['context']) => Promise<void>;
  onRuleExpand: (ruleId: string) => void;
  onRuleCollapse: (ruleId: string) => void;
  onFilterChange: (filters: RuleFilterOptions) => void;
  onSortChange: (sort: RuleSortOptions) => void;
  onAnalyticsToggle: () => void;
}

// Error handling

export interface ValidationError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, any>;
}

export interface GuardrailsApiError {
  error: string;
  code: string;
  details?: ValidationError[];
}

// Constants for UI configuration

export const SEVERITY_COLORS = {
  critical: '#dc2626', // red-600
  high: '#ea580c',     // orange-600
  medium: '#d97706',   // amber-600
  low: '#65a30d',      // lime-600
  none: '#6b7280'      // gray-500
} as const;

export const CATEGORY_ICONS = {
  safety: '🛡️',
  educational: '📚',
  'age-appropriate': '👶',
  behavioral: '🤝',
  'content-quality': '✨',
  privacy: '🔒'
} as const;

export const RULE_TYPE_LABELS = {
  ALWAYS: 'Required',
  NEVER: 'Prohibited',
  ENCOURAGE: 'Encouraged',
  DISCOURAGE: 'Discouraged'
} as const;