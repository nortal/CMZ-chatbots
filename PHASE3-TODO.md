# Phase 3 Implementation - Pending Items

## conversation_dynamo.py Updates Needed

The updated conversation handler requires two new functions in `utils/conversation_dynamo.py`:

### 1. get_thread_id(session_id: str) -> Optional[str]
```python
def get_thread_id(session_id: str) -> Optional[str]:
    """
    Get OpenAI thread ID for a session

    Args:
        session_id: Conversation session ID

    Returns:
        Thread ID or None if not found
    """
    # Query DynamoDB conversations table for session
    # Return threadId field if exists
    pass
```

### 2. store_thread_id(session_id: str, thread_id: str) -> bool
```python
def store_thread_id(session_id: str, thread_id: str) -> bool:
    """
    Store OpenAI thread ID for a session

    Args:
        session_id: Conversation session ID
        thread_id: OpenAI thread ID

    Returns:
        True if successful
    """
    # Update DynamoDB conversations table
    # Add threadId field to session record
    pass
```

## DynamoDB Schema Update

The conversations table needs a new field:
- `threadId` (String) - OpenAI thread identifier for this session

## Next Steps for Phase 2 Completion

1. Update `utils/conversation_dynamo.py` with get_thread_id() and store_thread_id()
2. Update DynamoDB conversations table schema to include threadId field
3. Rebuild and deploy backend
4. Test conversation flow (T014-T015)

## Current Status

✅ conversation_assistants.py - Complete
✅ Conversation handler migration - Complete (with dependencies noted)
⏸️ conversation_dynamo.py updates - Pending
⏸️ Testing - Pending backend deployment

