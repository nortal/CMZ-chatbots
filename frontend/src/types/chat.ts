/**
 * Chat Types for POST Polling Implementation
 *
 * These interfaces define the contract for migrating from SSE streaming
 * to POST request/response pattern for Lambda compatibility.
 *
 * Migration Context:
 * - Replaces EventSource SSE streaming with synchronous POST requests
 * - Maintains session continuity through sessionId parameter
 * - Simplifies from auto-generated OpenAPI types for frontend clarity
 */

// Request interface for POST /convo_turn
export interface ChatRequest {
  /** The user's message content */
  message: string;

  /** Animal personality identifier */
  animalId: string;

  /** Session identifier for conversation continuity (optional, server generates if not provided) */
  sessionId?: string;

  /** Additional context or metadata */
  metadata?: {
    userId?: string;
    source?: 'web' | 'mobile';
    [key: string]: unknown;
  };
}

// Response interface from POST /convo_turn
export interface ChatResponse {
  /** The AI assistant's complete response */
  reply: string;

  /** Session identifier for this conversation */
  sessionId: string;

  /** Unique identifier for this turn */
  turnId: string;

  /** ISO timestamp when response was generated */
  timestamp: string;

  /** Response metadata and analytics */
  metadata: {
    /** Animal that generated the response */
    animalId: string;

    /** OpenAI thread identifier */
    threadId?: string;

    /** Additional annotations or context */
    annotations: unknown[];

    /** Whether knowledge base was used */
    hasKnowledge: boolean;

    /** Token usage information */
    tokens?: {
      prompt?: number;
      completion?: number;
      total?: number;
    };

    /** Model used for response generation */
    model?: string;

    /** Response latency in milliseconds */
    latencyMs?: number;
  };
}

// Error response for failed requests
export interface ChatError {
  /** Error message */
  message: string;

  /** HTTP status code */
  status: number;

  /** Error type classification */
  type: 'validation' | 'auth' | 'rate_limit' | 'server' | 'network';

  /** Additional error context */
  details?: {
    field?: string;
    code?: string;
    retryAfter?: number;
  };
}

// Chat message state for UI components
export interface ChatMessage {
  /** Unique message identifier */
  id: string;

  /** Message content */
  content: string;

  /** Whether message is from user or assistant */
  isUser: boolean;

  /** Message timestamp */
  timestamp: Date;

  /** Current message status */
  status: 'sending' | 'sent' | 'received' | 'error';

  /** Associated animal identifier */
  animalId?: string;

  /** Session this message belongs to */
  sessionId?: string;

  /** Error information if status is 'error' */
  error?: ChatError;
}

// Connection status for POST polling
export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

// Chat service configuration
export interface ChatConfig {
  /** API base URL */
  apiUrl: string;

  /** Request timeout in milliseconds (default: 30000 for Lambda compatibility) */
  timeout?: number;

  /** Number of retry attempts for failed requests */
  maxRetries?: number;

  /** Delay between retry attempts in milliseconds */
  retryDelay?: number;
}