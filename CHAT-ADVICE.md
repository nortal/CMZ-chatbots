# CHAT-ADVICE.md - Chat and Chat History Implementation Guide

## Overview
This document tracks learnings, patterns, and best practices discovered during the implementation of the Chat and Chat History Epic (PR003946-170). All team members working on chat-related tickets should read this document first and update it with their learnings.

## Epic Context
- **Epic**: PR003946-170 - Enable Chat - ChatGPT Integration with Real-time Streaming
- **Tickets**: PR003946-156 through PR003946-169 (14 tickets total)
- **Total Story Points**: 89
- **Estimated Duration**: 3-4 sprints

## Implementation Status

### Completed Items
- ✅ **PR003946-170**: Epic created for Enable Chat functionality
- ✅ **Basic /convo_turn endpoint**: Returns "We're having a conversation!" placeholder

### In Progress
- 🔄 **Ticket Updates**: All 14 tickets updated with CHAT-ADVICE.md requirements

### Pending Implementation
- ⏳ PR003946-156: ChatGPT Integration with Animal Personalities
- ⏳ PR003946-157: Response Streaming with Server-Sent Events
- ⏳ PR003946-158: DynamoDB Conversation Storage
- ⏳ PR003946-159: Conversation Session List Endpoint
- ⏳ PR003946-160: Role-Based Access Control for History
- ⏳ PR003946-161: Conversation History Retrieval Endpoint
- ⏳ PR003946-162: Chat History List Page with 21st.dev
- ⏳ PR003946-163: Conversation Viewer Page with 21st.dev
- ⏳ PR003946-164: Real-time Chat Streaming UI with 21st.dev
- ⏳ PR003946-165: Family View for Parent History Access
- ⏳ PR003946-166: Audit Logging for Conversation Access
- ⏳ PR003946-167: Data Privacy Controls
- ⏳ PR003946-168: DynamoDB Tables and Indexes Setup
- ⏳ PR003946-169: E2E Tests for Complete Chat Flow

## Technical Architecture

### Backend Components

#### API Endpoints
```yaml
/convo_turn:
  POST:
    description: "Submit a chat message and receive AI response"
    current_status: "Returns placeholder response"
    implementation_file: "impl/conversation.py"
    handler: "handle_convo_turn_post"

/convo_turn/stream:
  POST:
    description: "Stream chat responses via Server-Sent Events"
    status: "Not yet implemented"
    notes: "Will require SSE support in Flask/Connexion"

/conversations/sessions:
  GET:
    description: "List conversation sessions with pagination"
    status: "Not yet implemented"

/conversations/history/{sessionId}:
  GET:
    description: "Retrieve full conversation history"
    status: "Not yet implemented"
```

#### DynamoDB Schema (Proposed)
```yaml
Table: cmz-conversations
Partition Key: userId (String)
Sort Key: sessionId#timestamp (String)

Global Secondary Indexes:
  GSI1: sessionId as PK, timestamp as SK
  GSI2: animalId as PK, timestamp as SK
  GSI3: parentUserId as PK, timestamp as SK

Attributes:
  - userId: User who initiated conversation
  - sessionId: Unique session identifier
  - timestamp: ISO 8601 timestamp
  - animalId: Animal personality in conversation
  - messageType: "user" or "assistant"
  - content: Message content
  - tokensUsed: Token consumption for billing
  - parentUserId: For family access control
  - ttl: Timestamp for automatic deletion (90 days)
```

### Frontend Components

#### Chat Interface
- **Location**: `/frontend/src/pages/Chat.tsx` (to be created)
- **Components**: Use 21st.dev chat components
- **Features**: Real-time streaming, typing indicators, message history

#### History Viewer
- **Location**: `/frontend/src/pages/ChatHistory.tsx` (to be created)
- **Components**: DataTable from 21st.dev
- **Features**: Filtering, sorting, export functionality

## Implementation Patterns

### ChatGPT Integration Pattern
```python
# Pattern for animal personality integration
def get_animal_personality(animal_id):
    """Fetch animal configuration from DynamoDB"""
    # TODO: Document actual implementation

def construct_system_prompt(animal_config):
    """Build ChatGPT system prompt with personality"""
    # TODO: Document prompt engineering best practices

def call_chatgpt_api(messages, animal_endpoint_url=None):
    """Call ChatGPT with proper error handling"""
    # TODO: Document rate limiting and retry logic
```

### Server-Sent Events Pattern
```python
# Pattern for SSE streaming
def stream_response():
    """Generator for SSE responses"""
    # TODO: Document Flask SSE implementation
    yield f"data: {json.dumps(chunk)}\n\n"
```

### Role-Based Access Pattern
```python
# Access control hierarchy
ROLE_PERMISSIONS = {
    'student': ['own_conversations'],
    'parent': ['own_conversations', 'children_conversations'],
    'zookeeper': ['all_conversations_readonly'],
    'admin': ['all_conversations_full']
}
```

## Common Issues and Solutions

### Issue 1: CORS for SSE
**Problem**: Server-Sent Events require specific CORS headers
**Solution**: TBD - Document when implementing PR003946-157

### Issue 2: DynamoDB TTL
**Problem**: TTL attribute needs specific format
**Solution**: Use Unix timestamp (seconds since epoch) for TTL attribute

### Issue 3: Token Counting
**Problem**: Need accurate token counting for billing
**Solution**: Use tiktoken library for GPT token counting

## Testing Strategies

### Unit Tests
- Mock ChatGPT API responses
- Test DynamoDB operations with moto
- Validate access control logic

### Integration Tests
- Test complete conversation flow
- Verify SSE streaming
- Check role-based access

### E2E Tests (Playwright)
- User login → Start chat → Receive response
- Parent views child's history
- Export conversation functionality

## Security Considerations

### Data Privacy
- PII detection in conversations
- Automatic redaction of sensitive info
- COPPA compliance for children under 13

### Access Control
- JWT token validation
- Role-based permissions
- Audit logging for all access

### Rate Limiting
- Per-user rate limits
- ChatGPT API quota management
- Cost control mechanisms

## Performance Optimization

### Caching Strategy
- Cache animal configurations (5 min TTL)
- Cache session lists for pagination
- Use Redis for real-time data

### Database Optimization
- Batch writes for conversation storage
- Query optimization with GSIs
- DynamoDB auto-scaling configuration

## Deployment Considerations

### Environment Variables
```bash
CHATGPT_API_KEY=sk-...
CHATGPT_ORG_ID=org-...
DYNAMODB_CONVERSATIONS_TABLE=cmz-conversations
SSE_TIMEOUT=30000
CONVERSATION_TTL_DAYS=90
```

### Infrastructure Requirements
- DynamoDB table with proper indexes
- API Gateway SSE support
- CloudWatch logging for audit trail

## Team Notes

### PR003946-156 (ChatGPT Integration)
*Notes to be added by implementer*

### PR003946-157 (SSE Streaming)
*Notes to be added by implementer*

### PR003946-158 (DynamoDB Storage)
*Notes to be added by implementer*

### PR003946-159 (Session List)
*Notes to be added by implementer*

### PR003946-160 (RBAC)
*Notes to be added by implementer*

### PR003946-161 (History Retrieval)
*Notes to be added by implementer*

### PR003946-162 (Chat History UI)
*Notes to be added by implementer*

### PR003946-163 (Conversation Viewer)
*Notes to be added by implementer*

### PR003946-164 (Streaming UI)
*Notes to be added by implementer*

### PR003946-165 (Family View)
*Notes to be added by implementer*

### PR003946-166 (Audit Logging)
*Notes to be added by implementer*

### PR003946-167 (Privacy Controls)
*Notes to be added by implementer*

### PR003946-168 (DynamoDB Setup)
*Notes to be added by implementer*

### PR003946-169 (E2E Tests)
*Notes to be added by implementer*

## References

### External Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [21st.dev Components](https://21st.dev)

### Internal Documentation
- [OpenAPI Spec](backend/api/openapi_spec.yaml)
- [Implementation Guide](CLAUDE.md)
- [Jira Epic](https://nortal.atlassian.net/browse/PR003946-170)

## Update History

- **2025-01-18**: Initial document created with epic structure and ticket requirements
- **2025-01-18**: Added placeholder /convo_turn implementation notes

---

**Remember**: Update this document with your learnings to help the team!