/**
 * TypeScript Type Definitions for Animal Assistant Management System
 *
 * Provides comprehensive type safety for all assistant management operations
 * including animal assistants, personalities, guardrails, knowledge base,
 * and sandbox testing functionality.
 *
 * Based on data-model.md specifications and OpenAPI schema definitions.
 *
 * @author CMZ Animal Assistant Management System
 * @date 2025-10-23
 */

// ============================================================================
// Core Entity Types
// ============================================================================

/**
 * Animal Assistant - Live configuration for a specific animal
 */
export interface AnimalAssistant {
  /** Unique identifier (UUID format) */
  assistantId: string;

  /** Reference to animal entity */
  animalId: string;

  /** Reference to personality configuration */
  personalityId: string;

  /** Reference to guardrail configuration */
  guardrailId: string;

  /** Combined personality + guardrail system prompt */
  mergedPrompt: string;

  /** Array of linked knowledge base file IDs (max 50) */
  knowledgeBaseFileIds: string[];

  /** Current assistant status */
  status: AssistantStatus;

  /** Timestamp of last prompt regeneration */
  lastPromptMerge: AuditTimestamp;

  /** Performance metric for monitoring (milliseconds) */
  responseTimeP95?: number;

  /** Creation audit trail */
  created: AuditTimestamp;

  /** Last modification audit trail */
  modified: AuditTimestamp;
}

/**
 * Personality - Reusable text configuration defining animal behavior
 */
export interface Personality {
  /** Unique identifier (UUID format) */
  personalityId: string;

  /** Human-readable personality name (1-100 chars, unique) */
  name: string;

  /** Purpose and usage description (1-500 chars) */
  description: string;

  /** Core personality prompt text (100-5000 chars) */
  personalityText: string;

  /** Suggested animal categories */
  animalType: AnimalType;

  /** Communication style */
  tone: PersonalityTone;

  /** Target age group */
  ageTarget: AgeTarget;

  /** Number of assistants using this (auto-calculated) */
  usageCount: number;

  /** Whether this is a starter template */
  isTemplate: boolean;

  /** Creation audit trail */
  created: AuditTimestamp;

  /** Last modification audit trail */
  modified: AuditTimestamp;
}

/**
 * Guardrail - Text-based safety and tone rules
 */
export interface Guardrail {
  /** Unique identifier (UUID format) */
  guardrailId: string;

  /** Human-readable guardrail name (1-100 chars, unique) */
  name: string;

  /** Purpose and scope description (1-500 chars) */
  description: string;

  /** Safety rules as text prompts (50-2000 chars) */
  guardrailText: string;

  /** Guardrail category */
  category: GuardrailCategory;

  /** Enforcement level */
  severity: GuardrailSeverity;

  /** Target age groups */
  ageAppropriate: AgeTarget[];

  /** Number of assistants using this (auto-calculated) */
  usageCount: number;

  /** Whether this is default for new assistants */
  isDefault: boolean;

  /** Creation audit trail */
  created: AuditTimestamp;

  /** Last modification audit trail */
  modified: AuditTimestamp;
}

/**
 * Knowledge Base File - Educational document metadata
 */
export interface KnowledgeFile {
  /** Unique identifier (UUID format) */
  fileId: string;

  /** Associated assistant */
  assistantId: string;

  /** User-provided filename */
  originalName: string;

  /** S3 object key for original file */
  s3Key: string;

  /** S3 key for extracted text (nullable) */
  s3ProcessedKey?: string;

  /** Original file size in bytes (max 50MB) */
  fileSize: number;

  /** File content type */
  mimeType: SupportedMimeType;

  /** Current processing state */
  processingStatus: ProcessingStatus;

  /** Error message if failed (nullable) */
  processingError?: string;

  /** Length of extracted text */
  extractedTextLength?: number;

  /** Reference to vector store */
  vectorEmbeddingId?: string;

  /** Validation results */
  contentValidation?: ContentValidation;

  /** Processing start time */
  processingStarted?: string;

  /** Processing completion time */
  processingCompleted?: string;

  /** Upload audit trail */
  created: AuditTimestamp;

  /** Last modification audit trail */
  modified: AuditTimestamp;
}

/**
 * Sandbox Assistant - Temporary, ephemeral assistant for testing
 */
export interface SandboxAssistant {
  /** Unique identifier (UUID format) */
  sandboxId: string;

  /** Zoo staff member who created */
  createdBy: string;

  /** Associated animal (optional) */
  animalId?: string;

  /** Test personality configuration */
  personalityId: string;

  /** Test guardrail configuration */
  guardrailId: string;

  /** Combined test system prompt */
  mergedPrompt: string;

  /** Test knowledge base files (max 10) */
  knowledgeBaseFileIds: string[];

  /** TTL expiration timestamp (30 min from creation) */
  expiresAt: number;

  /** Number of test conversations */
  conversationCount: number;

  /** Most recent test interaction */
  lastConversationAt?: string;

  /** Whether promoted to live */
  isPromoted: boolean;

  /** Promotion timestamp (nullable) */
  promotedAt?: string;

  /** Creation audit trail */
  created: AuditTimestamp;
}

// ============================================================================
// Enum Types
// ============================================================================

/**
 * Assistant status values
 */
export enum AssistantStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  ERROR = 'ERROR'
}

/**
 * Animal type categories
 */
export enum AnimalType {
  MAMMAL = 'MAMMAL',
  BIRD = 'BIRD',
  REPTILE = 'REPTILE',
  AMPHIBIAN = 'AMPHIBIAN',
  FISH = 'FISH',
  INVERTEBRATE = 'INVERTEBRATE'
}

/**
 * Personality communication styles
 */
export enum PersonalityTone {
  PLAYFUL = 'PLAYFUL',
  EDUCATIONAL = 'EDUCATIONAL',
  CALM = 'CALM',
  ENERGETIC = 'ENERGETIC',
  WISE = 'WISE',
  FRIENDLY = 'FRIENDLY'
}

/**
 * Target age groups
 */
export enum AgeTarget {
  PRESCHOOL = 'PRESCHOOL',
  ELEMENTARY = 'ELEMENTARY',
  MIDDLE_SCHOOL = 'MIDDLE_SCHOOL',
  HIGH_SCHOOL = 'HIGH_SCHOOL',
  FAMILY = 'FAMILY',
  ADULT = 'ADULT'
}

/**
 * Guardrail categories
 */
export enum GuardrailCategory {
  SAFETY = 'SAFETY',
  EDUCATION = 'EDUCATION',
  TONE = 'TONE',
  CONTENT = 'CONTENT'
}

/**
 * Guardrail enforcement levels
 */
export enum GuardrailSeverity {
  STRICT = 'STRICT',
  MODERATE = 'MODERATE',
  GUIDANCE = 'GUIDANCE'
}

/**
 * Processing status values
 */
export enum ProcessingStatus {
  UPLOADED = 'UPLOADED',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

/**
 * Supported MIME types for knowledge base files
 */
export enum SupportedMimeType {
  PDF = 'application/pdf',
  DOC = 'application/msword',
  DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  TXT = 'text/plain'
}

// ============================================================================
// Supporting Types
// ============================================================================

/**
 * Audit timestamp with user information
 */
export interface AuditTimestamp {
  /** ISO datetime string */
  at: string;

  /** User ID who performed the action */
  by?: string;
}

/**
 * Content validation results
 */
export interface ContentValidation {
  /** Content is safe for all audiences */
  safe: boolean;

  /** Content has educational value */
  educational: boolean;

  /** Content is age-appropriate for target audience */
  ageAppropriate: boolean;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

/**
 * Request to create a new animal assistant
 */
export interface CreateAssistantRequest {
  animalId: string;
  personalityId: string;
  guardrailId: string;
  knowledgeBaseFileIds?: string[];
}

/**
 * Request to update an existing assistant
 */
export interface UpdateAssistantRequest {
  personalityId?: string;
  guardrailId?: string;
  knowledgeBaseFileIds?: string[];
  status?: AssistantStatus;
}

/**
 * Request to create a new personality
 */
export interface CreatePersonalityRequest {
  name: string;
  description: string;
  personalityText: string;
  animalType: AnimalType;
  tone: PersonalityTone;
  ageTarget: AgeTarget;
  isTemplate?: boolean;
}

/**
 * Request to create a new guardrail
 */
export interface CreateGuardrailRequest {
  name: string;
  description: string;
  guardrailText: string;
  category: GuardrailCategory;
  severity: GuardrailSeverity;
  ageAppropriate: AgeTarget[];
  isDefault?: boolean;
}

/**
 * Request to create a sandbox assistant
 */
export interface CreateSandboxRequest {
  animalId?: string;
  personalityId: string;
  guardrailId: string;
  knowledgeBaseFileIds?: string[];
}

/**
 * Request to upload a knowledge base file
 */
export interface UploadKnowledgeFileRequest {
  assistantId: string;
  file: File;
  originalName: string;
}

/**
 * Response for knowledge base file upload
 */
export interface UploadKnowledgeFileResponse {
  fileId: string;
  s3Key: string;
  processingStatus: ProcessingStatus;
  message: string;
}

/**
 * Assistant conversation request
 */
export interface ConversationRequest {
  message: string;
  assistantId?: string;
  sandboxId?: string;
  conversationId?: string;
  sessionId?: string;
}

/**
 * Assistant conversation response
 */
export interface ConversationResponse {
  response: string;
  conversationId: string;
  assistantId: string;
  timestamp: string;
  modelUsed: string;
  tokensUsed: number;
  responseTimeMs: number;
}

/**
 * Streaming conversation chunk
 */
export interface ConversationChunk {
  content: string;
  chunkId: number;
  isFinal: boolean;
  conversationId: string;
  timestamp: string;
}

// ============================================================================
// UI Component Props Types
// ============================================================================

/**
 * Props for AssistantForm component
 */
export interface AssistantFormProps {
  /** Assistant to edit (for update mode) */
  assistant?: AnimalAssistant;

  /** Available animals for selection */
  animals: Animal[];

  /** Available personalities */
  personalities: Personality[];

  /** Available guardrails */
  guardrails: Guardrail[];

  /** Form submission handler */
  onSubmit: (data: CreateAssistantRequest | UpdateAssistantRequest) => Promise<void>;

  /** Cancel handler */
  onCancel: () => void;

  /** Loading state */
  isLoading?: boolean;
}

/**
 * Props for PersonalityForm component
 */
export interface PersonalityFormProps {
  /** Personality to edit (for update mode) */
  personality?: Personality;

  /** Form submission handler */
  onSubmit: (data: CreatePersonalityRequest) => Promise<void>;

  /** Cancel handler */
  onCancel: () => void;

  /** Loading state */
  isLoading?: boolean;
}

/**
 * Props for GuardrailForm component
 */
export interface GuardrailFormProps {
  /** Guardrail to edit (for update mode) */
  guardrail?: Guardrail;

  /** Form submission handler */
  onSubmit: (data: CreateGuardrailRequest) => Promise<void>;

  /** Cancel handler */
  onCancel: () => void;

  /** Loading state */
  isLoading?: boolean;
}

/**
 * Props for SandboxTester component
 */
export interface SandboxTesterProps {
  /** Available personalities */
  personalities: Personality[];

  /** Available guardrails */
  guardrails: Guardrail[];

  /** Sandbox creation handler */
  onCreateSandbox: (data: CreateSandboxRequest) => Promise<SandboxAssistant>;

  /** Sandbox promotion handler */
  onPromoteSandbox: (sandboxId: string, assistantData: CreateAssistantRequest) => Promise<void>;
}

/**
 * Props for KnowledgeBaseUpload component
 */
export interface KnowledgeBaseUploadProps {
  /** Assistant ID for file association */
  assistantId: string;

  /** Current knowledge files */
  knowledgeFiles: KnowledgeFile[];

  /** File upload handler */
  onUpload: (data: UploadKnowledgeFileRequest) => Promise<UploadKnowledgeFileResponse>;

  /** File deletion handler */
  onDelete: (fileId: string) => Promise<void>;

  /** Maximum files allowed */
  maxFiles?: number;

  /** Maximum file size in bytes */
  maxFileSize?: number;
}

// ============================================================================
// State Management Types
// ============================================================================

/**
 * Assistant management state
 */
export interface AssistantState {
  /** All animal assistants */
  assistants: AnimalAssistant[];

  /** All personalities */
  personalities: Personality[];

  /** All guardrails */
  guardrails: Guardrail[];

  /** Active sandbox assistants */
  sandboxes: SandboxAssistant[];

  /** Knowledge base files */
  knowledgeFiles: KnowledgeFile[];

  /** Loading states */
  loading: {
    assistants: boolean;
    personalities: boolean;
    guardrails: boolean;
    sandboxes: boolean;
    knowledgeFiles: boolean;
  };

  /** Error states */
  errors: {
    assistants?: string;
    personalities?: string;
    guardrails?: string;
    sandboxes?: string;
    knowledgeFiles?: string;
  };
}

/**
 * Assistant management actions
 */
export interface AssistantActions {
  // Assistant operations
  createAssistant: (data: CreateAssistantRequest) => Promise<AnimalAssistant>;
  updateAssistant: (id: string, data: UpdateAssistantRequest) => Promise<AnimalAssistant>;
  deleteAssistant: (id: string) => Promise<void>;
  listAssistants: () => Promise<AnimalAssistant[]>;

  // Personality operations
  createPersonality: (data: CreatePersonalityRequest) => Promise<Personality>;
  updatePersonality: (id: string, data: CreatePersonalityRequest) => Promise<Personality>;
  deletePersonality: (id: string) => Promise<void>;
  listPersonalities: () => Promise<Personality[]>;

  // Guardrail operations
  createGuardrail: (data: CreateGuardrailRequest) => Promise<Guardrail>;
  updateGuardrail: (id: string, data: CreateGuardrailRequest) => Promise<Guardrail>;
  deleteGuardrail: (id: string) => Promise<void>;
  listGuardrails: () => Promise<Guardrail[]>;

  // Sandbox operations
  createSandbox: (data: CreateSandboxRequest) => Promise<SandboxAssistant>;
  promoteSandbox: (sandboxId: string, assistantData: CreateAssistantRequest) => Promise<AnimalAssistant>;
  deleteSandbox: (id: string) => Promise<void>;
  listSandboxes: () => Promise<SandboxAssistant[]>;

  // Knowledge base operations
  uploadKnowledgeFile: (data: UploadKnowledgeFileRequest) => Promise<UploadKnowledgeFileResponse>;
  deleteKnowledgeFile: (fileId: string) => Promise<void>;
  listKnowledgeFiles: (assistantId: string) => Promise<KnowledgeFile[]>;

  // Conversation operations
  sendMessage: (data: ConversationRequest) => Promise<ConversationResponse>;
  streamMessage: (data: ConversationRequest) => AsyncIterableIterator<ConversationChunk>;
}

// ============================================================================
// External Dependencies (referenced types)
// ============================================================================

/**
 * Animal entity (from existing system)
 */
export interface Animal {
  animalId: string;
  name: string;
  species: string;
  scientificName?: string;
  habitat?: string;
  status: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Filter parameters for assistant lists
 */
export interface AssistantFilters {
  status?: AssistantStatus;
  animalType?: AnimalType;
  personalityTone?: PersonalityTone;
  ageTarget?: AgeTarget;
}

/**
 * Search parameters
 */
export interface SearchParams {
  query?: string;
  filters?: AssistantFilters;
  pagination?: PaginationParams;
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * List response with pagination
 */
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for AnimalAssistant
 */
export function isAnimalAssistant(obj: any): obj is AnimalAssistant {
  return obj && typeof obj.assistantId === 'string' && typeof obj.animalId === 'string';
}

/**
 * Type guard for Personality
 */
export function isPersonality(obj: any): obj is Personality {
  return obj && typeof obj.personalityId === 'string' && typeof obj.name === 'string';
}

/**
 * Type guard for Guardrail
 */
export function isGuardrail(obj: any): obj is Guardrail {
  return obj && typeof obj.guardrailId === 'string' && typeof obj.name === 'string';
}

/**
 * Type guard for SandboxAssistant
 */
export function isSandboxAssistant(obj: any): obj is SandboxAssistant {
  return obj && typeof obj.sandboxId === 'string' && typeof obj.expiresAt === 'number';
}

/**
 * Type guard for KnowledgeFile
 */
export function isKnowledgeFile(obj: any): obj is KnowledgeFile {
  return obj && typeof obj.fileId === 'string' && typeof obj.assistantId === 'string';
}