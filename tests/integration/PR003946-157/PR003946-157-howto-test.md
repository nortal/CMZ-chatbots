# Test Instructions: Backend ChatGPT Integration with Animal Personalities

## Ticket Information
- **Ticket**: PR003946-157
- **Type**: Task
- **Priority**: Highest
- **Component**: Integration

## Test Objective
Validate ChatGPT API integration for animal personalities with proper system prompts, context management, and response generation.

## Prerequisites
- [ ] Backend services running on localhost:8080
- [ ] OpenAI API key configured (or mock mode enabled)
- [ ] Animal configurations in DynamoDB
- [ ] Python environment with aiohttp installed
- [ ] Environment variables loaded from .env.local

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
- Verify OpenAI API configuration or mock mode
- Load sample animal configuration
- Prepare test conversation context

### 2. Execution Phase
- Test system prompt generation for animals
- Verify ChatGPT API call functionality
- Test streaming response capability
- Validate conversation context handling
- Test error handling and fallback responses

### 3. Validation Phase
- Verify response format matches specifications
- Check token usage tracking
- Validate latency measurements
- Confirm animal personality in responses
- Test fallback when API unavailable

## Pass/Fail Criteria

### ✅ PASS Conditions:
- [ ] System prompts include animal personality traits
- [ ] ChatGPT API calls succeed or fallback gracefully
- [ ] Responses reflect animal character
- [ ] Token usage and latency tracked
- [ ] Streaming responses work correctly

### ❌ FAIL Conditions:
- [ ] System prompts missing personality elements
- [ ] API calls fail without fallback
- [ ] Responses don't match animal character
- [ ] Missing metadata (tokens, latency)
- [ ] Streaming fails or corrupts data

## Substeps and Multiple Test Scenarios

### Substep 1: Build Animal System Prompt
- **Test**: Generate prompt for lion with specific traits
- **Expected**: Prompt includes name, traits, knowledge areas
- **Pass Criteria**: Educational, friendly, in-character prompt

### Substep 2: Test Non-Streaming Response
- **Test**: Send message and get complete response
- **Expected**: Returns reply with metadata
- **Pass Criteria**: Response coherent, metadata complete

### Substep 3: Test Streaming Response
- **Test**: Stream response chunks via async generator
- **Expected**: Chunks arrive sequentially
- **Pass Criteria**: Complete message assembled correctly

### Substep 4: Test Fallback Response
- **Test**: Simulate API failure or missing key
- **Expected**: Returns friendly fallback message
- **Pass Criteria**: No errors exposed to user

## Evidence Collection
- System prompt examples for different animals
- API request/response payloads
- Token usage and latency metrics
- Streaming response chunks
- Fallback response examples

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: ChatGPT integration should handle all response modes
- **Expected Outcome**: Animal personalities reflected in responses
- **Variance Analysis**: Document response quality variations
- **Root Cause Assessment**: Analyze any API failures

## Test Commands
```python
# Test system prompt generation
from openapi_server.impl.utils.chatgpt_integration import ChatGPTIntegration
chatgpt = ChatGPTIntegration()

animal_config = {
    'name': 'Leo',
    'chatConfig': {
        'personality': {
            'traits': ['friendly', 'educational'],
            'knowledge': ['savanna facts', 'lion behavior']
        }
    }
}

prompt = chatgpt.build_animal_system_prompt(animal_config)
print(f"System Prompt: {prompt}")

# Test response generation (with mock if no API key)
import asyncio

async def test_response():
    response = await chatgpt.get_animal_response(
        animal_id='lion_001',
        user_message='Tell me about lions!',
        conversation_history=[],
        animal_config=animal_config
    )
    print(f"Response: {response}")

asyncio.run(test_response())
```

## Troubleshooting
### Common Issues and Solutions

**Issue**: OpenAI API key not configured
- **Solution**: System returns mock responses (expected behavior)
- **Check**: Set OPENAI_API_KEY environment variable for real responses

**Issue**: API rate limiting
- **Solution**: Implement retry logic with backoff
- **Check**: Monitor API usage and limits

**Issue**: Timeout errors
- **Solution**: Adjust timeout settings and max_tokens
- **Check**: Network connectivity and API status

---
*Generated: 2025-09-18*
*Test Category: Integration*
*CMZ TDD Framework v1.0*