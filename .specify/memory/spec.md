# Feature Specification: Cougar Mountain Zoo Digital Ambassador Chatbot Platform

**Feature Branch**: `main`
**Created**: 2025-10-19
**Status**: Active Production System (Enhancing)
**Purpose**: Educational zoo chatbot platform where visitors interact with AI-powered animal personalities

## Executive Summary

The CMZ Chatbots platform is an existing production system that enables zoo visitors to have educational conversations with AI-powered digital ambassadors representing zoo animals. Each animal has a unique personality, knowledge base, and conversational style powered by ChatGPT. The system serves multiple user roles (visitors, students, parents, educators, zookeepers, admins) with role-based access control and comprehensive family/group management.

## Current System Architecture

### Backend (Python Flask)
- **OpenAPI 3.0 Specification-Driven**: All endpoints defined in `openapi_spec.yaml`
- **Code Generation**: Controllers and models auto-generated via OpenAPI Generator
- **Hexagonal Architecture**: Controllers → Implementation modules → Handlers → Domain Services
- **AWS DynamoDB**: 10+ production tables for data persistence
- **Mock Authentication**: Development mode with pre-configured test users
- **Docker Containerized**: Complete development and deployment workflow

### Frontend (React TypeScript)
- **React 18 with TypeScript**: Component-based UI architecture
- **Tailwind CSS**: Utility-first styling system
- **Vite Build System**: Fast development and optimized production builds
- **Role-Based Navigation**: Dynamic menus based on user permissions
- **Responsive Design**: Mobile and desktop optimized

### Infrastructure
- **AWS Services**: DynamoDB, S3 (media), Cognito (auth), End User Messaging
- **MCP Integration**: 24 Model Context Protocol servers for AWS operations
- **GitHub Actions**: CI/CD pipeline with quality gates
- **Cost Efficient**: ~$2.15/month AWS spend with pay-per-request billing

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat Frontend Migration to POST Polling (Priority: P1)

A zoo visitor can use the chat interface that works reliably with Lambda deployment by using POST requests instead of Server-Sent Events (SSE), ensuring scalable, load-balancer friendly architecture.

**Why this priority**: CRITICAL - Current SSE implementation is incompatible with AWS Lambda, API Gateway timeout limits, and load balancing. This blocks serverless deployment.

**Independent Test**: Can be fully tested by initiating chat with any animal, verifying messages send/receive without SSE connections, and confirming session persistence via DynamoDB.

**Technical Context**:
- ✅ POST /convo_turn endpoint working (tested with curl)
- ❌ GET /convo_turn/stream endpoint returns 404 (Connexion SSE limitation)
- ✅ DynamoDB session management is stateless and ready
- ✅ OpenAI integration complete in backend

**Acceptance Scenarios**:

1. **Given** a visitor opens chat with any animal, **When** they send a message, **Then** the system uses POST /convo_turn instead of SSE streaming
2. **Given** a message is sent via POST, **When** the response arrives, **Then** the complete message appears in chat without streaming animations
3. **Given** an active chat session, **When** the page refreshes, **Then** the sessionId persists and conversation continues
4. **Given** multiple chat sessions, **When** switching between animals, **Then** each conversation maintains independent session state
5. **Given** a network error occurs, **When** sending a message, **Then** appropriate error handling shows user-friendly feedback
6. **Given** a message takes time to process, **When** waiting for response, **Then** loading indicators show clear processing status

---

### User Story 2 - Animal Configuration Management (Priority: P1)

Zookeepers and administrators can configure each animal's chatbot personality, including name, species, personality traits, conversation style, and knowledge base integration.

**Why this priority**: Essential for maintaining unique, engaging personalities that align with actual zoo animals and educational goals.

**Independent Test**: Can be tested by accessing /animals/config as admin, modifying an animal's personality settings, saving, and verifying changes persist in chat interactions.

**Acceptance Scenarios**:

1. **Given** an admin on animal config page, **When** they update Bella's personality to be "more playful", **Then** subsequent chats reflect the personality change
2. **Given** a zookeeper adds conservation facts, **When** visitors chat with that animal, **Then** the new facts are incorporated naturally
3. **Given** configuration changes are saved, **When** the page reloads, **Then** all settings persist from DynamoDB
4. **Given** an animal is marked inactive, **When** visitors view the list, **Then** that animal is hidden from selection

---

### User Story 3 - Family Group Management (Priority: P2)

Educators can create and manage family groups linking parents and students, enabling coordinated educational experiences and parental oversight of children's interactions.

**Why this priority**: Supports educational programs and safe child engagement with parental visibility.

**Independent Test**: Can be tested by creating a family with parents and students, verifying relationships persist, and confirming parents can view children's chat history.

**Acceptance Scenarios**:

1. **Given** an educator on family management page, **When** they create a new family with 2 parents and 3 students, **Then** the family persists with all relationships
2. **Given** a family exists, **When** adding a new student, **Then** the student is linked without affecting existing members
3. **Given** validation rules require at least one student, **When** submitting without students, **Then** an error message appears
4. **Given** a parent logs in, **When** viewing their dashboard, **Then** they see their children's recent animal interactions

---

### User Story 4 - AI Provider Configuration (Priority: P2)

Administrators can configure the AI backend provider (ChatGPT), manage API keys, track usage costs, and create GPT instances for each animal.

**Why this priority**: Critical for system operation and cost management, enables switching providers in future.

**Independent Test**: Can be tested by accessing /system/ai-provider, updating API key, monitoring usage, and creating new GPT instances.

**Acceptance Scenarios**:

1. **Given** an admin on AI settings page, **When** they enter ChatGPT API key, **Then** the key is securely stored and masked in display
2. **Given** monthly budget is set to $500, **When** usage reaches 80%, **Then** visual indicators warn of approaching limit
3. **Given** a new animal is created, **When** admin clicks "Create GPT", **Then** a new GPT instance is provisioned for that animal
4. **Given** billing information displays, **When** the month progresses, **Then** current spend updates accurately

---

### User Story 5 - Conversation History & Analytics (Priority: P3)

Users can view their past conversations, and administrators can access usage analytics to understand engagement patterns and optimize the experience.

**Why this priority**: Provides continuity for returning visitors and data-driven insights for improvement.

**Independent Test**: Can be tested by having multiple conversations, accessing /conversations/history, and verifying all past chats are retrievable with timestamps.

**Acceptance Scenarios**:

1. **Given** a user with past conversations, **When** they visit history page, **Then** all conversations are listed chronologically
2. **Given** a conversation is selected, **When** viewing details, **Then** the complete chat transcript is displayed
3. **Given** an admin views analytics, **When** filtering by date range, **Then** accurate usage metrics are shown
4. **Given** multiple users chat simultaneously, **When** checking active conversations, **Then** real-time count is accurate

---

### User Story 6 - Multi-Role Dashboard Experience (Priority: P3)

Each user role (admin, zookeeper, educator, parent, student, visitor) sees a customized dashboard with relevant metrics and quick actions.

**Why this priority**: Improves user experience by surfacing role-relevant information and actions immediately upon login.

**Independent Test**: Can be tested by logging in with each role type and verifying appropriate dashboard content and navigation options.

**Acceptance Scenarios**:

1. **Given** an admin logs in, **When** viewing dashboard, **Then** they see total users (247), animals (24), and active conversations (89)
2. **Given** a zookeeper logs in, **When** viewing dashboard, **Then** they see animal interactions, active chats, and visitor engagement metrics
3. **Given** a parent logs in, **When** viewing dashboard, **Then** they see their family's activity and children's recent interactions
4. **Given** role-based navigation, **When** a visitor logs in, **Then** they only see public features without admin options

## Technical Requirements

### Performance Requirements
- Chat response time < 3 seconds
- Page load time < 2 seconds
- Support 100+ concurrent conversations
- 99.9% uptime availability

### Security Requirements
- JWT token authentication
- Role-based access control (RBAC)
- Secure API key storage
- CORS properly configured
- Input sanitization for log injection prevention

### Data Requirements
- All data persists to DynamoDB
- Audit timestamps on all records
- Soft delete for data retention
- Backup and recovery procedures

### Integration Requirements
- ChatGPT API for conversation engine
- AWS services for infrastructure
- GitHub for source control
- Docker for containerization

## Improvement Opportunities for Spec Kit

### Phase 1: Stabilization & Testing
1. **Comprehensive Test Coverage**: Increase from current ~75% to 95%
2. **Fix Forwarding Chains**: Resolve the 5 critical handler forwarding issues
3. **E2E Test Suite**: Expand Playwright tests for all user journeys
4. **Contract Validation**: Ensure OpenAPI spec matches implementation

### Phase 2: Feature Enhancement
1. **Multi-Language Support**: Enable conversations in Spanish, Mandarin
2. **Voice Interaction**: Add text-to-speech and speech-to-text
3. **Educational Modules**: Structured lessons and quizzes
4. **Virtual Tours**: Guided zoo experiences through chat

### Phase 3: Scale & Optimize
1. **Caching Layer**: Reduce DynamoDB reads for common queries
2. **CDN Integration**: Serve static assets globally
3. **Auto-Scaling**: Handle traffic spikes during events
4. **Advanced Analytics**: ML-driven insights on engagement

## Success Metrics

### User Engagement
- Average conversation duration > 5 minutes
- Return visitor rate > 30%
- User satisfaction score > 4.5/5

### Educational Impact
- Knowledge retention test scores improve 20%
- Conservation awareness survey positive responses > 80%
- Student engagement in educational programs increases 40%

### Operational Efficiency
- Cost per conversation < $0.05
- System maintenance hours < 4/month
- Incident response time < 15 minutes

## Constraints & Considerations

### Technical Constraints
- Must maintain OpenAPI-first approach
- Cannot modify generated code directly
- Must preserve hexagonal architecture
- DynamoDB-only for persistence (no SQL databases)

### Business Constraints
- Monthly AI provider budget: $500
- Development team: 2-3 engineers
- Go-live for summer season: June 2025
- Must support 1000+ daily users

### Compliance Requirements
- COPPA compliance for children under 13
- ADA accessibility standards
- Zoo accreditation educational standards
- Data privacy regulations

## Implementation Status

### Completed Features ✅
- Core chat functionality with 24 animals
- Role-based authentication and authorization
- Family group management
- Animal configuration interface
- AI provider settings page
- Basic analytics dashboard
- Docker containerization
- AWS DynamoDB integration

### In Progress 🔄
- Comprehensive test coverage
- Handler forwarding fixes
- Performance optimization
- Documentation updates

### Planned Features 📋
- Multi-language support
- Voice interaction
- Advanced analytics
- Educational modules
- Virtual tours

## Risk Mitigation

### Technical Risks
- **API Rate Limiting**: Implement request queuing and caching
- **Data Loss**: Regular automated backups to S3
- **Security Breach**: Penetration testing and security audits
- **Performance Degradation**: Load testing and monitoring

### Business Risks
- **Cost Overrun**: Usage alerts and automatic throttling
- **User Adoption**: Marketing campaign and school partnerships
- **Competition**: Unique animal personalities and educational focus
- **Maintenance Burden**: Comprehensive documentation and automation

## Appendix: System Inventory

### API Endpoints (60+ implemented)
- Authentication: login, logout, refresh
- Users: CRUD operations, role management
- Families: Create, update, member management
- Animals: List, details, configuration
- Conversations: Start, continue, history
- Analytics: Usage, engagement, performance
- System: Health, configuration, monitoring

### Database Tables (10+ in production)
- quest-dev-users
- quest-dev-family
- quest-dev-animals
- quest-dev-conversations
- quest-dev-sessions
- quest-dev-analytics
- quest-dev-media
- quest-dev-knowledge
- quest-dev-audit
- quest-dev-configuration

### External Integrations
- OpenAI ChatGPT API
- AWS DynamoDB
- AWS S3
- AWS Cognito
- AWS CloudWatch
- GitHub Actions
- Docker Hub
- ClickSend SMS

This specification represents the current state of the CMZ Chatbots platform with clear paths for enhancement rather than replacement. The system is production-ready with real users and should be evolved incrementally while maintaining service availability.