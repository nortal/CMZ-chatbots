# Epic: Chat and Chat History Functionality

**Epic ID**: CMZ-EPIC-001
**Epic Name**: Chat and chat history functionality
**Priority**: High
**Estimated Duration**: 3-4 sprints (6-8 weeks)
**Total Story Points**: 89 points

## Epic Overview

Implement a comprehensive chat system that enables real-time streaming conversations with animal chatbots, stores conversation history in DynamoDB, and provides secure access to chat history based on user roles. The system will integrate with ChatGPT APIs using unique endpoints per animal, stream responses in real-time, and maintain complete conversation records with proper access controls.

## Business Value

- **User Engagement**: Enable immersive, real-time conversations with animal personalities
- **Educational Impact**: Preserve learning conversations for review and continued education
- **Parental Oversight**: Allow parents to review their children's conversations for safety
- **Zoo Management**: Enable zookeepers and administrators to monitor engagement and quality
- **Data Insights**: Build valuable conversation data for improving animal personalities and educational content

## Technical Architecture

### Key Components
1. **ChatGPT Integration**: Unique endpoint per animal with system prompts
2. **Streaming Response**: Server-sent events (SSE) for real-time response streaming
3. **DynamoDB Storage**: Conversation history with session management
4. **Role-Based Access**: Hierarchical permission system for history viewing
5. **UI Components**: Chat interface and history viewer (built with 21st.dev)

### Security Model
- **User**: Can view only their own conversation history
- **Parent**: Can view their own and their children's history
- **Zookeeper**: Can view all conversation histories
- **Administrator**: Full access to all conversations
- **Visitor**: No access to conversation history

---

## Backend Tickets

### Ticket 1: [Backend] Implement ChatGPT Integration with Animal Personalities
**Type**: Task
**Story Points**: 8
**Priority**: Critical
**Sprint**: 1

**Description**:
Integrate the /convo_turn endpoint with ChatGPT API to enable real conversations with animal personalities. Each animal will have a unique ChatGPT endpoint URL and system prompt configuration.

**Technical Requirements**:
- Modify `handle_convo_turn_post` in `conversation.py`
- Load animal personality configuration from DynamoDB
- Construct system prompt with animal personality traits
- Call ChatGPT API with animal-specific endpoint URL
- Handle API errors and rate limiting
- Support conversation context (last 10 messages)

**Implementation Details**:
```python
# Configuration structure in DynamoDB animals table
{
    "animalId": "lion_001",
    "chatConfig": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4",
        "systemPrompt": "You are Leo, a friendly lion at Cougar Mountain Zoo...",
        "temperature": 0.7,
        "maxTokens": 500,
        "personality": {
            "traits": ["playful", "educational", "friendly"],
            "knowledge": ["savanna facts", "lion behavior", "conservation"]
        }
    }
}
```

**API Integration**:
```python
async def handle_convo_turn_post(body, animalId, userId):
    # 1. Load animal config from DynamoDB
    animal = get_animal_config(animalId)

    # 2. Build conversation context
    context = get_conversation_context(userId, animalId, limit=10)

    # 3. Construct ChatGPT request
    messages = [
        {"role": "system", "content": animal.chatConfig.systemPrompt},
        *context,
        {"role": "user", "content": body.message}
    ]

    # 4. Call ChatGPT API
    response = await call_chatgpt(
        endpoint=animal.chatConfig.endpoint,
        messages=messages,
        **animal.chatConfig
    )

    # 5. Store in DynamoDB (async)
    store_conversation_turn(userId, animalId, body.message, response)

    return response
```

**Acceptance Criteria**:
- [ ] GIVEN a message with animalId WHEN sent to /convo_turn THEN ChatGPT API is called with correct animal personality
- [ ] GIVEN animal has custom endpoint URL WHEN chat requested THEN that specific URL is used
- [ ] GIVEN conversation has history WHEN new message sent THEN last 10 messages are included as context
- [ ] GIVEN ChatGPT API fails WHEN message sent THEN graceful fallback message returns
- [ ] GIVEN rate limit exceeded WHEN message sent THEN appropriate error with retry-after header returns
- [ ] GIVEN animal has no chat config WHEN message sent THEN default friendly response returns

**Dependencies**:
- OpenAI API credentials configured
- Animal personality configurations in DynamoDB
- Error handling middleware

---

### Ticket 2: [Backend] Implement Response Streaming with Server-Sent Events
**Type**: Task
**Story Points**: 13
**Priority**: Critical
**Sprint**: 1

**Description**:
Implement real-time response streaming using Server-Sent Events (SSE) to display ChatGPT responses as they are generated, providing a more engaging user experience.

**Technical Requirements**:
- Create new endpoint POST `/convo_turn/stream`
- Implement SSE response format
- Stream ChatGPT API responses token by token
- Handle connection drops and reconnection
- Buffer management for partial tokens
- Cleanup on client disconnect

**Implementation Details**:
```python
@app.route('/convo_turn/stream', methods=['POST'])
async def stream_conversation():
    def generate():
        # SSE format
        yield "event: start\n"
        yield f"data: {json.dumps({'sessionId': session_id})}\n\n"

        # Stream from ChatGPT
        for chunk in chatgpt_stream_response(messages):
            if chunk.choices[0].delta.content:
                yield "event: token\n"
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

        # Save complete response
        save_conversation(complete_response)

        yield "event: complete\n"
        yield f"data: {json.dumps({'messageId': message_id})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
```

**Client Integration Example**:
```javascript
const eventSource = new EventSource('/convo_turn/stream', {
    method: 'POST',
    body: JSON.stringify({ message, animalId })
});

eventSource.addEventListener('token', (e) => {
    const { content } = JSON.parse(e.data);
    appendToChat(content);
});

eventSource.addEventListener('complete', (e) => {
    const { messageId } = JSON.parse(e.data);
    markMessageComplete(messageId);
    eventSource.close();
});
```

**Acceptance Criteria**:
- [ ] GIVEN streaming endpoint called WHEN response generates THEN tokens stream in real-time
- [ ] GIVEN connection drops WHEN streaming THEN client can reconnect and continue
- [ ] GIVEN client disconnects WHEN streaming THEN server cleanup occurs
- [ ] GIVEN partial token received WHEN buffering THEN complete words are sent
- [ ] GIVEN streaming completes WHEN all tokens sent THEN complete event fires
- [ ] GIVEN error occurs during streaming WHEN processing THEN error event sent to client
- [ ] GIVEN multiple concurrent streams WHEN processing THEN all work independently

**Dependencies**:
- ChatGPT streaming API support
- WebSocket/SSE infrastructure
- Connection management

---

### Ticket 3: [Backend] Implement DynamoDB Conversation Storage
**Type**: Task
**Story Points**: 8
**Priority**: Critical
**Sprint**: 1

**Description**:
Design and implement DynamoDB schema for storing conversation history with efficient querying for session management and history retrieval.

**DynamoDB Schema**:
```yaml
Table: cmz-conversations
Partition Key: userId (String)
Sort Key: sessionId#timestamp (String)

Attributes:
  - userId: String (user who initiated conversation)
  - sessionId: String (UUID for conversation session)
  - timestamp: String (ISO-8601)
  - animalId: String (animal being chatted with)
  - messageType: String (user|assistant)
  - content: String (message content)
  - tokenCount: Number
  - parentUserId: String (if user is a child)
  - metadata: Map {
      latencyMs: Number,
      model: String,
      temperature: Number
    }

GSI1:
  Partition Key: sessionId
  Sort Key: timestamp

GSI2:
  Partition Key: animalId
  Sort Key: timestamp

GSI3:
  Partition Key: parentUserId
  Sort Key: timestamp
```

**Implementation Requirements**:
- Batch write for efficiency (25 items max)
- TTL for old conversations (90 days)
- Encryption at rest
- Point-in-time recovery enabled
- Auto-scaling configuration

**Storage Functions**:
```python
async def store_conversation_turn(
    user_id: str,
    session_id: str,
    animal_id: str,
    user_message: str,
    assistant_response: str,
    metadata: dict
):
    timestamp = datetime.utcnow().isoformat()

    # Batch write both messages
    items = [
        {
            'userId': user_id,
            'sessionId#timestamp': f"{session_id}#{timestamp}_user",
            'sessionId': session_id,
            'timestamp': timestamp,
            'animalId': animal_id,
            'messageType': 'user',
            'content': user_message,
            'parentUserId': get_parent_id(user_id)
        },
        {
            'userId': user_id,
            'sessionId#timestamp': f"{session_id}#{timestamp}_assistant",
            'sessionId': session_id,
            'timestamp': timestamp,
            'animalId': animal_id,
            'messageType': 'assistant',
            'content': assistant_response,
            'metadata': metadata,
            'parentUserId': get_parent_id(user_id)
        }
    ]

    await batch_write_items(items)
```

**Acceptance Criteria**:
- [ ] GIVEN conversation occurs WHEN saved THEN both user and assistant messages stored
- [ ] GIVEN sessionId provided WHEN queried THEN all messages in session return in order
- [ ] GIVEN userId queried WHEN fetching THEN all user's sessions return
- [ ] GIVEN parentUserId queried WHEN fetching THEN all children's conversations return
- [ ] GIVEN conversation older than 90 days WHEN TTL runs THEN conversation deleted
- [ ] GIVEN batch write fails WHEN retried THEN exponential backoff applied
- [ ] GIVEN high load WHEN writing THEN auto-scaling handles capacity

**Dependencies**:
- DynamoDB table creation
- IAM permissions
- TTL configuration

---

### Ticket 4: [Backend] Create Conversation Session List Endpoint
**Type**: Task
**Story Points**: 5
**Priority**: High
**Sprint**: 2

**Description**:
Create GET `/conversations/sessions` endpoint to retrieve a paginated list of conversation sessions for users to browse their chat history.

**Technical Requirements**:
- Query by userId with pagination
- Include session metadata (animal, message count, last activity)
- Support date range filtering
- Sort by most recent first
- Implement caching for performance

**API Specification**:
```yaml
GET /conversations/sessions
Query Parameters:
  - userId: string (required)
  - startDate: ISO-8601 (optional)
  - endDate: ISO-8601 (optional)
  - animalId: string (optional)
  - limit: number (default: 20, max: 100)
  - nextToken: string (pagination token)

Response:
{
  "sessions": [
    {
      "sessionId": "uuid",
      "animalId": "lion_001",
      "animalName": "Leo the Lion",
      "startTime": "2024-01-15T10:00:00Z",
      "lastActivity": "2024-01-15T10:15:00Z",
      "messageCount": 12,
      "firstMessage": "Hi Leo!",
      "lastMessage": "Thanks for teaching me about lions!"
    }
  ],
  "pagination": {
    "nextToken": "encoded_token",
    "hasMore": true,
    "totalSessions": 45
  }
}
```

**Implementation**:
```python
async def get_user_sessions(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    animal_id: Optional[str] = None,
    limit: int = 20,
    next_token: Optional[str] = None
):
    # Query DynamoDB for sessions
    query_params = {
        'KeyConditionExpression': 'userId = :uid',
        'ExpressionAttributeValues': {':uid': user_id},
        'ScanIndexForward': False,  # Most recent first
        'Limit': limit
    }

    if next_token:
        query_params['ExclusiveStartKey'] = decode_token(next_token)

    # Add date filtering if provided
    if start_date or end_date:
        add_date_filter(query_params, start_date, end_date)

    result = await dynamodb.query(**query_params)

    # Group by sessionId and enhance with metadata
    sessions = group_and_enhance_sessions(result['Items'])

    return {
        'sessions': sessions,
        'pagination': {
            'nextToken': encode_token(result.get('LastEvaluatedKey')),
            'hasMore': 'LastEvaluatedKey' in result
        }
    }
```

**Acceptance Criteria**:
- [ ] GIVEN userId WHEN sessions requested THEN all user's sessions return paginated
- [ ] GIVEN date range WHEN filtered THEN only sessions in range return
- [ ] GIVEN animalId filter WHEN applied THEN only sessions with that animal return
- [ ] GIVEN pagination token WHEN provided THEN next page of results return
- [ ] GIVEN no sessions exist WHEN requested THEN empty array with proper structure returns
- [ ] GIVEN sessions requested WHEN sorted THEN most recent sessions appear first
- [ ] GIVEN large result set WHEN requested THEN maximum 100 items return

**Dependencies**:
- DynamoDB query optimization
- Pagination token encryption
- Session aggregation logic

---

### Ticket 5: [Backend] Implement Role-Based Access Control for History
**Type**: Task
**Story Points**: 8
**Priority**: Critical
**Sprint**: 2

**Description**:
Implement comprehensive role-based access control to ensure users can only view appropriate conversation histories based on their role and relationships.

**Access Rules**:
```yaml
Visitor:
  - No access to any conversation history

User (Authenticated):
  - View own conversations only
  - Cannot view others' conversations

Parent:
  - View own conversations
  - View all children's conversations
  - Cannot view other families' conversations

Zookeeper:
  - View all conversations
  - Read-only access
  - Can filter by date, user, animal

Administrator:
  - Full access to all conversations
  - Can delete conversations
  - Can export conversation data
```

**Implementation**:
```python
from enum import Enum
from typing import List, Optional

class UserRole(Enum):
    VISITOR = "visitor"
    USER = "user"
    PARENT = "parent"
    ZOOKEEPER = "zookeeper"
    ADMINISTRATOR = "administrator"

async def check_conversation_access(
    requesting_user_id: str,
    target_user_id: str,
    action: str = "read"
) -> bool:
    """
    Check if requesting user can access target user's conversations
    """
    # Get requesting user details
    user = await get_user(requesting_user_id)

    # Administrators and zookeepers have universal read access
    if user.role in [UserRole.ADMINISTRATOR, UserRole.ZOOKEEPER]:
        return action == "read" or user.role == UserRole.ADMINISTRATOR

    # Users can only see their own conversations
    if user.role == UserRole.USER:
        return requesting_user_id == target_user_id

    # Parents can see their own and children's conversations
    if user.role == UserRole.PARENT:
        if requesting_user_id == target_user_id:
            return True

        # Check if target is a child
        children = await get_children_ids(requesting_user_id)
        return target_user_id in children

    # Visitors have no access
    return False

# Middleware for endpoints
async def authorize_conversation_access():
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            requesting_user = get_current_user()
            target_user = request.args.get('userId')

            if not await check_conversation_access(
                requesting_user.id,
                target_user,
                request.method.lower()
            ):
                return {'error': 'Forbidden', 'code': 403}, 403

            return await f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Database Queries by Role**:
```python
async def get_accessible_conversations(user_id: str, user_role: UserRole):
    if user_role == UserRole.ADMINISTRATOR:
        # No filtering needed
        return query_all_conversations()

    elif user_role == UserRole.ZOOKEEPER:
        # Read-only access to all
        return query_all_conversations(read_only=True)

    elif user_role == UserRole.PARENT:
        # Get parent's and children's conversations
        children_ids = await get_children_ids(user_id)
        user_ids = [user_id] + children_ids
        return query_conversations_for_users(user_ids)

    elif user_role == UserRole.USER:
        # Only own conversations
        return query_conversations_for_users([user_id])

    else:  # VISITOR
        return []
```

**Acceptance Criteria**:
- [ ] GIVEN visitor role WHEN accessing history THEN 403 Forbidden returns
- [ ] GIVEN user role WHEN accessing own history THEN conversations return successfully
- [ ] GIVEN user role WHEN accessing others' history THEN 403 Forbidden returns
- [ ] GIVEN parent role WHEN accessing child's history THEN conversations return successfully
- [ ] GIVEN parent role WHEN accessing non-child's history THEN 403 Forbidden returns
- [ ] GIVEN zookeeper role WHEN accessing any history THEN read-only access granted
- [ ] GIVEN admin role WHEN accessing any history THEN full access granted
- [ ] GIVEN invalid role WHEN accessing history THEN 403 Forbidden returns

**Dependencies**:
- User role management system
- Family relationship data
- Authentication middleware

---

### Ticket 6: [Backend] Implement Conversation History Retrieval Endpoint
**Type**: Task
**Story Points**: 5
**Priority**: High
**Sprint**: 2

**Description**:
Create GET `/conversations/history/{sessionId}` endpoint to retrieve complete conversation history for a specific session with proper access controls.

**API Specification**:
```yaml
GET /conversations/history/{sessionId}
Headers:
  - Authorization: Bearer {token}

Response:
{
  "sessionId": "uuid",
  "userId": "user_001",
  "animalId": "lion_001",
  "animalName": "Leo the Lion",
  "startTime": "2024-01-15T10:00:00Z",
  "endTime": "2024-01-15T10:15:00Z",
  "messages": [
    {
      "messageId": "msg_001",
      "timestamp": "2024-01-15T10:00:00Z",
      "sender": "user",
      "content": "Hi Leo! What do you eat?",
      "metadata": {}
    },
    {
      "messageId": "msg_002",
      "timestamp": "2024-01-15T10:00:05Z",
      "sender": "assistant",
      "content": "Hello! I'm Leo the lion. In the wild, lions like me are carnivores...",
      "metadata": {
        "tokensUsed": 45,
        "latencyMs": 320
      }
    }
  ],
  "statistics": {
    "totalMessages": 12,
    "userMessages": 6,
    "assistantMessages": 6,
    "totalTokens": 520,
    "averageResponseTime": 285
  }
}
```

**Implementation**:
```python
async def get_conversation_history(
    session_id: str,
    requesting_user_id: str
) -> dict:
    # Get session metadata
    session = await get_session_metadata(session_id)

    # Check access permissions
    if not await check_conversation_access(
        requesting_user_id,
        session['userId'],
        'read'
    ):
        raise ForbiddenError("Access denied to this conversation")

    # Query all messages in session
    messages = await query_session_messages(session_id)

    # Calculate statistics
    stats = calculate_conversation_stats(messages)

    # Get animal info
    animal = await get_animal_info(session['animalId'])

    return {
        'sessionId': session_id,
        'userId': session['userId'],
        'animalId': session['animalId'],
        'animalName': animal['name'],
        'startTime': messages[0]['timestamp'] if messages else None,
        'endTime': messages[-1]['timestamp'] if messages else None,
        'messages': messages,
        'statistics': stats
    }
```

**Acceptance Criteria**:
- [ ] GIVEN valid sessionId WHEN history requested THEN all messages return in order
- [ ] GIVEN user owns session WHEN requested THEN full history returns
- [ ] GIVEN parent requests child's session WHEN requested THEN full history returns
- [ ] GIVEN user requests others' session WHEN requested THEN 403 Forbidden returns
- [ ] GIVEN session doesn't exist WHEN requested THEN 404 Not Found returns
- [ ] GIVEN large conversation WHEN requested THEN paginated response returns
- [ ] GIVEN statistics requested WHEN returned THEN accurate calculations provided

**Dependencies**:
- Session metadata storage
- Message aggregation
- Statistics calculation

---

## Frontend Tickets (Using 21st.dev)

### Ticket 7: [Frontend] Create Chat History List Page with 21st.dev
**Type**: Task
**Story Points**: 8
**Priority**: High
**Sprint**: 2

**Description**:
Create a chat history list page using 21st.dev components that displays all accessible conversation sessions with filtering and search capabilities.

**21st.dev Component Requirements**:
- Use 21st.dev data table component for session list
- Implement filter sidebar with date range picker
- Add search bar for finding specific conversations
- Include animal avatar badges
- Responsive design for mobile/tablet/desktop

**UI Specifications**:
```typescript
interface ChatHistoryListPage {
  components: {
    header: "Chat History" with user info;
    filterSidebar: {
      dateRangePicker: DateRange;
      animalFilter: MultiSelect;
      searchBox: TextInput;
    };
    sessionList: DataTable<ConversationSession>;
    pagination: PaginationControls;
  };

  features: {
    sorting: "date" | "animal" | "messageCount";
    rowClick: NavigateToConversation;
    emptyState: IllustratedMessage;
    loadingState: SkeletonRows;
  };
}
```

**21st.dev Integration**:
```typescript
// Use 21st.dev CLI to generate base component
// Command: /ui create chat-history-list with data table, filters, and pagination

import { DataTable, FilterPanel, DateRangePicker } from '@21st/components';

const ChatHistoryList = () => {
  const [sessions, setSessions] = useState([]);
  const [filters, setFilters] = useState({});

  return (
    <div className="chat-history-container">
      <FilterPanel position="left">
        <DateRangePicker onChange={setFilters} />
        <AnimalMultiSelect animals={availableAnimals} />
      </FilterPanel>

      <DataTable
        data={sessions}
        columns={[
          { key: 'animalName', header: 'Animal', sortable: true },
          { key: 'startTime', header: 'Date', sortable: true },
          { key: 'messageCount', header: 'Messages' },
          { key: 'duration', header: 'Duration' }
        ]}
        onRowClick={navigateToConversation}
        emptyState={<EmptyConversations />}
      />
    </div>
  );
};
```

**Acceptance Criteria**:
- [ ] GIVEN user navigates to history WHEN page loads THEN session list displays
- [ ] GIVEN user applies date filter WHEN submitted THEN list updates with filtered results
- [ ] GIVEN user searches for text WHEN typing THEN list filters in real-time
- [ ] GIVEN user clicks session row WHEN selected THEN navigation to conversation occurs
- [ ] GIVEN no sessions exist WHEN viewing THEN friendly empty state displays
- [ ] GIVEN parent views history WHEN loaded THEN children's sessions show with indicators
- [ ] GIVEN mobile device WHEN viewing THEN responsive layout adapts appropriately

**Dependencies**:
- 21st.dev component library setup
- API integration for session list
- Routing configuration

---

### Ticket 8: [Frontend] Create Conversation Viewer Page with 21st.dev
**Type**: Task
**Story Points**: 8
**Priority**: High
**Sprint**: 3

**Description**:
Build a conversation viewer page using 21st.dev chat components to display historical conversations with proper formatting and metadata.

**21st.dev Component Requirements**:
- Use 21st.dev chat/message components
- Implement message bubbles with sender identification
- Add timestamp displays
- Include animal avatar in header
- Support message metadata tooltips

**UI Specifications**:
```typescript
interface ConversationViewer {
  layout: {
    header: {
      animalAvatar: Image;
      animalName: Text;
      sessionDate: DateTime;
      backButton: IconButton;
    };

    messageArea: {
      messages: ChatMessage[];
      layout: "bubble" | "timeline";
      showTimestamps: boolean;
      showMetadata: boolean;
    };

    footer: {
      statistics: ConversationStats;
      exportButton: Button;
      shareButton: Button;
    };
  };
}
```

**21st.dev Implementation**:
```typescript
// Command: /ui create conversation-viewer with chat messages and metadata

import { ChatMessage, ChatContainer, Avatar } from '@21st/components';

const ConversationViewer = ({ sessionId }) => {
  const { messages, metadata } = useConversation(sessionId);

  return (
    <ChatContainer>
      <ChatHeader>
        <Avatar src={metadata.animalAvatar} />
        <Title>{metadata.animalName}</Title>
        <Subtitle>{formatDate(metadata.startTime)}</Subtitle>
      </ChatHeader>

      <MessageList>
        {messages.map(msg => (
          <ChatMessage
            key={msg.messageId}
            sender={msg.sender}
            content={msg.content}
            timestamp={msg.timestamp}
            align={msg.sender === 'user' ? 'right' : 'left'}
            avatar={msg.sender === 'assistant' ? metadata.animalAvatar : null}
          />
        ))}
      </MessageList>

      <ConversationFooter>
        <Stats {...calculateStats(messages)} />
        <ExportButton onClick={exportConversation} />
      </ConversationFooter>
    </ChatContainer>
  );
};
```

**Features**:
- Smooth scrolling to latest message
- Lazy loading for long conversations
- Print-friendly layout option
- Export to PDF/Text
- Share via link (with permissions)

**Acceptance Criteria**:
- [ ] GIVEN sessionId WHEN page loads THEN all messages display in order
- [ ] GIVEN user messages WHEN displayed THEN appear on right with user styling
- [ ] GIVEN assistant messages WHEN displayed THEN appear on left with animal avatar
- [ ] GIVEN timestamp hover WHEN activated THEN detailed time information shows
- [ ] GIVEN export clicked WHEN processed THEN PDF/text file downloads
- [ ] GIVEN print initiated WHEN processed THEN print-friendly layout renders
- [ ] GIVEN unauthorized access WHEN attempted THEN error message displays
- [ ] GIVEN long conversation WHEN viewed THEN smooth scrolling and pagination work

**Dependencies**:
- 21st.dev chat components
- Export functionality
- Print CSS styles

---

### Ticket 9: [Frontend] Implement Real-time Chat Streaming UI with 21st.dev
**Type**: Task
**Story Points**: 10
**Priority**: Critical
**Sprint**: 1

**Description**:
Enhance the chat interface to support real-time streaming responses using Server-Sent Events, displaying text as it's generated by ChatGPT.

**21st.dev Component Requirements**:
- Use 21st.dev streaming text component
- Implement typing indicator animation
- Add message status indicators
- Support partial message rendering
- Handle connection status

**Streaming Implementation**:
```typescript
// Command: /ui create streaming-chat with real-time text and typing indicators

import { StreamingMessage, TypingIndicator } from '@21st/components';

const StreamingChat = ({ animalId }) => {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [partialMessage, setPartialMessage] = useState('');

  const sendMessage = async (content: string) => {
    // Add user message
    const userMessage = { sender: 'user', content, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);

    // Start streaming
    setStreaming(true);
    const eventSource = new EventSource('/convo_turn/stream', {
      method: 'POST',
      body: JSON.stringify({ message: content, animalId })
    });

    let assistantMessage = '';

    eventSource.addEventListener('token', (e) => {
      const { content } = JSON.parse(e.data);
      assistantMessage += content;
      setPartialMessage(assistantMessage);
    });

    eventSource.addEventListener('complete', (e) => {
      const { messageId } = JSON.parse(e.data);
      setMessages(prev => [...prev, {
        messageId,
        sender: 'assistant',
        content: assistantMessage,
        timestamp: new Date()
      }]);
      setPartialMessage('');
      setStreaming(false);
      eventSource.close();
    });

    eventSource.addEventListener('error', (e) => {
      console.error('Streaming error:', e);
      setStreaming(false);
      eventSource.close();
    });
  };

  return (
    <ChatInterface>
      <MessageList>
        {messages.map(msg => (
          <ChatMessage key={msg.timestamp} {...msg} />
        ))}

        {streaming && (
          <StreamingMessage
            content={partialMessage}
            showCursor={true}
            avatar={animalAvatar}
          />
        )}

        {streaming && !partialMessage && (
          <TypingIndicator avatar={animalAvatar} />
        )}
      </MessageList>

      <MessageInput
        onSend={sendMessage}
        disabled={streaming}
        placeholder={streaming ? "Waiting for response..." : "Type your message..."}
      />
    </ChatInterface>
  );
};
```

**UI Features**:
- Smooth text appearance animation
- Blinking cursor during streaming
- Connection status indicator
- Retry mechanism for failed streams
- Cancel streaming button

**Acceptance Criteria**:
- [ ] GIVEN message sent WHEN streaming starts THEN typing indicator appears
- [ ] GIVEN response streams WHEN tokens arrive THEN text appears character by character
- [ ] GIVEN streaming active WHEN displayed THEN cursor blinks at end of text
- [ ] GIVEN connection drops WHEN streaming THEN reconnection attempted automatically
- [ ] GIVEN user navigates away WHEN streaming THEN stream properly closes
- [ ] GIVEN error occurs WHEN streaming THEN error message displays with retry option
- [ ] GIVEN streaming completes WHEN finished THEN full message renders normally
- [ ] GIVEN multiple messages stream WHEN concurrent THEN each maintains own state

**Dependencies**:
- SSE client implementation
- 21st.dev streaming components
- Connection management

---

### Ticket 10: [Frontend] Add Family View for Parent History Access with 21st.dev
**Type**: Task
**Story Points**: 5
**Priority**: Medium
**Sprint**: 3

**Description**:
Create a family-oriented view for parents to monitor their children's conversations using 21st.dev family/group components.

**21st.dev Component Requirements**:
- Use 21st.dev tab/accordion components for child separation
- Implement family member selector
- Add child safety indicators
- Include parental controls

**UI Specification**:
```typescript
// Command: /ui create family-chat-history with tabs and child selectors

interface FamilyChatHistory {
  layout: {
    header: "Family Chat History";

    childSelector: TabGroup<Child> | Dropdown<Child>;

    viewModes: {
      combined: "All Family Conversations";
      individual: "View by Family Member";
    };

    conversationList: {
      childIndicator: Badge;
      animalInfo: AvatarGroup;
      safetyScore: ProgressBar;
      lastActive: RelativeTime;
    };
  };
}
```

**Implementation**:
```typescript
import { Tabs, TabPanel, Badge, AvatarGroup } from '@21st/components';

const FamilyChatHistory = () => {
  const { children, conversations } = useFamilyData();

  return (
    <div className="family-history">
      <Tabs defaultValue="all">
        <TabList>
          <Tab value="all">All Family</Tab>
          {children.map(child => (
            <Tab key={child.id} value={child.id}>
              {child.name}
              {child.hasNewMessages && <Badge variant="dot" />}
            </Tab>
          ))}
        </TabList>

        <TabPanels>
          <TabPanel value="all">
            <CombinedFamilyView conversations={conversations} />
          </TabPanel>

          {children.map(child => (
            <TabPanel key={child.id} value={child.id}>
              <ChildConversations
                childId={child.id}
                conversations={filterByChild(conversations, child.id)}
              />
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>

      <ParentalInsights>
        <EngagementChart data={engagementData} />
        <PopularAnimals animals={topAnimals} />
        <LearningTopics topics={educationalTopics} />
      </ParentalInsights>
    </div>
  );
};
```

**Acceptance Criteria**:
- [ ] GIVEN parent logs in WHEN viewing history THEN all family conversations display
- [ ] GIVEN parent selects child WHEN filtered THEN only that child's conversations show
- [ ] GIVEN child has new messages WHEN displayed THEN notification badge appears
- [ ] GIVEN parent views conversation WHEN opened THEN child name clearly indicated
- [ ] GIVEN safety concern detected WHEN displayed THEN appropriate indicator shows
- [ ] GIVEN parent clicks insights WHEN viewed THEN engagement metrics display
- [ ] GIVEN export requested WHEN processed THEN family report generates

**Dependencies**:
- Family relationship data
- 21st.dev tab components
- Analytics aggregation

---

## Security & Compliance Tickets

### Ticket 11: [Security] Implement Audit Logging for Conversation Access
**Type**: Task
**Story Points**: 5
**Priority**: High
**Sprint**: 3

**Description**:
Implement comprehensive audit logging for all conversation history access to ensure compliance and security monitoring.

**Audit Requirements**:
```yaml
Log Events:
  - conversation_viewed
  - conversation_exported
  - conversation_shared
  - conversation_deleted
  - unauthorized_access_attempt

Log Data:
  - timestamp
  - userId (who accessed)
  - targetUserId (whose conversation)
  - sessionId
  - action
  - ipAddress
  - userAgent
  - result (success/failure)
  - reason (for failures)
```

**Implementation**:
```python
import json
from datetime import datetime

class ConversationAuditLogger:
    def __init__(self, dynamo_table):
        self.table = dynamo_table

    async def log_access(
        self,
        event_type: str,
        user_id: str,
        target_user_id: str,
        session_id: str,
        success: bool,
        metadata: dict = None
    ):
        log_entry = {
            'logId': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'eventType': event_type,
            'userId': user_id,
            'targetUserId': target_user_id,
            'sessionId': session_id,
            'success': success,
            'ipAddress': request.remote_addr,
            'userAgent': request.user_agent.string,
            'metadata': metadata or {}
        }

        # Store in DynamoDB
        await self.table.put_item(Item=log_entry)

        # Alert on suspicious activity
        if not success or event_type == 'unauthorized_access_attempt':
            await self.alert_security_team(log_entry)

    async def get_audit_trail(
        self,
        user_id: str = None,
        session_id: str = None,
        start_date: str = None,
        end_date: str = None
    ):
        # Query audit logs with filters
        pass
```

**Acceptance Criteria**:
- [ ] GIVEN conversation accessed WHEN logged THEN all required fields captured
- [ ] GIVEN unauthorized attempt WHEN logged THEN security alert triggered
- [ ] GIVEN export performed WHEN logged THEN full export details recorded
- [ ] GIVEN audit query WHEN requested THEN filtered results return
- [ ] GIVEN suspicious pattern WHEN detected THEN automated alert sent
- [ ] GIVEN compliance audit WHEN performed THEN complete trail available
- [ ] GIVEN logs older than 1 year WHEN archived THEN moved to cold storage

**Dependencies**:
- Audit table setup
- Alert system integration
- Compliance requirements

---

### Ticket 12: [Security] Implement Data Privacy Controls
**Type**: Task
**Story Points**: 5
**Priority**: High
**Sprint**: 3

**Description**:
Implement privacy controls including data retention, deletion, and anonymization capabilities for COPPA and GDPR compliance.

**Privacy Features**:
- Auto-deletion after retention period
- User-requested data deletion
- Data export for portability
- Conversation anonymization
- PII detection and masking

**Implementation**:
```python
class PrivacyManager:
    async def delete_user_conversations(self, user_id: str, reason: str):
        """
        Complete deletion of user's conversation history
        """
        # Get all conversations
        conversations = await get_all_user_conversations(user_id)

        # Log deletion request
        await audit_log.log_deletion_request(user_id, reason, len(conversations))

        # Batch delete from DynamoDB
        for batch in chunk(conversations, 25):
            await batch_delete_items(batch)

        # Update user record
        await update_user_privacy_status(user_id, 'conversations_deleted')

        return {'deleted': len(conversations), 'timestamp': datetime.utcnow()}

    async def anonymize_conversation(self, session_id: str):
        """
        Replace PII with anonymized values
        """
        messages = await get_session_messages(session_id)

        for message in messages:
            # Detect and replace PII
            message['content'] = detect_and_mask_pii(message['content'])
            message['userId'] = hash_user_id(message['userId'])

        await update_messages(messages)

    async def export_user_data(self, user_id: str) -> bytes:
        """
        GDPR-compliant data export
        """
        data = {
            'conversations': await get_all_user_conversations(user_id),
            'profile': await get_user_profile(user_id),
            'exportDate': datetime.utcnow().isoformat()
        }

        return json.dumps(data, indent=2).encode('utf-8')
```

**Acceptance Criteria**:
- [ ] GIVEN deletion requested WHEN processed THEN all conversations removed
- [ ] GIVEN retention period expired WHEN job runs THEN old conversations deleted
- [ ] GIVEN export requested WHEN processed THEN complete data package provided
- [ ] GIVEN PII detected WHEN anonymizing THEN properly masked in storage
- [ ] GIVEN child account WHEN accessed THEN COPPA compliance maintained
- [ ] GIVEN deletion completed WHEN verified THEN no data recoverable

**Dependencies**:
- PII detection library
- Data retention policies
- Compliance requirements

---

## Infrastructure & Testing Tickets

### Ticket 13: [Infrastructure] Setup DynamoDB Tables and Indexes
**Type**: Task
**Story Points**: 3
**Priority**: Critical
**Sprint**: 1

**Description**:
Create and configure DynamoDB tables for conversation storage with appropriate indexes, scaling, and backup policies.

**Table Configuration**:
```yaml
TableName: cmz-conversations
BillingMode: PAY_PER_REQUEST
PointInTimeRecoveryEnabled: true
SSESpecification:
  SSEEnabled: true
  SSEType: KMS
  KMSMasterKeyId: alias/cmz-conversations

StreamSpecification:
  StreamEnabled: true
  StreamViewType: NEW_AND_OLD_IMAGES

GlobalSecondaryIndexes:
  - IndexName: SessionIndex
    Keys:
      PartitionKey: sessionId
      SortKey: timestamp
    Projection: ALL

  - IndexName: AnimalIndex
    Keys:
      PartitionKey: animalId
      SortKey: timestamp
    Projection: KEYS_ONLY

  - IndexName: ParentIndex
    Keys:
      PartitionKey: parentUserId
      SortKey: timestamp
    Projection: ALL

TimeToLiveSpecification:
  AttributeName: ttl
  Enabled: true

Tags:
  - Environment: production
  - Application: cmz-chatbots
  - DataClassification: sensitive
```

**Acceptance Criteria**:
- [ ] GIVEN table created WHEN verified THEN all indexes properly configured
- [ ] GIVEN encryption enabled WHEN checked THEN KMS key properly applied
- [ ] GIVEN backup enabled WHEN tested THEN point-in-time recovery works
- [ ] GIVEN TTL configured WHEN tested THEN old records auto-delete
- [ ] GIVEN high load WHEN tested THEN auto-scaling handles traffic
- [ ] GIVEN stream enabled WHEN tested THEN changes captured correctly

**Dependencies**:
- AWS account permissions
- KMS key creation
- Backup strategy

---

### Ticket 14: [Testing] E2E Tests for Complete Chat Flow
**Type**: Test
**Story Points**: 8
**Priority**: High
**Sprint**: 4

**Description**:
Create comprehensive end-to-end tests covering the entire chat flow from initiation through history viewing with all permission scenarios.

**Test Scenarios**:
```javascript
// Playwright E2E tests
describe('Chat with Animals E2E', () => {
  test('Complete chat flow with streaming', async ({ page }) => {
    // 1. Login as user
    await loginAs(page, 'student1@test.cmz.org');

    // 2. Navigate to animals
    await page.goto('/dashboard/conversations/animals');

    // 3. Select an animal
    await page.click('[data-animal="lion_001"]');

    // 4. Send message
    await page.fill('[data-testid="message-input"]', 'Hello Leo!');
    await page.click('[data-testid="send-button"]');

    // 5. Verify streaming response
    await expect(page.locator('[data-testid="typing-indicator"]')).toBeVisible();
    await expect(page.locator('[data-testid="assistant-message"]')).toContainText('Hello!');

    // 6. Navigate to history
    await page.goto('/dashboard/conversations/history');

    // 7. Verify session appears
    await expect(page.locator('[data-session]').first()).toContainText('Leo the Lion');

    // 8. View conversation
    await page.click('[data-session]');
    await expect(page.locator('[data-message]')).toHaveCount(2);
  });

  test('Parent views child conversation', async ({ page }) => {
    // Parent access scenario
  });

  test('Unauthorized access blocked', async ({ page }) => {
    // Security test
  });

  test('Export conversation to PDF', async ({ page }) => {
    // Export functionality
  });
});
```

**Test Coverage Requirements**:
- Happy path chat flow (send, receive, view)
- Streaming message reception
- Error handling (network, timeout)
- Permission scenarios (user, parent, admin)
- Export and share functionality
- Mobile responsive behavior
- Performance under load
- Accessibility compliance

**Acceptance Criteria**:
- [ ] GIVEN E2E tests run WHEN completed THEN >90% scenarios pass
- [ ] GIVEN streaming tested WHEN messages flow THEN real-time updates verify
- [ ] GIVEN permissions tested WHEN validated THEN all roles work correctly
- [ ] GIVEN mobile tested WHEN executed THEN responsive design confirmed
- [ ] GIVEN load tested WHEN stressed THEN system remains responsive
- [ ] GIVEN accessibility tested WHEN scanned THEN WCAG 2.1 AA compliance

**Dependencies**:
- Test data setup
- Test environment
- Playwright configuration

---

## Summary

### Epic Metrics
- **Total Story Points**: 89 points
- **Duration**: 3-4 sprints (6-8 weeks)
- **Team Size**: 2-3 developers (1 backend, 1 frontend, 1 full-stack)

### Sprint Breakdown

**Sprint 1 (Critical Path - 24 points)**:
- Ticket 1: ChatGPT Integration (8 pts)
- Ticket 2: Response Streaming (13 pts)
- Ticket 3: DynamoDB Storage (8 pts)
- Ticket 13: Infrastructure Setup (3 pts)
- Ticket 9: Streaming UI (10 pts) - Start

**Sprint 2 (History & Access - 26 points)**:
- Ticket 9: Streaming UI (continued)
- Ticket 4: Session List Endpoint (5 pts)
- Ticket 5: Role-Based Access (8 pts)
- Ticket 6: History Retrieval (5 pts)
- Ticket 7: History List UI (8 pts)

**Sprint 3 (Polish & Security - 23 points)**:
- Ticket 8: Conversation Viewer UI (8 pts)
- Ticket 10: Family View UI (5 pts)
- Ticket 11: Audit Logging (5 pts)
- Ticket 12: Privacy Controls (5 pts)

**Sprint 4 (Testing & Optimization - 8 points)**:
- Ticket 14: E2E Testing (8 pts)
- Performance optimization
- Bug fixes
- Documentation

### Risk Factors
1. **ChatGPT API Integration Complexity**: Rate limiting, cost management
2. **Real-time Streaming Reliability**: Connection management, error recovery
3. **Permission System Complexity**: Family relationships, role interactions
4. **Performance at Scale**: Large conversation history, concurrent users
5. **Compliance Requirements**: COPPA, GDPR, data retention

### Success Criteria
- Real-time chat with animal personalities working smoothly
- Complete conversation history with proper access controls
- Parent visibility into children's conversations
- Audit trail for compliance
- Performance targets met (<500ms response time)
- Security requirements satisfied

### Dependencies
- OpenAI API access and credentials
- DynamoDB tables provisioned
- Authentication system integrated
- Family relationships established
- 21st.dev components configured