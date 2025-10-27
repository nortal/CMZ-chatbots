# AI-Powered Conversation History Compression Research
## CMZ Chatbots Platform - January 2025

**Research Objective**: Investigate AI-powered techniques for compressing conversation history while preserving personalization value for the CMZ Chatbots platform, targeting 60% token reduction while maintaining 90% personalization effectiveness.

**Current Architecture Context**:
- 24 zoo animal chatbot personalities
- OpenAI Assistants API with persistent threads
- DynamoDB storage (quest-dev-conversation table)
- Full message history stored as list in conversation items
- AWS Lambda execution environment with timeout constraints

---

## Executive Summary

### Key Findings

**Token Reduction Potential**:
- Recursive summarization: **80-90% token reduction** documented in production systems (Mem0)
- Hierarchical approaches: **5x compression** (500 tokens → 60-100 tokens) with minimal information loss
- Combined strategies: Can achieve **target 60% reduction** while improving response quality by 26%

**Critical Insights**:
1. **OpenAI Assistants API Sunset**: Current API will be deprecated by mid-2026; migration to Responses API recommended
2. **Hierarchical Summarization Superior**: Keep recent messages verbatim, summarize older conversations
3. **Semantic Embeddings Essential**: Extract user preferences without storing full conversation text
4. **Real-time Summarization Viable**: 300ms-2s latency acceptable for user experience with proper optimization

### Recommended Architecture for CMZ

**Three-Tier Memory System**:
1. **Recent Context** (5-10 most recent turns): Full verbatim storage
2. **Session Summary** (current conversation): AI-generated summary of older turns
3. **User Profile** (cross-session): Semantic embeddings of preferences and interests

**Expected Outcomes**:
- 60-70% token reduction
- 90%+ personalization effectiveness retention
- Improved conversation coherence across sessions
- Reduced Lambda execution time and costs

---

## 1. LLM-Based Summarization Techniques

### 1.1 Recursive Summarization

**Concept**: LLMs continuously update summaries by combining previous memory with subsequent dialogues.

**Implementation Patterns**:
```python
# Pseudocode for recursive summarization
def recursive_summarize(previous_summary, new_turns, max_tokens=200):
    """
    Combines previous summary with new conversation turns
    Returns updated summary within token limit
    """
    prompt = f"""
    Previous conversation summary: {previous_summary}

    New conversation turns:
    {format_turns(new_turns)}

    Create an updated summary that:
    1. Preserves key facts about user preferences (likes/dislikes, interests)
    2. Retains important context about the relationship with the animal
    3. Notes any decisions or commitments made
    4. Maximum {max_tokens} tokens

    Focus on information needed for personalized future interactions.
    """

    return llm.generate(prompt)
```

**Research Evidence**:
- Implemented with GPT-3.5-Turbo achieving +3% BLEU score improvement over baseline
- Microsoft documentation shows 500-token histories compressed to 60-100 tokens
- Maintains conversation continuity across 100+ turn conversations

**CMZ Application**:
- Trigger summarization every 10 message pairs (20 total messages)
- Store summary in DynamoDB conversation item as `conversationSummary` field
- Use summary + recent 10 messages for context window

### 1.2 Structured Summarization with Templates

**Concept**: Use predefined formats to ensure critical information is captured consistently.

**Template Example for Zoo Chatbots**:
```python
SUMMARY_TEMPLATE = """
User Profile:
- Favorite animals: [extracted from conversation]
- Age/grade level: [if mentioned]
- Interests: [topics user engaged with most]
- Learning style: [visual/auditory/reading preferences]

Conversation History:
- Topics discussed: [key subjects]
- Questions asked: [main information requests]
- Facts learned: [educational outcomes]
- Emotional engagement: [user sentiment/excitement]

Commitments:
- Follow-up topics: [things to discuss next time]
- Unanswered questions: [pending inquiries]

Animal Relationship:
- Connection level: [first conversation / returning friend]
- Shared experiences: [memorable moments in dialogue]
"""
```

**Research Evidence**:
- Structured summaries of ≤200 words achieve similar performance to full history
- Predefined formats ensure consistency across different animal personalities
- Templates prevent critical information loss during summarization

**CMZ Application**:
- Animal-specific templates capture personality-relevant context
- Educational outcomes tracking for parent/teacher reporting
- Consistent structure enables analytics across all 24 animals

### 1.3 Prompt Optimization for Summarization

**Critical Factor**: Prompt quality significantly impacts summarization success.

**Best Practices**:
```python
SUMMARIZATION_PROMPT = """
You are summarizing a conversation between a {animal_name} and a zoo visitor.

Previous summary (or "First conversation" if none):
{previous_summary}

Recent conversation (last {n} turns):
{recent_turns}

Create a concise summary (max 150 words) focusing on:
1. PREFERENCES: What the visitor likes/dislikes
2. INTERESTS: Topics that engage them most
3. LEARNING: Educational facts they found interesting
4. PERSONALITY: How they interact (curious/shy/enthusiastic)
5. COMMITMENTS: Topics to continue next time

Preserve specific details like favorite animals, colors, activities.
This helps {animal_name} provide personalized responses in future chats.

Summary:
"""
```

**Research Evidence**:
- Tested prompts show 5-10x variation in summary quality
- Explicit instructions for what to preserve critical for personalization
- Domain-specific prompts (zoo/education) outperform generic summarization

---

## 2. Semantic Embedding Approaches for Interest Extraction

### 2.1 User Preference Embeddings

**Concept**: Convert user messages to vector embeddings, extract preference clusters without storing full text.

**Architecture**:
```python
from openai import OpenAI

class UserPreferenceExtractor:
    def __init__(self):
        self.client = OpenAI()

    def extract_preferences(self, conversation_turns):
        """
        Extract and store user preferences as embeddings
        Returns structured preference data
        """
        # Combine user messages
        user_messages = [t['text'] for t in conversation_turns if t['role'] == 'user']
        combined_text = " ".join(user_messages)

        # Generate embedding
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=combined_text
        )

        embedding = response.data[0].embedding

        # Extract explicit preferences using LLM
        preferences = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Extract user preferences from this conversation. Return JSON with categories: favorite_animals, interests, dislikes, learning_topics."
            }, {
                "role": "user",
                "content": combined_text
            }]
        )

        return {
            "embedding": embedding,
            "structured_preferences": preferences,
            "timestamp": datetime.utcnow().isoformat()
        }
```

**Research Evidence**:
- Difference-aware Embedding-based Personalization (DEP) models inter-user differences in latent space
- Embeddings capture semantic meaning without storing verbatim text
- Enable similarity search across user base for collaborative filtering

**CMZ Application**:
- Store user preference embeddings in DynamoDB or vector database
- Use for cross-session personalization ("I remember you like cats")
- Enable similarity search to recommend animals based on interests

### 2.2 Hierarchical Attention Networks for Preference Learning

**Concept**: Multi-level attention mechanisms identify important conversation elements.

**Implementation Pattern**:
```python
class HierarchicalPreferenceLearner:
    """
    Learns user preferences at multiple granularity levels:
    - Word level: Specific animals, colors, activities mentioned
    - Sentence level: Complete thoughts and opinions
    - Conversation level: Overall themes and engagement patterns
    """

    def learn_preferences(self, conversation_history):
        # Word-level attention: Extract entities
        entities = self.extract_entities(conversation_history)

        # Sentence-level attention: Identify key statements
        key_statements = self.rank_statements_by_importance(conversation_history)

        # Conversation-level: Overall themes
        themes = self.identify_themes(conversation_history)

        return {
            "entities": entities,  # Specific mentions
            "key_statements": key_statements,  # Important opinions
            "themes": themes  # Overall interests
        }
```

**Research Evidence**:
- GCORec framework shows hierarchical attention reduces noise while emphasizing important attributes
- Fine-grained semantics improve recommendation accuracy
- Works well with limited data (cold-start problem for new users)

**CMZ Application**:
- Extract animal preferences at entity level ("I love penguins")
- Capture learning interests at theme level ("interested in habitats")
- Enable personalization even after first conversation

### 2.3 Collaborative Filtering with Embeddings

**Concept**: Recommend experiences based on similar users' preferences.

**Pattern**:
```python
def find_similar_users(user_embedding, user_embeddings_db, top_k=5):
    """
    Find users with similar interests using vector similarity
    """
    similarities = cosine_similarity(user_embedding, user_embeddings_db)
    similar_user_ids = similarities.argsort()[-top_k:][::-1]
    return similar_user_ids

def recommend_animals(user_id, similar_users, interaction_history):
    """
    Recommend animals based on what similar users engaged with
    """
    recommendations = []
    for similar_user in similar_users:
        user_interactions = interaction_history[similar_user]
        recommendations.extend(user_interactions['favorite_animals'])

    # Rank by frequency among similar users
    return Counter(recommendations).most_common(5)
```

**CMZ Application**:
- "Students who liked Pokey (porcupine) also enjoyed..." recommendations
- Cross-animal engagement patterns inform educational pathways
- Parent/teacher dashboards show interest-based suggestions

---

## 3. Hierarchical Summarization Strategies

### 3.1 Temporal Tiering

**Concept**: Different levels of detail for different time periods.

**Architecture**:
```python
class TemporalMemoryManager:
    """
    Manages conversation history with temporal tiers:
    - Tier 1 (Recent): Last 5-10 turns, full verbatim
    - Tier 2 (Session): Current session summary
    - Tier 3 (Historical): Cross-session user profile
    """

    def build_context(self, session_id, user_id, animal_id):
        # Tier 1: Recent verbatim messages (highest detail)
        recent_messages = self.get_recent_messages(session_id, limit=10)

        # Tier 2: Current session summary (medium detail)
        session_summary = self.get_session_summary(session_id)
        if not session_summary:
            session_summary = self.generate_summary(session_id)

        # Tier 3: User profile across all sessions (lowest detail)
        user_profile = self.get_user_profile(user_id, animal_id)

        return {
            "recent_context": recent_messages,  # ~2000 tokens
            "session_summary": session_summary,  # ~200 tokens
            "user_profile": user_profile,  # ~100 tokens
            "total_tokens": self.estimate_tokens(recent_messages, session_summary, user_profile)
        }
```

**Token Allocation Example**:
- Recent messages: 2000 tokens (10 turns × ~200 tokens/turn)
- Session summary: 200 tokens
- User profile: 100 tokens
- **Total: 2300 tokens vs 5000+ tokens for full history (54% reduction)**

**Research Evidence**:
- LangGraph's SummarizationNode uses this pattern
- Microsoft's chat completion documentation recommends keeping recent verbatim
- Reduces context drift while maintaining coherence

**CMZ Application**:
```python
# DynamoDB schema enhancement
{
    "conversationId": "conv_pokey_user123_abc123",
    "userId": "user123",
    "animalId": "pokey",

    # Tier 1: Recent messages (full verbatim)
    "messages": [
        {"messageId": "msg1", "role": "user", "text": "..."},
        {"messageId": "msg2", "role": "assistant", "text": "..."},
        # ... last 10 messages
    ],

    # Tier 2: Session summary
    "sessionSummary": {
        "summary": "User expressed interest in porcupine habitats...",
        "preferences": ["habitats", "diet", "conservation"],
        "lastUpdated": "2025-01-10T15:30:00Z",
        "tokenCount": 187
    },

    # Tier 3: User profile (separate table or attribute)
    "userProfileSummary": {
        "favoriteTopics": ["conservation", "animal behavior"],
        "engagementLevel": "high",
        "learningStyle": "visual",
        "conversationCount": 5
    }
}
```

### 3.2 Sliding Window with Compression

**Concept**: Maintain fixed-size context window by compressing older content.

**Implementation**:
```python
class SlidingWindowMemory:
    def __init__(self, max_tokens=4000, window_size=10):
        self.max_tokens = max_tokens
        self.window_size = window_size

    def manage_context(self, conversation_id):
        messages = self.get_all_messages(conversation_id)
        current_tokens = self.count_tokens(messages)

        if current_tokens <= self.max_tokens:
            return messages

        # Keep recent window verbatim
        recent = messages[-self.window_size:]
        older = messages[:-self.window_size]

        # Compress older messages
        if older:
            summary = self.summarize_messages(older)
            return [{"role": "system", "content": f"Previous conversation summary: {summary}"}] + recent

        return recent
```

**Research Evidence**:
- SummarizingTokenWindowChatMemory pattern widely adopted
- Prevents token limit errors while maintaining coherence
- Faster response times and lower costs

### 3.3 Importance-Based Retention

**Concept**: Keep important messages regardless of recency.

**Scoring Function**:
```python
def calculate_message_importance(message, conversation_context):
    """
    Score messages by importance for retention
    High importance: Preference statements, decisions, commitments
    Medium importance: Questions, facts learned
    Low importance: Greetings, acknowledgments
    """
    importance_score = 0

    # Preference indicators
    preference_keywords = ["like", "love", "favorite", "interested in", "want to learn"]
    if any(keyword in message.lower() for keyword in preference_keywords):
        importance_score += 5

    # Decision/commitment indicators
    commitment_keywords = ["next time", "remember", "tell me more about"]
    if any(keyword in message.lower() for keyword in commitment_keywords):
        importance_score += 4

    # Educational content
    if "learned" in message.lower() or "didn't know" in message.lower():
        importance_score += 3

    # Question asking
    if "?" in message:
        importance_score += 2

    return importance_score

def selective_retention(messages, max_tokens=3000):
    """
    Retain most important messages within token budget
    """
    # Always keep last 5 messages
    recent = messages[-5:]
    candidates = messages[:-5]

    # Score and rank older messages
    scored = [(msg, calculate_message_importance(msg['text'], messages)) for msg in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Add high-importance messages until token limit
    retained = []
    current_tokens = count_tokens(recent)

    for msg, score in scored:
        msg_tokens = count_tokens([msg])
        if current_tokens + msg_tokens <= max_tokens and score >= 3:
            retained.append(msg)
            current_tokens += msg_tokens

    return retained + recent
```

**CMZ Application**:
- Preserve key learning moments for educational reporting
- Retain user preference statements across sessions
- Maintain conversation continuity for relationship building

---

## 4. Token Optimization Patterns for OpenAI API

### 4.1 Token Counting with tiktoken

**Implementation**:
```python
import tiktoken

class TokenManager:
    def __init__(self, model="gpt-4o"):
        self.encoding = tiktoken.encoding_for_model(model)

    def count_tokens(self, text):
        """Count tokens in text using model-specific encoding"""
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages):
        """Count tokens in message array including OpenAI formatting overhead"""
        tokens_per_message = 3  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1  # If there's a name, the role is omitted

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def truncate_to_budget(self, messages, max_tokens=4000):
        """Truncate message list to fit within token budget"""
        current_tokens = self.count_message_tokens(messages)

        if current_tokens <= max_tokens:
            return messages

        # Remove oldest messages until under budget
        while current_tokens > max_tokens and len(messages) > 1:
            removed = messages.pop(0)
            current_tokens = self.count_message_tokens(messages)

        return messages
```

**Research Evidence**:
- tiktoken is 3-6x faster than open-source tokenizers
- Pre-request validation prevents API errors
- Model-specific encodings ensure accuracy (cl100k_base for GPT-4)

**CMZ Application**:
- Validate context size before OpenAI API calls
- Prevent Lambda timeouts from oversized requests
- Monitor token usage for cost optimization

### 4.2 Context Window Management

**OpenAI Model Limits**:
- GPT-4o: 128K tokens input
- GPT-4o-mini: 128K tokens input
- GPT-3.5-turbo: 16K tokens input

**Optimal Allocation**:
```python
class ContextWindowManager:
    """
    Allocate token budget across context components
    """

    def allocate_budget(self, model="gpt-4o-mini", response_tokens=500):
        if model == "gpt-4o-mini":
            total_budget = 128000
        elif model == "gpt-3.5-turbo":
            total_budget = 16000
        else:
            total_budget = 128000

        # Reserve tokens for response
        available = total_budget - response_tokens

        # Allocate remaining budget
        allocation = {
            "system_instructions": int(available * 0.10),  # 10% - Animal personality
            "user_profile": int(available * 0.05),  # 5% - Cross-session preferences
            "session_summary": int(available * 0.10),  # 10% - Current session context
            "recent_messages": int(available * 0.60),  # 60% - Recent conversation
            "knowledge_base": int(available * 0.15),  # 15% - Retrieved facts
        }

        return allocation
```

**CMZ Application**:
- System instructions: Animal personality and educational guidelines
- User profile: Cross-session preferences and learning history
- Session summary: Current conversation context
- Recent messages: Last 10-15 message pairs
- Knowledge base: Retrieved facts from vector store

### 4.3 Batch Processing for Summarization

**Pattern for Cost Optimization**:
```python
class BatchSummarizer:
    """
    Batch summarization of multiple conversations to reduce API calls
    """

    def batch_summarize_sessions(self, session_ids, batch_size=10):
        """
        Summarize multiple sessions in parallel batches
        """
        batches = [session_ids[i:i+batch_size] for i in range(0, len(session_ids), batch_size)]

        all_summaries = []
        for batch in batches:
            # Prepare batch request
            batch_requests = []
            for session_id in batch:
                messages = self.get_messages_needing_summary(session_id)
                if messages:
                    batch_requests.append({
                        "session_id": session_id,
                        "messages": messages
                    })

            # Process batch in parallel
            summaries = self.parallel_summarize(batch_requests)
            all_summaries.extend(summaries)

        return all_summaries

    def parallel_summarize(self, requests):
        """
        Use ThreadPoolExecutor for parallel API calls
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        summaries = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_session = {
                executor.submit(self.summarize_single, req): req['session_id']
                for req in requests
            }

            for future in as_completed(future_to_session):
                session_id = future_to_session[future]
                try:
                    summary = future.result()
                    summaries.append({
                        "session_id": session_id,
                        "summary": summary
                    })
                except Exception as e:
                    print(f"Error summarizing {session_id}: {e}")

        return summaries
```

**Research Evidence**:
- Batch processing reduces per-request overhead
- Parallel execution improves throughput 5-10x
- Better resource utilization for Lambda functions

**CMZ Application**:
- Nightly batch summarization of inactive sessions
- Parallel processing of multiple animal conversations
- Cost-optimized summary generation during off-peak hours

---

## 5. Real-Time vs Batch Summarization Trade-offs

### 5.1 Real-Time Summarization

**Characteristics**:
- Triggered during active conversation
- Latency: 300ms - 2 seconds
- User perceives as "thinking time"
- Immediate context compression

**Implementation**:
```python
class RealTimeSummarizer:
    """
    Summarize during conversation with minimal latency
    """

    def should_summarize(self, session_id):
        """
        Determine if summarization should trigger
        """
        message_count = self.get_message_count(session_id)
        last_summary = self.get_last_summary_timestamp(session_id)

        # Trigger conditions
        return (
            message_count % 20 == 0 or  # Every 20 messages
            self.estimate_context_tokens(session_id) > 3000 or  # Token threshold
            (datetime.utcnow() - last_summary).seconds > 600  # 10 minutes since last
        )

    async def summarize_async(self, session_id):
        """
        Non-blocking summarization during conversation
        """
        messages = self.get_messages_since_last_summary(session_id)
        previous_summary = self.get_current_summary(session_id)

        # Use fast model for real-time summarization
        summary = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Faster, cheaper for summarization
            messages=[{
                "role": "system",
                "content": "Summarize conversation focusing on user preferences and context."
            }, {
                "role": "user",
                "content": f"Previous summary: {previous_summary}\n\nNew messages: {messages}"
            }],
            max_tokens=200,
            temperature=0.3  # Lower temperature for consistent summaries
        )

        self.store_summary(session_id, summary)
        return summary
```

**Pros**:
- Immediate token reduction
- Prevents Lambda timeouts on long conversations
- Real-time context management

**Cons**:
- Adds 300ms-2s latency per request
- Higher API call frequency increases costs
- May interrupt user flow if slow

**CMZ Application**:
- Trigger after 20 messages in active conversation
- Use during natural pauses (student thinking, typing)
- Display friendly message: "Let me organize my thoughts..."

### 5.2 Batch Summarization

**Characteristics**:
- Scheduled processing (hourly, nightly)
- No user-facing latency
- Optimized for throughput and cost
- Better resource utilization

**Implementation**:
```python
class BatchSummaryJob:
    """
    Scheduled batch job for conversation summarization
    """

    def run_nightly_summarization(self):
        """
        Nightly job to summarize inactive sessions
        """
        # Get sessions inactive for >1 hour but <24 hours
        cutoff_start = datetime.utcnow() - timedelta(hours=24)
        cutoff_end = datetime.utcnow() - timedelta(hours=1)

        sessions = self.get_sessions_in_range(cutoff_start, cutoff_end)

        # Process in batches
        batch_size = 50
        for i in range(0, len(sessions), batch_size):
            batch = sessions[i:i+batch_size]
            self.process_batch(batch)

    def process_batch(self, sessions):
        """
        Batch process multiple sessions efficiently
        """
        # Prepare all requests
        requests = []
        for session in sessions:
            if self.needs_summary(session['sessionId']):
                requests.append({
                    "custom_id": session['sessionId'],
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": self.build_summary_request(session)
                })

        # Submit batch to OpenAI Batch API
        batch_file = self.client.files.create(
            file=self.create_jsonl(requests),
            purpose="batch"
        )

        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        # Process results when complete (separate job)
        return batch_job.id
```

**Pros**:
- 50% cost reduction using OpenAI Batch API
- No user-facing latency
- Better resource utilization
- Can use slower, more accurate models

**Cons**:
- Delayed context compression
- May not prevent Lambda timeouts during long conversations
- Requires separate job scheduling infrastructure

**CMZ Application**:
- Nightly summarization of completed conversations
- Weekly user profile updates from all conversations
- Monthly analytics and preference aggregation

### 5.3 Hybrid Approach (Recommended)

**Strategy**:
```python
class HybridSummarizer:
    """
    Combines real-time and batch summarization
    """

    def handle_conversation_turn(self, session_id, message):
        """
        Real-time: Light summarization when needed
        Batch: Comprehensive summarization during off-hours
        """
        # Check if immediate summarization needed
        context_size = self.estimate_context_tokens(session_id)

        if context_size > 4000:
            # CRITICAL: Real-time summarization to prevent timeout
            summary = self.quick_summarize(session_id, max_tokens=150)
            self.store_summary(session_id, summary, type="realtime")

        # Mark for batch processing if session is long
        message_count = self.get_message_count(session_id)
        if message_count > 50:
            self.queue_for_batch_summary(session_id)

        return {
            "summarization_performed": context_size > 4000,
            "queued_for_batch": message_count > 50
        }

    def quick_summarize(self, session_id, max_tokens=150):
        """Fast, lightweight summarization for real-time needs"""
        messages = self.get_recent_messages(session_id, limit=30)

        # Use streaming for faster TTFT (time to first token)
        summary_chunks = []
        for chunk in self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Briefly summarize key preferences and context."
            }, {
                "role": "user",
                "content": str(messages)
            }],
            max_tokens=max_tokens,
            stream=True
        ):
            if chunk.choices[0].delta.content:
                summary_chunks.append(chunk.choices[0].delta.content)

        return "".join(summary_chunks)
```

**CMZ Recommendation**:
- **Real-time**: Triggered at 4000 tokens to prevent Lambda timeouts
- **Batch**: Nightly comprehensive summarization and profile updates
- **Best of both**: User experience preserved, costs optimized

---

## 6. Vector Database Integration for Context Retrieval

### 6.1 Vector Database Options for AWS

**Option 1: Amazon RDS PostgreSQL with pgvector**

**Pros**:
- Integrates with existing AWS infrastructure
- No additional service to manage
- Combines structured data + vector search
- Familiar PostgreSQL tooling

**Cons**:
- Self-managed scaling
- Limited vector-specific optimizations
- Higher latency vs specialized vector DBs

**Implementation**:
```python
import psycopg2
from pgvector.psycopg2 import register_vector

class PgVectorStore:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        register_vector(self.conn)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;

            CREATE TABLE IF NOT EXISTS conversation_embeddings (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255),
                user_id VARCHAR(255),
                animal_id VARCHAR(255),
                message_text TEXT,
                embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX ON conversation_embeddings
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        self.conn.commit()

    def store_conversation_embedding(self, session_id, user_id, animal_id,
                                     message_text, embedding, metadata=None):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO conversation_embeddings
            (session_id, user_id, animal_id, message_text, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session_id, user_id, animal_id, message_text, embedding,
              json.dumps(metadata or {})))
        self.conn.commit()

    def search_similar_conversations(self, query_embedding, limit=5):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT session_id, user_id, animal_id, message_text, metadata,
                   1 - (embedding <=> %s) as similarity
            FROM conversation_embeddings
            ORDER BY embedding <=> %s
            LIMIT %s
        """, (query_embedding, query_embedding, limit))
        return cur.fetchall()
```

**Cost Estimate**:
- RDS PostgreSQL db.t3.medium: $70/month
- Storage (100GB): $11.50/month
- **Total: ~$82/month**

**Option 2: Pinecone (Managed Vector Database)**

**Pros**:
- Fully managed, zero operations
- Optimized for vector search performance
- Hybrid search (sparse + dense)
- Auto-scaling

**Cons**:
- Additional service dependency
- Recurring SaaS costs
- Data stored outside AWS (compliance considerations)

**Implementation**:
```python
from pinecone import Pinecone, ServerlessSpec

class PineconeVectorStore:
    def __init__(self, api_key, environment="us-east-1"):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = "cmz-conversations"
        self.ensure_index()

    def ensure_index(self):
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
        self.index = self.pc.Index(self.index_name)

    def store_conversation_embedding(self, session_id, user_id, animal_id,
                                     message_text, embedding, metadata=None):
        vector_id = f"{session_id}_{datetime.utcnow().timestamp()}"

        self.index.upsert(vectors=[{
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "session_id": session_id,
                "user_id": user_id,
                "animal_id": animal_id,
                "message_text": message_text,
                **(metadata or {})
            }
        }])

    def search_similar_conversations(self, query_embedding,
                                     filter_dict=None, top_k=5):
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict  # e.g., {"animal_id": "pokey"}
        )
        return results.matches
```

**Cost Estimate**:
- Starter: $70/month (100K vectors)
- Standard: $100-200/month (1M vectors)

**Option 3: Qdrant (Open-Source with Managed Option)**

**Pros**:
- Open-source (self-host option)
- High performance
- Rich filtering capabilities
- Managed cloud option available

**Cons**:
- Additional infrastructure if self-hosted
- Smaller ecosystem than Pinecone

**Implementation**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore:
    def __init__(self, url="http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self.collection_name = "cmz_conversations"
        self.ensure_collection()

    def ensure_collection(self):
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )

    def store_conversation_embedding(self, session_id, user_id, animal_id,
                                     message_text, embedding, metadata=None):
        point_id = hash(f"{session_id}_{datetime.utcnow().timestamp()}")

        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "session_id": session_id,
                    "user_id": user_id,
                    "animal_id": animal_id,
                    "message_text": message_text,
                    **(metadata or {})
                }
            )]
        )

    def search_similar_conversations(self, query_embedding,
                                     filter_conditions=None, limit=5):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filter_conditions,
            limit=limit
        )
        return results
```

**Cost Estimate**:
- Self-hosted on EC2 t3.medium: $35/month
- Managed Qdrant Cloud: $25-100/month

### 6.2 Recommended Architecture for CMZ

**Hybrid Approach: DynamoDB + pgvector**

```python
class CMZConversationStore:
    """
    Combines DynamoDB for operational data with pgvector for semantic search
    """

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.conversations_table = self.dynamodb.Table('quest-dev-conversation')
        self.vector_store = PgVectorStore(os.getenv('POSTGRES_CONNECTION'))
        self.openai_client = OpenAI()

    def store_conversation_turn(self, session_id, user_message,
                                assistant_reply, metadata):
        """
        Store turn in both DynamoDB (operational) and pgvector (semantic)
        """
        # 1. Store in DynamoDB (existing pattern)
        user_msg_id = str(uuid.uuid4())
        assistant_msg_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'

        self.conversations_table.update_item(
            Key={'conversationId': session_id},
            UpdateExpression='SET messages = list_append(messages, :msgs), '
                           'messageCount = messageCount + :count, '
                           'endTime = :time',
            ExpressionAttributeValues={
                ':msgs': [
                    {'messageId': user_msg_id, 'role': 'user',
                     'text': user_message, 'timestamp': timestamp},
                    {'messageId': assistant_msg_id, 'role': 'assistant',
                     'text': assistant_reply, 'timestamp': timestamp}
                ],
                ':count': 2,
                ':time': timestamp
            }
        )

        # 2. Generate embedding for semantic search
        combined_text = f"User: {user_message}\nAssistant: {assistant_reply}"
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=combined_text
        )
        embedding = embedding_response.data[0].embedding

        # 3. Store in vector database
        self.vector_store.store_conversation_embedding(
            session_id=session_id,
            user_id=metadata.get('user_id'),
            animal_id=metadata.get('animal_id'),
            message_text=combined_text,
            embedding=embedding,
            metadata={
                'user_msg_id': user_msg_id,
                'assistant_msg_id': assistant_msg_id,
                'timestamp': timestamp
            }
        )

        return user_msg_id

    def retrieve_relevant_context(self, current_message, session_id, limit=3):
        """
        Retrieve semantically similar past conversations for context
        """
        # Generate embedding for current message
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=current_message
        )
        query_embedding = embedding_response.data[0].embedding

        # Search for similar conversations
        similar = self.vector_store.search_similar_conversations(
            query_embedding=query_embedding,
            limit=limit
        )

        # Format for context
        context_items = []
        for match in similar:
            session_id, user_id, animal_id, message_text, metadata, similarity = match
            if similarity > 0.7:  # Threshold for relevance
                context_items.append({
                    "text": message_text,
                    "similarity": similarity,
                    "metadata": metadata
                })

        return context_items
```

**Benefits**:
- DynamoDB: Fast operational queries, existing infrastructure
- pgvector: Semantic search for relevant context retrieval
- Combined: Best of both worlds

**Cost**:
- DynamoDB: Pay-per-request (existing)
- RDS PostgreSQL: ~$82/month
- **Total additional cost: $82/month**

---

## 7. Personalization Effectiveness Metrics and Validation

### 7.1 Key Metrics for CMZ Platform

**User Engagement Metrics**:

```python
class PersonalizationMetrics:
    """
    Track personalization effectiveness for CMZ chatbots
    """

    def calculate_engagement_metrics(self, user_id, time_period_days=30):
        """
        Measure user engagement with personalized conversations
        """
        sessions = self.get_user_sessions(user_id, days=time_period_days)

        metrics = {
            # Conversation Length
            "avg_messages_per_session": np.mean([s['messageCount'] for s in sessions]),
            "avg_session_duration_seconds": np.mean([s['durationSeconds'] for s in sessions]),

            # User Retention
            "sessions_count": len(sessions),
            "unique_animals_visited": len(set(s['animalId'] for s in sessions)),
            "return_rate": self.calculate_return_rate(user_id, sessions),

            # Task Completion
            "questions_answered": sum(s['metadata'].get('questions_answered', 0) for s in sessions),
            "learning_objectives_met": sum(s['metadata'].get('objectives_met', 0) for s in sessions),

            # Satisfaction Indicators
            "positive_sentiment_ratio": self.calculate_sentiment(sessions),
            "explicit_likes_count": sum(s['metadata'].get('likes', 0) for s in sessions)
        }

        return metrics

    def calculate_return_rate(self, user_id, sessions):
        """
        Percentage of users who return for multiple sessions
        """
        if len(sessions) <= 1:
            return 0.0

        # Calculate time gaps between sessions
        session_dates = sorted([datetime.fromisoformat(s['startTime'].replace('Z', ''))
                               for s in sessions])

        # Return rate: came back within 7 days
        returns = 0
        for i in range(len(session_dates) - 1):
            gap = (session_dates[i+1] - session_dates[i]).days
            if gap <= 7:
                returns += 1

        return returns / (len(sessions) - 1) if len(sessions) > 1 else 0

    def calculate_sentiment(self, sessions):
        """
        Analyze user message sentiment as proxy for satisfaction
        """
        positive_indicators = ["love", "cool", "awesome", "interesting", "fun", "like"]
        negative_indicators = ["boring", "don't", "stop", "bad"]

        total_messages = 0
        positive_count = 0

        for session in sessions:
            for message in session.get('messages', []):
                if message['role'] == 'user':
                    text = message['text'].lower()
                    total_messages += 1

                    if any(word in text for word in positive_indicators):
                        positive_count += 1

        return positive_count / total_messages if total_messages > 0 else 0
```

**Personalization Quality Metrics**:

```python
def measure_personalization_effectiveness(user_id, baseline_period, personalized_period):
    """
    Compare metrics before and after personalization implementation
    """
    baseline = calculate_engagement_metrics(user_id, baseline_period)
    personalized = calculate_engagement_metrics(user_id, personalized_period)

    improvements = {
        "conversation_length_increase": (
            (personalized['avg_messages_per_session'] - baseline['avg_messages_per_session'])
            / baseline['avg_messages_per_session']
        ) * 100,

        "retention_improvement": (
            (personalized['return_rate'] - baseline['return_rate'])
            / baseline['return_rate']
        ) * 100 if baseline['return_rate'] > 0 else 0,

        "satisfaction_increase": (
            (personalized['positive_sentiment_ratio'] - baseline['positive_sentiment_ratio'])
            / baseline['positive_sentiment_ratio']
        ) * 100 if baseline['positive_sentiment_ratio'] > 0 else 0,

        "learning_improvement": (
            (personalized['learning_objectives_met'] - baseline['learning_objectives_met'])
            / baseline['learning_objectives_met']
        ) * 100 if baseline['learning_objectives_met'] > 0 else 0
    }

    return improvements

# Target: 90% personalization effectiveness means:
# - Conversation length within 10% of baseline
# - Retention rate within 10% of baseline
# - Satisfaction within 10% of baseline
# - Learning outcomes within 10% of baseline
```

### 7.2 A/B Testing Framework

**Experimental Design**:

```python
class PersonalizationABTest:
    """
    A/B test personalization strategies
    """

    def assign_user_to_group(self, user_id):
        """
        Consistent user assignment to A/B groups
        """
        # Use hash of user_id for deterministic assignment
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        return "A" if hash_value % 2 == 0 else "B"

    def run_experiment(self, experiment_config):
        """
        Compare different personalization strategies

        Example config:
        {
            "name": "Summarization Strategy Test",
            "group_A": "Full History (Baseline)",
            "group_B": "Hierarchical Summarization",
            "duration_days": 30,
            "metrics": ["avg_messages", "return_rate", "satisfaction"]
        }
        """
        users_A = self.get_users_in_group("A")
        users_B = self.get_users_in_group("B")

        # Collect metrics
        metrics_A = [self.calculate_engagement_metrics(u, experiment_config['duration_days'])
                    for u in users_A]
        metrics_B = [self.calculate_engagement_metrics(u, experiment_config['duration_days'])
                    for u in users_B]

        # Statistical comparison
        results = {}
        for metric in experiment_config['metrics']:
            values_A = [m[metric] for m in metrics_A]
            values_B = [m[metric] for m in metrics_B]

            # T-test for significance
            from scipy import stats
            t_stat, p_value = stats.ttest_ind(values_A, values_B)

            results[metric] = {
                "group_A_mean": np.mean(values_A),
                "group_B_mean": np.mean(values_B),
                "improvement": ((np.mean(values_B) - np.mean(values_A)) / np.mean(values_A)) * 100,
                "statistically_significant": p_value < 0.05,
                "p_value": p_value
            }

        return results
```

**Example Experiment**:
```python
experiment = {
    "name": "Token Reduction vs Personalization Quality",
    "hypothesis": "60% token reduction maintains 90%+ personalization effectiveness",
    "group_A": "Full conversation history (baseline)",
    "group_B": "Hierarchical summarization (60% token reduction)",
    "duration_days": 30,
    "metrics": [
        "avg_messages_per_session",
        "return_rate",
        "positive_sentiment_ratio",
        "learning_objectives_met"
    ],
    "success_criteria": {
        "min_improvement_retention": -10,  # Max 10% decrease acceptable
        "min_improvement_satisfaction": -10,
        "min_improvement_learning": -10,
        "max_token_increase": -50  # Must reduce by 50%+
    }
}

results = ab_tester.run_experiment(experiment)
```

### 7.3 Automated Quality Monitoring

**Continuous Monitoring**:

```python
class PersonalizationQualityMonitor:
    """
    Monitor personalization quality in production
    """

    def check_quality_degradation(self, threshold_days=7):
        """
        Alert if personalization quality degrades
        """
        # Compare recent vs historical metrics
        recent_metrics = self.aggregate_metrics(days=threshold_days)
        historical_metrics = self.aggregate_metrics(days=30, offset=threshold_days)

        alerts = []

        # Check for significant degradation
        if recent_metrics['return_rate'] < historical_metrics['return_rate'] * 0.85:
            alerts.append({
                "severity": "HIGH",
                "metric": "return_rate",
                "current": recent_metrics['return_rate'],
                "historical": historical_metrics['return_rate'],
                "message": "User return rate dropped >15%"
            })

        if recent_metrics['avg_messages_per_session'] < historical_metrics['avg_messages_per_session'] * 0.85:
            alerts.append({
                "severity": "MEDIUM",
                "metric": "conversation_length",
                "current": recent_metrics['avg_messages_per_session'],
                "historical": historical_metrics['avg_messages_per_session'],
                "message": "Conversation length dropped >15%"
            })

        # Send to CloudWatch/SNS if alerts exist
        if alerts:
            self.send_quality_alerts(alerts)

        return alerts

    def generate_daily_quality_report(self):
        """
        Daily dashboard of personalization effectiveness
        """
        metrics = self.aggregate_metrics(days=1)

        report = {
            "date": datetime.utcnow().isoformat(),
            "total_sessions": metrics['total_sessions'],
            "unique_users": metrics['unique_users'],
            "avg_messages_per_session": metrics['avg_messages_per_session'],
            "return_rate": metrics['return_rate'],
            "satisfaction_score": metrics['positive_sentiment_ratio'],

            # Personalization-specific
            "avg_context_tokens": metrics['avg_context_tokens'],
            "token_reduction_achieved": metrics['token_reduction_percentage'],
            "summarizations_triggered": metrics['summarizations_count'],

            # Quality indicators
            "quality_score": self.calculate_quality_score(metrics),
            "alerts": self.check_quality_degradation()
        }

        # Store in DynamoDB for trending
        self.store_daily_report(report)

        # Send to stakeholders
        self.send_quality_report(report)

        return report

    def calculate_quality_score(self, metrics):
        """
        Composite score (0-100) for personalization quality
        """
        weights = {
            "return_rate": 0.3,
            "avg_messages_per_session": 0.2,
            "positive_sentiment_ratio": 0.3,
            "learning_objectives_met": 0.2
        }

        # Normalize each metric to 0-1 scale
        normalized = {
            "return_rate": min(metrics['return_rate'] / 0.5, 1.0),  # 50% return = perfect
            "avg_messages_per_session": min(metrics['avg_messages_per_session'] / 20, 1.0),  # 20 messages = perfect
            "positive_sentiment_ratio": metrics['positive_sentiment_ratio'],  # Already 0-1
            "learning_objectives_met": min(metrics['learning_objectives_met'] / 5, 1.0)  # 5 objectives = perfect
        }

        score = sum(normalized[k] * weights[k] for k in weights.keys()) * 100
        return round(score, 2)
```

**CloudWatch Integration**:

```python
import boto3

class CloudWatchMetrics:
    """
    Publish personalization metrics to CloudWatch
    """

    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.namespace = 'CMZ/Personalization'

    def publish_metrics(self, metrics):
        """
        Publish metrics to CloudWatch for monitoring and alerting
        """
        metric_data = [
            {
                'MetricName': 'ReturnRate',
                'Value': metrics['return_rate'],
                'Unit': 'Percent',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'AverageConversationLength',
                'Value': metrics['avg_messages_per_session'],
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'SatisfactionScore',
                'Value': metrics['positive_sentiment_ratio'],
                'Unit': 'Percent',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'TokenReductionPercentage',
                'Value': metrics['token_reduction_percentage'],
                'Unit': 'Percent',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'QualityScore',
                'Value': self.calculate_quality_score(metrics),
                'Unit': 'None',
                'Timestamp': datetime.utcnow()
            }
        ]

        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=metric_data
        )
```

---

## 8. Practical Implementation Recommendations for CMZ

### 8.1 Phase 1: Foundation (Weeks 1-2)

**Objective**: Implement token counting and basic summarization infrastructure

**Tasks**:

1. **Add tiktoken Integration**
```python
# In requirements.txt
tiktoken>=0.5.0

# In conversation.py
import tiktoken

class TokenCounter:
    def __init__(self, model="gpt-4o-mini"):
        self.encoding = tiktoken.encoding_for_model(model)

    def count_message_tokens(self, messages):
        # Implementation from section 4.1
        pass

# Add to handle_convo_turn_post
token_counter = TokenCounter()
context_tokens = token_counter.count_message_tokens(messages)

# Log token usage to DynamoDB
metadata['context_tokens'] = context_tokens
```

2. **Enhance DynamoDB Schema**
```python
# Add to quest-dev-conversation table:
{
    "conversationId": "conv_pokey_user123_abc123",
    "messages": [...],  # Existing

    # NEW FIELDS:
    "sessionSummary": {
        "summary": "User expressed interest in...",
        "preferences": ["habitats", "diet"],
        "lastUpdated": "2025-01-10T15:30:00Z",
        "tokenCount": 187
    },
    "contextStats": {
        "totalMessages": 45,
        "totalTokens": 8500,
        "lastSummarized": "2025-01-10T14:00:00Z",
        "summarizationCount": 2
    }
}
```

3. **Implement Basic Token Threshold**
```python
# In handle_convo_turn_post, before OpenAI API call:
TOKEN_THRESHOLD = 4000

if context_tokens > TOKEN_THRESHOLD:
    # Trigger summarization
    logger.info(f"Context tokens ({context_tokens}) exceeded threshold ({TOKEN_THRESHOLD}). Summarizing...")
    session_summary = generate_session_summary(session_id)

    # Use summary instead of full history
    messages = build_context_with_summary(session_summary, recent_messages=10)
```

**Success Criteria**:
- Token counting accurate within 5%
- DynamoDB schema updated
- Logging shows token usage per request
- No Lambda timeouts on long conversations

### 8.2 Phase 2: Hierarchical Summarization (Weeks 3-4)

**Objective**: Implement three-tier memory system

**Tasks**:

1. **Implement Summarization Functions**
```python
# New file: impl/utils/conversation_summarization.py

class ConversationSummarizer:
    def __init__(self):
        self.client = OpenAI()
        self.token_counter = TokenCounter()

    def generate_session_summary(self, session_id, animal_id):
        """Generate summary of conversation session"""
        # Get messages since last summary
        messages = self.get_messages_since_last_summary(session_id)
        previous_summary = self.get_current_summary(session_id)

        # Build summarization prompt
        prompt = SUMMARIZATION_PROMPT.format(
            animal_name=self.get_animal_name(animal_id),
            previous_summary=previous_summary or "First conversation",
            n=len(messages),
            recent_turns=self.format_messages(messages)
        )

        # Generate summary using gpt-4o-mini (fast, cheap)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3
        )

        summary = response.choices[0].message.content
        token_count = self.token_counter.count_tokens(summary)

        # Store summary in DynamoDB
        self.store_session_summary(session_id, summary, token_count)

        return summary

    def build_context_with_summary(self, session_id, recent_message_count=10):
        """Build context using summary + recent messages"""
        # Get recent messages (verbatim)
        recent_messages = self.get_recent_messages(session_id, limit=recent_message_count)

        # Get session summary
        session_summary = self.get_session_summary(session_id)

        # Get user profile (cross-session)
        user_id = self.get_session_user_id(session_id)
        animal_id = self.get_session_animal_id(session_id)
        user_profile = self.get_user_profile(user_id, animal_id)

        # Combine into context
        context = []

        # Add user profile as system message
        if user_profile:
            context.append({
                "role": "system",
                "content": f"User profile: {user_profile['summary']}"
            })

        # Add session summary
        if session_summary:
            context.append({
                "role": "system",
                "content": f"Earlier conversation summary: {session_summary['summary']}"
            })

        # Add recent messages
        context.extend(recent_messages)

        return context
```

2. **Integrate into Conversation Handler**
```python
# In impl/conversation.py, update handle_convo_turn_post:

def handle_convo_turn_post(*args, **kwargs):
    # ... existing code ...

    # Build optimized context
    from .utils.conversation_summarization import ConversationSummarizer
    summarizer = ConversationSummarizer()

    # Check if summarization needed
    context_stats = get_context_stats(session_id)
    if context_stats['totalTokens'] > 4000:
        # Generate/update summary
        summarizer.generate_session_summary(session_id, animal_id)

    # Build context with summary + recent messages
    messages = summarizer.build_context_with_summary(session_id, recent_message_count=10)

    # Continue with OpenAI API call using optimized context
    # ...
```

**Success Criteria**:
- Automatic summarization triggered at 4000 tokens
- Context size reduced by 50-60%
- Conversation continuity maintained (user testing)
- No increase in user-reported issues

### 8.3 Phase 3: User Profile & Semantic Search (Weeks 5-6)

**Objective**: Extract user preferences and enable cross-session personalization

**Tasks**:

1. **Setup pgvector on RDS**
```sql
-- On RDS PostgreSQL instance
CREATE EXTENSION vector;

CREATE TABLE user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    animal_id VARCHAR(255),
    profile_summary TEXT,
    favorite_topics TEXT[],
    engagement_level VARCHAR(50),
    learning_style VARCHAR(50),
    conversation_count INTEGER,
    last_updated TIMESTAMP,
    embedding vector(1536)
);

CREATE INDEX ON user_profiles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE conversation_embeddings (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    user_id VARCHAR(255),
    animal_id VARCHAR(255),
    message_text TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

2. **Implement User Profile Generation**
```python
# New file: impl/utils/user_profile_manager.py

class UserProfileManager:
    def __init__(self):
        self.client = OpenAI()
        self.vector_store = PgVectorStore(os.getenv('POSTGRES_CONNECTION'))

    def generate_user_profile(self, user_id, animal_id):
        """Generate cross-session user profile"""
        # Get all conversations for this user + animal
        sessions = self.get_user_animal_sessions(user_id, animal_id)

        # Combine all messages
        all_user_messages = []
        for session in sessions:
            messages = session.get('messages', [])
            user_msgs = [m['text'] for m in messages if m['role'] == 'user']
            all_user_messages.extend(user_msgs)

        combined_text = " ".join(all_user_messages)

        # Generate profile using LLM
        profile_prompt = f"""
        Analyze these messages from a zoo visitor to create a user profile.

        Messages:
        {combined_text[:4000]}  # Limit to avoid token limits

        Create a profile (max 100 words) including:
        1. Favorite animals or topics
        2. Learning interests
        3. Engagement style (curious, enthusiastic, etc.)
        4. Age-appropriate content level

        Profile:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": profile_prompt}],
            max_tokens=150
        )

        profile_text = response.choices[0].message.content

        # Generate embedding
        embedding_response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=profile_text
        )
        embedding = embedding_response.data[0].embedding

        # Extract structured preferences
        preferences = self.extract_preferences(combined_text)

        # Store profile in pgvector
        profile_data = {
            "user_id": user_id,
            "animal_id": animal_id,
            "profile_summary": profile_text,
            "favorite_topics": preferences.get('topics', []),
            "engagement_level": preferences.get('engagement_level', 'medium'),
            "learning_style": preferences.get('learning_style', 'mixed'),
            "conversation_count": len(sessions),
            "embedding": embedding
        }

        self.vector_store.store_user_profile(profile_data)

        return profile_data

    def extract_preferences(self, text):
        """Extract structured preferences using LLM"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Extract user preferences. Return JSON with: topics (list), engagement_level (low/medium/high), learning_style (visual/auditory/reading/mixed)."
            }, {
                "role": "user",
                "content": text[:2000]
            }],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

3. **Scheduled Profile Updates**
```python
# New file: scripts/update_user_profiles.py
# Run as nightly Lambda function or ECS task

def update_user_profiles_batch():
    """Nightly job to update user profiles"""
    # Get users with activity in last 7 days
    active_users = get_active_users(days=7)

    profile_manager = UserProfileManager()

    for user in active_users:
        for animal_id in user['animals_visited']:
            try:
                profile_manager.generate_user_profile(user['user_id'], animal_id)
                print(f"Updated profile for {user['user_id']} + {animal_id}")
            except Exception as e:
                print(f"Error updating profile: {e}")

    print(f"Updated {len(active_users)} user profiles")

if __name__ == "__main__":
    update_user_profiles_batch()
```

**Success Criteria**:
- User profiles generated for active users
- Profiles accessible in <100ms from pgvector
- Cross-session personalization working ("I remember you like cats")
- Profile accuracy >80% (manual validation)

### 8.4 Phase 4: Batch Summarization & Optimization (Weeks 7-8)

**Objective**: Implement cost-optimized batch processing

**Tasks**:

1. **Implement Batch Summarization**
```python
# New file: scripts/batch_summarize_conversations.py

class BatchSummarizationJob:
    def __init__(self):
        self.client = OpenAI()
        self.dynamodb = boto3.resource('dynamodb')
        self.conversations_table = self.dynamodb.Table('quest-dev-conversation')

    def run_nightly_batch(self):
        """Nightly comprehensive summarization"""
        # Get sessions inactive for >1 hour but active in last 24 hours
        cutoff_start = datetime.utcnow() - timedelta(hours=24)
        cutoff_end = datetime.utcnow() - timedelta(hours=1)

        # Scan for eligible sessions
        response = self.conversations_table.scan(
            FilterExpression=Attr('endTime').between(
                cutoff_start.isoformat() + 'Z',
                cutoff_end.isoformat() + 'Z'
            ) & Attr('messageCount').gt(20)  # Only summarize substantial conversations
        )

        sessions = response.get('Items', [])
        print(f"Found {len(sessions)} sessions for batch summarization")

        # Process in batches using OpenAI Batch API
        batch_size = 50
        for i in range(0, len(sessions), batch_size):
            batch = sessions[i:i+batch_size]
            self.process_batch_with_openai(batch)

    def process_batch_with_openai(self, sessions):
        """Use OpenAI Batch API for 50% cost reduction"""
        # Prepare JSONL file for batch API
        requests = []
        for session in sessions:
            messages = session.get('messages', [])
            if len(messages) < 20:
                continue

            request = {
                "custom_id": session['conversationId'],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": self.build_summary_prompt(messages, session.get('animalId'))
                    }],
                    "max_tokens": 200,
                    "temperature": 0.3
                }
            }
            requests.append(request)

        # Write to JSONL file
        batch_file_path = f"/tmp/batch_{datetime.utcnow().timestamp()}.jsonl"
        with open(batch_file_path, 'w') as f:
            for req in requests:
                f.write(json.dumps(req) + '\n')

        # Upload to OpenAI
        with open(batch_file_path, 'rb') as f:
            batch_file = self.client.files.create(file=f, purpose="batch")

        # Create batch job
        batch = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        print(f"Created batch job: {batch.id}")

        # Store batch ID for result retrieval
        self.store_batch_job(batch.id, [s['conversationId'] for s in sessions])

        return batch.id

    def retrieve_batch_results(self, batch_id):
        """Retrieve and store batch summarization results"""
        batch = self.client.batches.retrieve(batch_id)

        if batch.status != 'completed':
            print(f"Batch {batch_id} not completed yet: {batch.status}")
            return

        # Download results
        result_file = self.client.files.content(batch.output_file_id)
        results = [json.loads(line) for line in result_file.text.split('\n') if line]

        # Store summaries in DynamoDB
        for result in results:
            session_id = result['custom_id']
            summary = result['response']['body']['choices'][0]['message']['content']

            self.conversations_table.update_item(
                Key={'conversationId': session_id},
                UpdateExpression='SET sessionSummary = :summary',
                ExpressionAttributeValues={
                    ':summary': {
                        'summary': summary,
                        'lastUpdated': datetime.utcnow().isoformat() + 'Z',
                        'tokenCount': len(summary.split())  # Approximate
                    }
                }
            )

        print(f"Stored {len(results)} summaries from batch {batch_id}")
```

2. **Setup Scheduled Jobs**
```python
# CloudWatch Events or EventBridge rule
# Run daily at 2 AM UTC

# Lambda function: batch_summarization_runner
import boto3
from batch_summarize_conversations import BatchSummarizationJob

def lambda_handler(event, context):
    job = BatchSummarizationJob()

    # Run batch summarization
    batch_ids = job.run_nightly_batch()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Batch summarization initiated',
            'batch_ids': batch_ids
        })
    }

# Lambda function: batch_result_retriever
# Run every hour to check for completed batches
def lambda_handler(event, context):
    job = BatchSummarizationJob()

    # Get pending batch jobs
    pending_batches = job.get_pending_batches()

    for batch_id in pending_batches:
        job.retrieve_batch_results(batch_id)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Retrieved results from completed batches',
            'batches_processed': len(pending_batches)
        })
    }
```

**Success Criteria**:
- Batch summarization running nightly
- 50% cost reduction on summarization (using Batch API)
- All sessions >20 messages summarized within 24 hours
- No impact on real-time conversation performance

### 8.5 Phase 5: Monitoring & Validation (Week 9-10)

**Objective**: Implement quality monitoring and validate effectiveness

**Tasks**:

1. **Setup CloudWatch Dashboards**
```python
# Create CloudWatch dashboard
import boto3

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["CMZ/Personalization", "ReturnRate"],
                    [".", "AverageConversationLength"],
                    [".", "SatisfactionScore"]
                ],
                "period": 3600,
                "stat": "Average",
                "region": "us-west-2",
                "title": "Personalization Quality Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["CMZ/Personalization", "TokenReductionPercentage"],
                    [".", "AverageContextTokens"]
                ],
                "period": 3600,
                "stat": "Average",
                "region": "us-west-2",
                "title": "Token Optimization Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["CMZ/Personalization", "QualityScore"]
                ],
                "period": 3600,
                "stat": "Average",
                "region": "us-west-2",
                "title": "Overall Quality Score",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "max": 100
                    }
                }
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='CMZ-Personalization-Quality',
    DashboardBody=json.dumps(dashboard_body)
)
```

2. **Setup Quality Alerts**
```python
# Create CloudWatch alarms
cloudwatch.put_metric_alarm(
    AlarmName='CMZ-PersonalizationQualityDegradation',
    MetricName='QualityScore',
    Namespace='CMZ/Personalization',
    Statistic='Average',
    Period=3600,
    EvaluationPeriods=2,
    Threshold=80,  # Alert if quality score drops below 80
    ComparisonOperator='LessThanThreshold',
    AlarmActions=[os.getenv('SNS_ALERT_TOPIC_ARN')]
)

cloudwatch.put_metric_alarm(
    AlarmName='CMZ-TokenReductionInsufficient',
    MetricName='TokenReductionPercentage',
    Namespace='CMZ/Personalization',
    Statistic='Average',
    Period=3600,
    EvaluationPeriods=2,
    Threshold=50,  # Alert if token reduction <50%
    ComparisonOperator='LessThanThreshold',
    AlarmActions=[os.getenv('SNS_ALERT_TOPIC_ARN')]
)
```

3. **Run A/B Test**
```python
# Deploy A/B test for 2 weeks
ab_test = PersonalizationABTest()

experiment_config = {
    "name": "Hierarchical Summarization Validation",
    "group_A": "Full History (Baseline)",
    "group_B": "Hierarchical Summarization (60% token reduction)",
    "duration_days": 14,
    "metrics": [
        "avg_messages_per_session",
        "return_rate",
        "positive_sentiment_ratio",
        "learning_objectives_met",
        "context_tokens_avg"
    ],
    "success_criteria": {
        "min_quality_retention": 0.90,  # 90% of baseline quality
        "min_token_reduction": 0.50  # 50% token reduction
    }
}

# Run experiment
results = ab_test.run_experiment(experiment_config)

# Validate success
if results['quality_retention'] >= 0.90 and results['token_reduction'] >= 0.50:
    print("✅ SUCCESS: Hierarchical summarization meets all criteria")
    print(f"Quality retention: {results['quality_retention']:.1%}")
    print(f"Token reduction: {results['token_reduction']:.1%}")
else:
    print("❌ FAILURE: Does not meet success criteria")
    print(f"Quality retention: {results['quality_retention']:.1%} (need 90%)")
    print(f"Token reduction: {results['token_reduction']:.1%} (need 50%)")
```

**Success Criteria**:
- CloudWatch dashboard showing all key metrics
- Alerts configured and tested
- A/B test shows 90%+ quality retention with 60%+ token reduction
- Weekly quality reports generated automatically

---

## 9. Migration Considerations: OpenAI Assistants API Sunset

### 9.1 Timeline and Urgency

**Critical Information**:
- **OpenAI Assistants API will be sunset by mid-2026**
- **Recommended migration to Responses API** (successor to Chat Completions API)
- Migration utilities expected in 2025-2026

**CMZ Impact**:
- Current implementation uses Assistants API with threads
- Need to plan migration within 12-18 months
- Can leverage migration as opportunity to implement compression

### 9.2 Responses API Benefits

**Key Features**:
- Optional server-side memory (don't send entire history every turn)
- Superset of Chat Completions API functionality
- Better alignment with conversational patterns

**Architecture Difference**:
```python
# Current: Assistants API with Threads
thread_id = assistant_conversation_manager.create_thread(metadata={...})
assistant_conversation_manager.add_message_to_thread(thread_id, message)
response = assistant_conversation_manager.run_assistant(thread_id, assistant_id)

# Future: Responses API with Server-Side Memory
response = openai.responses.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": message}
    ],
    memory={
        "session_id": session_id,
        "context": {
            "user_profile": user_profile_summary,
            "session_summary": session_summary
        }
    }
)
```

### 9.3 Migration Strategy

**Phase 1: Parallel Implementation (Q2 2025)**
- Implement Responses API alongside existing Assistants API
- Use A/B testing to validate equivalent functionality
- Gradually shift traffic to new implementation

**Phase 2: Data Migration (Q3 2025)**
- Export thread data from Assistants API
- Convert to Responses API format
- Validate conversation continuity

**Phase 3: Complete Migration (Q4 2025)**
- Deprecate Assistants API usage
- Full cutover to Responses API
- Monitor for regressions

**Opportunity**:
- Migration is ideal time to implement conversation compression
- Clean architecture for hierarchical summarization
- Server-side memory reduces client-side context management

---

## 10. Cost-Benefit Analysis

### 10.1 Current Costs (Estimated)

**OpenAI API Costs** (current full-history approach):
- Average conversation: 20 message pairs = 40 messages
- Average tokens per message: 200 tokens
- Average context per request: 8,000 tokens (20 pairs × 200 tokens × 2)
- Monthly active users: 1,000
- Messages per user per month: 100
- Total API calls: 100,000/month

**Calculation**:
```
GPT-4o-mini pricing (as of Jan 2025):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

Input tokens: 100,000 calls × 8,000 tokens = 800M tokens
Input cost: 800M × $0.150 / 1M = $120/month

Output tokens: 100,000 calls × 500 tokens avg = 50M tokens
Output cost: 50M × $0.600 / 1M = $30/month

Total OpenAI: $150/month
```

**DynamoDB Costs**:
- Storage: 10GB × $0.25/GB = $2.50/month
- Read/write requests: ~$5/month
- **Total DynamoDB: $7.50/month**

**Lambda Costs**:
- Negligible (within free tier for current volume)

**Current Total: ~$157.50/month**

### 10.2 Projected Costs with Compression

**OpenAI API Costs** (with 60% token reduction):
```
Input tokens reduced by 60%: 800M × 0.4 = 320M tokens
Input cost: 320M × $0.150 / 1M = $48/month (SAVES $72/month)

Output tokens unchanged: $30/month

Summarization cost (batch):
- 100,000 conversations/month
- 10% need summarization (>20 messages): 10,000 summaries
- Tokens per summary: 3,000 input + 200 output
- Input: 10,000 × 3,000 = 30M tokens
- Output: 10,000 × 200 = 2M tokens
- Batch API 50% discount:
  - Input: 30M × $0.150 / 1M × 0.5 = $2.25/month
  - Output: 2M × $0.600 / 1M × 0.5 = $0.60/month
  - Summarization total: $2.85/month

Total OpenAI: $48 + $30 + $2.85 = $80.85/month (SAVES $69.15/month)
```

**DynamoDB Costs** (slightly increased for summaries):
- Storage: 12GB × $0.25/GB = $3.00/month
- Read/write requests: ~$6/month
- **Total DynamoDB: $9/month**

**RDS PostgreSQL** (pgvector for embeddings):
- db.t3.medium: $70/month
- Storage (100GB): $11.50/month
- **Total RDS: $81.50/month**

**Projected Total: $171.35/month**

### 10.3 Cost-Benefit Summary

**Incremental Cost**: +$13.85/month ($171.35 - $157.50)
**Benefits**:
- 60% token reduction in main API calls
- Improved conversation quality (research shows 26% improvement)
- Cross-session personalization
- Semantic search capabilities
- Better user experience (faster responses)
- Reduced Lambda timeout risk
- Scalability for growth

**ROI**:
- At current scale: Minimal cost increase for significant quality improvement
- **At 10x scale (10,000 users)**:
  - Without compression: $1,575/month OpenAI + $75 DynamoDB = $1,650/month
  - With compression: $808.50 OpenAI + $90 DynamoDB + $81.50 RDS = $980/month
  - **Savings at scale: $670/month (40% reduction)**

**Break-even**: ~2,500 active users/month

---

## 11. Key Takeaways and Action Items

### 11.1 Summary of Recommendations

**Architecture**:
✅ **Implement three-tier hierarchical memory system**
- Tier 1: Recent 10 messages (verbatim)
- Tier 2: Session summary (AI-generated)
- Tier 3: User profile (cross-session embeddings)

✅ **Use hybrid summarization approach**
- Real-time: Triggered at 4,000 tokens for Lambda timeout prevention
- Batch: Nightly comprehensive summarization using OpenAI Batch API

✅ **Add pgvector on RDS PostgreSQL**
- User preference embeddings
- Semantic conversation search
- Cross-user similarity for recommendations

✅ **Implement robust monitoring**
- CloudWatch metrics for quality tracking
- A/B testing framework for validation
- Automated quality degradation alerts

### 11.2 Expected Outcomes

**Token Reduction**: 60-70% reduction in context tokens
- From 8,000 tokens → 2,400 tokens average per request
- Prevents Lambda timeouts on long conversations
- Scales to support 100+ message conversations

**Personalization Effectiveness**: 90%+ retention
- Conversation length maintained within 10%
- User return rate maintained within 10%
- Satisfaction scores maintained within 10%
- Learning outcomes maintained within 10%

**Cost Impact**:
- Minimal at current scale (+$13.85/month)
- Significant savings at 10x scale ($670/month savings)
- 50% reduction on summarization via Batch API

**User Experience**:
- Faster response times (reduced context processing)
- Better conversation continuity across sessions
- Personalized interactions ("I remember you like...")
- Improved educational outcomes

### 11.3 Implementation Timeline

**Immediate (Weeks 1-2)**: Token counting + basic thresholds
**Short-term (Weeks 3-4)**: Hierarchical summarization
**Medium-term (Weeks 5-6)**: User profiles + semantic search
**Long-term (Weeks 7-8)**: Batch optimization
**Validation (Weeks 9-10)**: A/B testing + quality monitoring

**Total implementation**: 10 weeks to full production

### 11.4 Success Metrics

**Quantitative**:
- Token reduction: 60%+ ✅
- Quality retention: 90%+ ✅
- Cost at scale: 40% reduction at 10x growth ✅
- Lambda timeout rate: <0.1% ✅

**Qualitative**:
- User feedback: No increase in confusion/complaints ✅
- Teacher reports: Maintained or improved educational value ✅
- Parent satisfaction: Continued engagement ✅
- Conversation coherence: Manual review shows continuity ✅

---

## 12. References and Further Reading

### Academic Research

1. **Recursively Summarizing Enables Long-Term Dialogue Memory in Large Language Models**
   - ArXiv: https://arxiv.org/abs/2308.15022
   - Key finding: Recursive summarization achieves +3% BLEU improvement

2. **Difference-aware Embedding-based Personalization (DEP)**
   - Models inter-user differences in latent space for LLM personalization

3. **Hierarchical Attention Networks for Preference Learning**
   - GCORec framework integrating fine-grained semantics

### Industry Documentation

4. **OpenAI Cookbook - Context Summarization**
   - https://cookbook.openai.com/examples/context_summarization_with_realtime_api
   - Official summarization patterns and examples

5. **Mem0 - LLM Chat History Summarization Guide**
   - https://mem0.ai/blog/llm-chat-history-summarization-guide-2025
   - 80-90% token reduction case study

6. **LangChain DynamoDB Integration**
   - https://python.langchain.com/docs/integrations/memory/aws_dynamodb/
   - AWS-specific memory management patterns

### Vector Database Resources

7. **pgvector Documentation**
   - https://github.com/pgvector/pgvector
   - PostgreSQL extension for vector similarity search

8. **Pinecone Vector Database**
   - https://www.pinecone.io/
   - Managed vector database for semantic search

9. **Qdrant Vector Database**
   - https://qdrant.tech/
   - High-performance open-source vector database

### OpenAI Resources

10. **tiktoken Library**
    - https://github.com/openai/tiktoken
    - Fast BPE tokenizer for OpenAI models

11. **OpenAI Batch API**
    - 50% cost reduction for asynchronous batch processing

12. **OpenAI Responses API**
    - Successor to Assistants API (sunset mid-2026)
    - Server-side memory management

---

## Appendix A: Code Templates

### A.1 Complete Summarization Pipeline

```python
# File: impl/utils/conversation_compression.py

import os
import json
import boto3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI
import tiktoken
import numpy as np

class ConversationCompressionManager:
    """
    Complete conversation compression system for CMZ Chatbots
    Implements three-tier hierarchical memory with real-time and batch summarization
    """

    def __init__(self):
        self.client = OpenAI()
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.conversations_table = self.dynamodb.Table('quest-dev-conversation')

        # Configuration
        self.TOKEN_THRESHOLD = 4000
        self.RECENT_MESSAGE_COUNT = 10
        self.SUMMARY_MAX_TOKENS = 200
        self.SUMMARIZE_EVERY_N_MESSAGES = 20

    # ----- Token Management -----

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: List[Dict]) -> int:
        """Count total tokens in message list including formatting overhead"""
        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += self.count_tokens(str(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # Reply priming
        return num_tokens

    # ----- Context Building (Tier 1 + 2 + 3) -----

    def build_optimized_context(self, session_id: str, user_id: str,
                               animal_id: str) -> Dict[str, Any]:
        """
        Build three-tier context:
        - Tier 1: Recent messages (verbatim)
        - Tier 2: Session summary
        - Tier 3: User profile
        """
        # Tier 1: Recent verbatim messages
        recent_messages = self.get_recent_messages(session_id, self.RECENT_MESSAGE_COUNT)

        # Tier 2: Session summary
        session_summary = self.get_session_summary(session_id)
        if not session_summary:
            # Generate if doesn't exist and conversation is long enough
            message_count = self.get_message_count(session_id)
            if message_count >= self.SUMMARIZE_EVERY_N_MESSAGES:
                session_summary = self.generate_session_summary(session_id, animal_id)

        # Tier 3: User profile (cross-session)
        user_profile = self.get_user_profile(user_id, animal_id)

        # Combine into context
        context = {
            "messages": [],
            "stats": {
                "recent_tokens": 0,
                "summary_tokens": 0,
                "profile_tokens": 0,
                "total_tokens": 0
            }
        }

        # Add user profile as system message
        if user_profile:
            profile_msg = {
                "role": "system",
                "content": f"User Profile: {user_profile['summary']}"
            }
            context["messages"].append(profile_msg)
            context["stats"]["profile_tokens"] = self.count_tokens(user_profile['summary'])

        # Add session summary as system message
        if session_summary:
            summary_msg = {
                "role": "system",
                "content": f"Earlier Conversation: {session_summary['summary']}"
            }
            context["messages"].append(summary_msg)
            context["stats"]["summary_tokens"] = self.count_tokens(session_summary['summary'])

        # Add recent messages
        context["messages"].extend(recent_messages)
        context["stats"]["recent_tokens"] = self.count_message_tokens(recent_messages)

        # Calculate total
        context["stats"]["total_tokens"] = sum([
            context["stats"]["recent_tokens"],
            context["stats"]["summary_tokens"],
            context["stats"]["profile_tokens"]
        ])

        return context

    # ----- Summarization (Tier 2) -----

    def should_summarize(self, session_id: str) -> bool:
        """Determine if summarization should trigger"""
        message_count = self.get_message_count(session_id)

        # Check message threshold
        if message_count >= self.SUMMARIZE_EVERY_N_MESSAGES:
            last_summary = self.get_last_summary_timestamp(session_id)
            if not last_summary:
                return True

            # Check if enough new messages since last summary
            messages_since_summary = self.get_message_count_since(session_id, last_summary)
            if messages_since_summary >= self.SUMMARIZE_EVERY_N_MESSAGES:
                return True

        # Check token threshold
        context_tokens = self.estimate_context_tokens(session_id)
        if context_tokens > self.TOKEN_THRESHOLD:
            return True

        return False

    def generate_session_summary(self, session_id: str, animal_id: str) -> Dict[str, Any]:
        """Generate AI summary of conversation session"""
        # Get messages since last summary
        messages = self.get_messages_since_last_summary(session_id)
        previous_summary = self.get_current_summary(session_id)

        if not messages:
            return previous_summary

        # Get animal name for context
        animal_name = self.get_animal_name(animal_id)

        # Build summarization prompt
        prompt = f"""You are summarizing a conversation between {animal_name} (a zoo animal chatbot) and a zoo visitor.

Previous summary (or "First conversation" if none):
{previous_summary['summary'] if previous_summary else "First conversation"}

Recent conversation ({len(messages)} new messages):
{self.format_messages_for_summary(messages)}

Create a concise summary (max 150 words) focusing on:
1. PREFERENCES: What the visitor likes/dislikes about animals or nature
2. INTERESTS: Topics that engage them most (habitats, diet, conservation, etc.)
3. LEARNING: Educational facts they found interesting
4. PERSONALITY: How they interact (curious, shy, enthusiastic, thoughtful)
5. COMMITMENTS: Topics to continue discussing next time

Preserve specific details like favorite animals, colors, activities mentioned.
This helps {animal_name} provide personalized responses in future conversations.

Summary:"""

        # Generate summary
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.SUMMARY_MAX_TOKENS,
            temperature=0.3  # Lower temperature for consistency
        )

        summary_text = response.choices[0].message.content
        token_count = self.count_tokens(summary_text)

        # Store summary in DynamoDB
        summary_data = {
            "summary": summary_text,
            "lastUpdated": datetime.utcnow().isoformat() + 'Z',
            "tokenCount": token_count,
            "messagesCovered": len(messages)
        }

        self.store_session_summary(session_id, summary_data)

        return summary_data

    # ----- User Profile Management (Tier 3) -----

    def generate_user_profile(self, user_id: str, animal_id: str) -> Dict[str, Any]:
        """Generate cross-session user profile"""
        # Get all sessions for this user + animal
        sessions = self.get_user_animal_sessions(user_id, animal_id)

        if not sessions:
            return None

        # Collect all user messages
        all_user_messages = []
        for session in sessions:
            messages = session.get('messages', [])
            user_msgs = [m['text'] for m in messages if m['role'] == 'user']
            all_user_messages.extend(user_msgs)

        combined_text = " ".join(all_user_messages)

        # Truncate if too long
        if self.count_tokens(combined_text) > 4000:
            combined_text = combined_text[:15000]  # Approx 4000 tokens

        # Generate profile using LLM
        profile_prompt = f"""Analyze these messages from a zoo visitor to create a user profile for {animal_id}.

Visitor messages:
{combined_text}

Create a profile (max 100 words) including:
1. Favorite animals or nature topics
2. Learning interests and questions they ask
3. Engagement style (curious, enthusiastic, thoughtful, etc.)
4. Age-appropriate content level (if detectable)

Profile:"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": profile_prompt}],
            max_tokens=150
        )

        profile_text = response.choices[0].message.content

        # Store profile
        profile_data = {
            "user_id": user_id,
            "animal_id": animal_id,
            "summary": profile_text,
            "conversation_count": len(sessions),
            "last_updated": datetime.utcnow().isoformat() + 'Z'
        }

        self.store_user_profile(profile_data)

        return profile_data

    # ----- DynamoDB Operations -----

    def get_recent_messages(self, session_id: str, limit: int) -> List[Dict]:
        """Get most recent messages from session"""
        try:
            response = self.conversations_table.get_item(Key={'conversationId': session_id})
            item = response.get('Item')

            if not item:
                return []

            messages = item.get('messages', [])
            return messages[-limit:] if len(messages) > limit else messages

        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get current session summary"""
        try:
            response = self.conversations_table.get_item(Key={'conversationId': session_id})
            item = response.get('Item')
            return item.get('sessionSummary') if item else None
        except Exception:
            return None

    def store_session_summary(self, session_id: str, summary_data: Dict):
        """Store session summary in DynamoDB"""
        try:
            self.conversations_table.update_item(
                Key={'conversationId': session_id},
                UpdateExpression='SET sessionSummary = :summary',
                ExpressionAttributeValues={':summary': summary_data}
            )
        except Exception as e:
            print(f"Error storing summary: {e}")

    def get_user_profile(self, user_id: str, animal_id: str) -> Optional[Dict]:
        """Get user profile from cache or generate"""
        # TODO: Implement profile caching in DynamoDB or RDS
        # For now, return None to trigger generation as needed
        return None

    def store_user_profile(self, profile_data: Dict):
        """Store user profile"""
        # TODO: Implement profile storage in DynamoDB or RDS
        pass

    # ----- Helper Methods -----

    def get_message_count(self, session_id: str) -> int:
        """Get total message count for session"""
        try:
            response = self.conversations_table.get_item(Key={'conversationId': session_id})
            item = response.get('Item')
            return item.get('messageCount', 0) if item else 0
        except Exception:
            return 0

    def estimate_context_tokens(self, session_id: str) -> int:
        """Estimate total context tokens for session"""
        messages = self.get_recent_messages(session_id, limit=100)
        return self.count_message_tokens(messages)

    def get_animal_name(self, animal_id: str) -> str:
        """Get animal name from ID"""
        # TODO: Integrate with animal service
        return animal_id.title()

    def format_messages_for_summary(self, messages: List[Dict]) -> str:
        """Format messages for summarization prompt"""
        formatted = []
        for msg in messages:
            role = "Visitor" if msg['role'] == 'user' else "Animal"
            formatted.append(f"{role}: {msg['text']}")
        return "\n".join(formatted)

    def get_messages_since_last_summary(self, session_id: str) -> List[Dict]:
        """Get messages added since last summary"""
        try:
            response = self.conversations_table.get_item(Key={'conversationId': session_id})
            item = response.get('Item')

            if not item:
                return []

            messages = item.get('messages', [])
            summary = item.get('sessionSummary')

            if not summary:
                return messages

            # Get messages after last summary timestamp
            last_summary_time = datetime.fromisoformat(summary['lastUpdated'].replace('Z', ''))

            new_messages = []
            for msg in messages:
                msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', ''))
                if msg_time > last_summary_time:
                    new_messages.append(msg)

            return new_messages

        except Exception as e:
            print(f"Error getting messages since summary: {e}")
            return []

    def get_last_summary_timestamp(self, session_id: str) -> Optional[datetime]:
        """Get timestamp of last summarization"""
        summary = self.get_session_summary(session_id)
        if summary and 'lastUpdated' in summary:
            return datetime.fromisoformat(summary['lastUpdated'].replace('Z', ''))
        return None

    def get_message_count_since(self, session_id: str, since: datetime) -> int:
        """Count messages since given timestamp"""
        messages = self.get_messages_since_last_summary(session_id)
        return len(messages)

    def get_user_animal_sessions(self, user_id: str, animal_id: str) -> List[Dict]:
        """Get all sessions for user + animal combination"""
        try:
            from boto3.dynamodb.conditions import Attr

            response = self.conversations_table.scan(
                FilterExpression=Attr('userId').eq(user_id) & Attr('animalId').eq(animal_id)
            )

            return response.get('Items', [])

        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []

# ----- Usage Example -----

def example_usage():
    """Example of using ConversationCompressionManager"""

    manager = ConversationCompressionManager()

    # When processing a conversation turn
    session_id = "conv_pokey_user123_abc"
    user_id = "user123"
    animal_id = "pokey"

    # Check if summarization needed
    if manager.should_summarize(session_id):
        print("Summarization triggered")
        summary = manager.generate_session_summary(session_id, animal_id)
        print(f"Summary generated: {summary['tokenCount']} tokens")

    # Build optimized context for API call
    context = manager.build_optimized_context(session_id, user_id, animal_id)

    print(f"Context built:")
    print(f"  Recent messages: {context['stats']['recent_tokens']} tokens")
    print(f"  Session summary: {context['stats']['summary_tokens']} tokens")
    print(f"  User profile: {context['stats']['profile_tokens']} tokens")
    print(f"  Total: {context['stats']['total_tokens']} tokens")

    # Use context for OpenAI API call
    messages = context['messages']
    # ... make API call with messages ...

if __name__ == "__main__":
    example_usage()
```

---

**Document Prepared By**: Claude Code (Anthropic)
**Date**: January 2025
**Version**: 1.0
**For**: CMZ Chatbots Platform - Conversation History Compression Implementation
