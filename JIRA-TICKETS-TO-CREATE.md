# Jira Tickets to Create for Chat Features

## Summary
The Jira API requires project-specific fields (like "Billable") that prevent automatic ticket creation. Please create these tickets manually in Jira with the following details.

## Files with Full Specifications
1. **CHAT-WITH-ANIMALS-JIRA-TICKETS.md** - Initial animal chat interface (10 tickets, 41 story points)
2. **CHAT-HISTORY-EPIC.md** - Comprehensive chat history functionality (14 tickets, 89 story points)

## Quick Reference List - Chat History Epic Tickets

### Epic
**[EPIC] Chat and Chat History Functionality**
- Type: Epic/Task
- Priority: High
- Story Points: 89 total
- Duration: 3-4 sprints

### Sprint 1 - Critical Path (32 points)
1. **[Infrastructure] Setup DynamoDB Tables and Indexes** - 3 pts - Highest
2. **[Backend] Implement ChatGPT Integration with Animal Personalities** - 8 pts - Highest
3. **[Backend] Implement Response Streaming with Server-Sent Events** - 13 pts - Highest
4. **[Backend] Implement DynamoDB Conversation Storage** - 8 pts - Highest

### Sprint 2 - History & Access (34 points)
5. **[Frontend] Implement Real-time Chat Streaming UI with 21st.dev** - 10 pts - Highest
6. **[Backend] Create Conversation Session List Endpoint** - 5 pts - High
7. **[Backend] Implement Role-Based Access Control for History** - 8 pts - Highest
8. **[Backend] Implement Conversation History Retrieval Endpoint** - 5 pts - High
9. **[Frontend] Create Chat History List Page with 21st.dev** - 8 pts - High

### Sprint 3 - Polish & Security (23 points)
10. **[Frontend] Create Conversation Viewer Page with 21st.dev** - 8 pts - High
11. **[Frontend] Add Family View for Parent History Access with 21st.dev** - 5 pts - Medium
12. **[Security] Implement Audit Logging for Conversation Access** - 5 pts - High
13. **[Security] Implement Data Privacy Controls** - 5 pts - High

### Sprint 4 - Testing (8 points)
14. **[Testing] E2E Tests for Complete Chat Flow** - 8 pts - High

## Current Status

### ✅ Completed
- `/convo_turn` endpoint now returns "We're having a conversation!" (temporary implementation)
- Full ticket specifications documented with acceptance criteria
- Technical implementation details provided

### 📋 Ready for Manual Creation
All 14 tickets above need to be created in Jira with:
- Proper "Billable" field value
- Story points added to appropriate custom field
- Linked to epic
- Assigned to correct sprint

### 🚀 Ready to Implement After Ticket Creation
Once tickets are created in Jira, we can begin Sprint 1 implementation:
1. DynamoDB table setup
2. ChatGPT integration
3. Streaming response implementation
4. Basic chat UI with real-time updates

## Key Technical Decisions Made

### Backend Architecture
- **Streaming**: Server-Sent Events (SSE) for real-time responses
- **Storage**: DynamoDB with session-based partitioning
- **API Integration**: Direct ChatGPT API with animal-specific endpoints
- **Access Control**: Role-based with hierarchical permissions

### Frontend Architecture
- **UI Framework**: 21st.dev components for all interfaces
- **Streaming Client**: EventSource API for SSE
- **State Management**: React hooks with context for chat state
- **History Views**: Separate interfaces for users, parents, and admins

### Security Model
- **Visitor**: No history access
- **User**: Own conversations only
- **Parent**: Own + children's conversations
- **Zookeeper**: All conversations (read-only)
- **Administrator**: Full access including deletion

## Next Steps
1. Create all tickets manually in Jira
2. Assign tickets to sprints as outlined
3. Begin Sprint 1 implementation starting with DynamoDB setup
4. Set up ChatGPT API credentials and test connection
5. Implement basic streaming endpoint