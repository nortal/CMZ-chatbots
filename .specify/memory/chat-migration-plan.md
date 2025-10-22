# Implementation Plan: Migrate Chat Frontend from SSE to POST Polling

**Generated**: 2025-10-22
**Feature**: Replace Server-Sent Events with POST polling for Lambda-compatible chat functionality
**Branch**: feature/chat-post-polling
**Status**: Planning Phase

## Technical Context

### Current Architecture
- **Backend**: POST /convo_turn endpoint working perfectly (✅)
- **Backend**: GET /convo_turn/stream endpoint broken due to Connexion SSE limitations (❌)
- **Frontend**: Chat.tsx attempts SSE connection, falls back to error state
- **Session Management**: DynamoDB-based, stateless, load-balancer friendly
- **Deployment Target**: AWS Lambda functions with API Gateway

### Problem Statement
Server-Sent Events (SSE) streaming is incompatible with:
1. **Lambda Functions**: No persistent connections, 15-min execution limits
2. **API Gateway**: 30-second timeout limits
3. **Load Balancing**: Requires sticky sessions for SSE connections
4. **Connexion Framework**: Limited SSE support causing 404 routing errors

### Solution Approach
Replace SSE streaming with **POST polling pattern**:
- Frontend sends POST requests to /convo_turn
- Backend returns complete response immediately
- Session state persisted in DynamoDB between requests
- Load-balancer and Lambda-friendly architecture

## Constitution Check

### Compatibility Assessment
- ✅ **CMZ Requirements**: Chat functionality maintained
- ✅ **User Experience**: Functionally equivalent, slightly less real-time feel
- ✅ **Performance**: Better for short responses, eliminates SSE overhead
- ✅ **Scalability**: Perfect for serverless architecture
- ✅ **Cost**: More efficient Lambda billing (pay per request vs connection time)
- ✅ **Reliability**: Eliminates timeout and connection issues

### Risk Assessment
- **Low Risk**: Backend POST endpoint already tested and working
- **Low Risk**: DynamoDB session management already implemented
- **Medium Risk**: Frontend changes require testing across all browsers
- **Low Risk**: No breaking changes to API contracts

## Technical Gates

### Gate 1: Backend API Compatibility ✅
- POST /convo_turn endpoint tested and working
- DynamoDB persistence verified
- OpenAI integration functional
- Session management stateless

### Gate 2: Frontend Architecture Review ✅
- React component structure allows POST implementation
- State management can handle synchronous responses
- Error handling patterns applicable to POST requests

### Gate 3: Performance Requirements ✅
- POST polling suitable for typical chat response times (2-10 seconds)
- No requirement for character-by-character streaming
- User experience acceptable with loading states

## Phase 0: Research & Analysis

### Research Areas
1. **Frontend Chat Implementation**: Current SSE usage patterns in Chat.tsx
2. **Session Management**: How sessionId is handled across requests
3. **Error Handling**: Current error states and user feedback
4. **Loading States**: How UI indicates processing status
5. **Browser Compatibility**: POST vs SSE support across target browsers

### Technology Choices
- **HTTP Method**: POST (existing, tested)
- **Response Format**: JSON (existing, working)
- **Session Tracking**: DynamoDB + sessionId in request body
- **Error Handling**: Standard HTTP status codes + JSON error responses
- **Loading Indication**: React state-based spinners/indicators

## Phase 1: Design & Contracts

### Data Model
```typescript
// Request Contract (existing)
interface ChatRequest {
  message: string;
  animalId: string;
  sessionId?: string;  // Optional, created if not provided
}

// Response Contract (existing)
interface ChatResponse {
  reply: string;
  sessionId: string;
  turnId: string;
  timestamp: string;
  metadata: {
    animalId: string;
    threadId: string;
    annotations: any[];
    hasKnowledge: boolean;
  };
}

// Frontend State Model (new)
interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  connectionStatus: 'connected' | 'disconnected' | 'error';
}
```

### API Contracts

#### Existing Contract (No Changes Required)
```yaml
POST /convo_turn:
  requestBody:
    content:
      application/json:
        schema:
          type: object
          required: [message, animalId]
          properties:
            message: {type: string}
            animalId: {type: string}
            sessionId: {type: string}
  responses:
    200:
      content:
        application/json:
          schema: {$ref: '#/components/schemas/ChatResponse'}
```

### Frontend Component Contracts

#### Chat Component Interface
```typescript
interface ChatComponentProps {
  animalId: string;
  onMessageSent?: (message: string) => void;
  onError?: (error: string) => void;
}

interface ChatService {
  sendMessage(message: string, animalId: string, sessionId?: string): Promise<ChatResponse>;
  resetSession(): void;
  getSessionId(): string | null;
}
```

## Phase 2: Implementation Strategy

### Component Changes Required

1. **Chat.tsx** - Main chat component
   - Remove SSE connection logic
   - Implement POST request handling
   - Update loading states
   - Maintain session across messages

2. **ChatService** - API communication layer
   - Replace SSE EventSource with fetch POST
   - Handle session ID persistence
   - Implement error retry logic

3. **ChatMessage Components** - UI components
   - Update loading indicators
   - Remove streaming-specific animations
   - Maintain existing message display

### File Modifications

```
frontend/src/components/
├── Chat.tsx                    # Main component - MODIFY
├── ChatMessage.tsx             # Message display - MINOR UPDATES
├── ChatInput.tsx               # Input handling - NO CHANGES
└── services/
    └── ChatService.ts          # API layer - MAJOR REWRITE
```

### Implementation Sequence

1. **Create ChatService abstraction** - Centralize API calls
2. **Update Chat.tsx** - Replace SSE with POST calls
3. **Update loading states** - Replace streaming indicators
4. **Test session persistence** - Verify sessionId handling
5. **Error handling** - Update error states and messages
6. **Browser testing** - Verify across all target browsers

## Success Criteria

### Functional Requirements
- ✅ Users can send chat messages
- ✅ Users receive complete responses from animals
- ✅ Session continuity maintained across messages
- ✅ Error states clearly communicated
- ✅ Loading states indicate processing

### Performance Requirements
- ✅ Response time < 30 seconds (Lambda limit)
- ✅ UI responsive during message processing
- ✅ No memory leaks from abandoned SSE connections
- ✅ Browser compatibility maintained

### Technical Requirements
- ✅ Lambda-compatible architecture
- ✅ Load-balancer friendly (no sticky sessions)
- ✅ DynamoDB session persistence
- ✅ Standard HTTP error handling
- ✅ No breaking changes to backend API

## Next Steps

1. **Generate Tasks**: Use speckit.tasks to create detailed implementation tasks
2. **Implementation**: Execute tasks in dependency order
3. **Testing**: Validate functionality across browsers and scenarios
4. **Documentation**: Update CLAUDE.md with new chat architecture

---

**Note**: This plan leverages the existing, working POST /convo_turn endpoint and maintains all current backend functionality while providing a Lambda-compatible, load-balancer friendly chat experience.