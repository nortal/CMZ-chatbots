<!--
Sync Impact Report
==================
Version change: 0.0.0 → 1.0.0
New constitution created for CMZ Chatbots project
Added principles: OpenAPI-First, DynamoDB Persistence, Hexagonal Architecture, Mock Authentication, AWS Integration
Added sections: Technology Stack, Development Workflow
-->

# CMZ Chatbots Constitution

## Core Principles

### I. OpenAPI-First Development
Every API endpoint starts with OpenAPI specification. The spec drives code generation through OpenAPI Generator. Controllers and models are generated, never hand-written. Business logic lives only in implementation modules. The spec is the single source of truth for API contracts.

### II. DynamoDB Persistence
All data persists to AWS DynamoDB with pay-per-request billing. No local databases for production data. Use centralized utilities (impl/utils/dynamo.py) for all operations. Every table has proper primary keys and audit timestamps. Mock data serves only for AUTH_MODE=mock testing.

### III. Hexagonal Architecture
Controllers forward to implementation modules which forward to handlers.py. This three-layer pattern ensures clean separation. Never put business logic in controllers. Domain services handle business rules. Adapters manage external integrations.

### IV. Test-First with Validation Gates
Unit tests achieve 80%+ coverage minimum. Integration tests validate DynamoDB persistence. Playwright E2E tests verify user journeys. Pre-commit hooks prevent broken code. Quality gates run before every merge.

### V. Mock-First Authentication
Development uses AUTH_MODE=mock for rapid iteration. JWT tokens follow frontend expectations exactly. Test users are pre-configured for all roles. Production switches to Cognito seamlessly. Never compromise auth in development shortcuts.

### VI. AWS MCP Integration
24 MCP servers provide AWS service access. Use MCP tools over manual AWS operations. Leverage specialized servers for their strengths. Document MCP usage patterns. Maintain configuration in claude.json.

## Technology Stack

### Backend Requirements
- Python 3.11+ with Flask/Connexion framework
- OpenAPI 3.0 specification-driven
- AWS SDK (boto3) for all AWS operations
- Docker containerization for deployment
- UV for Python package management

### Frontend Requirements
- React 18+ with TypeScript
- Tailwind CSS for styling
- Vite for build tooling
- React Router for navigation
- Axios for API communication

### Infrastructure Requirements
- AWS DynamoDB for data persistence
- AWS Cognito for production auth
- AWS S3 for media storage
- Docker for containerization
- GitHub Actions for CI/CD

## Development Workflow

### Code Generation Protocol
1. Modify openapi_spec.yaml for API changes
2. Run `make post-generate` (never standalone generate)
3. Implement only in impl/ modules
4. Validate with pre-commit hooks
5. Test with make validate-api

### Testing Requirements
- Step 1: Login validation for all test users
- Step 2: Full E2E suite only after Step 1 passes
- Always test with visible Playwright browser
- Verify DynamoDB persistence for all operations
- Document test failures with screenshots

### Git Workflow
- Feature branches only (never main/master)
- Meaningful commit messages with context
- Pre-commit validation enforced
- PR reviews required for merge
- Session history documented in /history/

## Quality Standards

### Code Quality Gates
- Flake8 for Python linting
- ESLint for TypeScript/React
- 80% minimum test coverage
- No "do some magic!" placeholders
- No TODO comments in production code

### Documentation Requirements
- OpenAPI spec fully documented
- README maintained and current
- Session histories for handoff
- Architecture decisions recorded
- API endpoints documented with examples

## Governance

The constitution supersedes all development practices. Changes require:
- Documentation of rationale
- Impact analysis on existing code
- Migration plan if breaking
- Team consensus before adoption

All code reviews must verify constitutional compliance. Non-compliance blocks merge. Use CLAUDE.md for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19