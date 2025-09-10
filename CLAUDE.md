# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Python Flask-based API server for the Cougar Mountain Zoo digital ambassador chatbot platform. The project uses OpenAPI 3.0 specification-driven development with code generation and comprehensive AWS integration.

**Core Architecture:**
- **OpenAPI-First Development**: `backend/api/openapi_spec.yaml` drives all API definitions and server code generation
- **Generated Flask Server**: OpenAPI Generator creates controllers, models, and test stubs automatically
- **Implementation Layer**: Business logic implemented in `impl/` modules, never in generated code
- **AWS DynamoDB**: Data persistence with 10+ production tables for users, animals, conversations, families
- **Docker-Containerized**: Complete development and deployment workflow with live reloading
- **MCP Integration**: 24 Model Context Protocol servers for AWS services, Python development, and infrastructure

**Key Business Domains:**
- **Animals**: Chatbot personalities, configurations, and animal details
- **Families**: Parent-student group management for zoo educational programs  
- **Users & Auth**: User management with role-based access control
- **Conversations**: Chat session tracking and analytics
- **Knowledge Base**: Educational content and media management

## Development Commands

### Core Workflow
```bash
# Complete regeneration and deployment cycle
make generate-api && make build-api && make run-api

# Quick development iteration (after OpenAPI spec changes)
make generate-api
make build-api
make run-api

# Monitor running container
make logs-api

# Stop and cleanup
make stop-api
make clean-api
```

### Advanced Development
```bash
# Custom port deployment
make run-api PORT=9001

# Debug mode with interactive container
make run-api DEBUG=1

# Different OpenAPI spec
make generate-api OPENAPI_SPEC=path/to/other/spec.yaml

# Custom container/image names
make build-api IMAGE_NAME=myorg/cmz-api
make run-api CONTAINER_NAME=cmz-dev-custom
```

### Testing & Quality
```bash
# Full test suite with coverage
tox

# Quick unit tests
pytest --cov=openapi_server

# Test specific module
pytest backend/api/src/main/python/openapi_server/test/test_family.py

# Run tests in local virtualenv
make venv-api && make install-api
source .venv/openapi-venv/bin/activate
pytest --cov=openapi_server
```

### Local Python Environment (Optional)
```bash
# Setup local development (alternative to Docker)
make venv-api           # Create UV virtualenv (.venv/openapi-venv)
make install-api        # Install dependencies
source .venv/openapi-venv/bin/activate

# Rebuild environment from scratch
make rebuild-venv-api
```

## Critical Implementation Rules

### Code Generation Boundaries
- **NEVER modify generated files**: Controllers, models, and test stubs are regenerated on every `make generate-api`
- **All business logic in impl/**: Only implement functionality in `backend/api/src/main/python/openapi_server/impl/`
- **OpenAPI spec is source of truth**: API changes must start with `openapi_spec.yaml` modifications

### DynamoDB Integration Pattern
All DynamoDB operations use the centralized utilities in `impl/utils/dynamo.py`:

```python
from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

def handle_operation(body):
    # Convert OpenAPI model to dict
    item = model_to_json_keyed_dict(body) if isinstance(body, ModelClass) else dict(body)
    
    # Ensure primary key exists
    ensure_pk(item, "primaryKeyField")
    
    # Add audit timestamps
    item.setdefault("created", {"at": now_iso()})
    item["modified"] = {"at": now_iso()}
    
    # DynamoDB operation with proper error handling
    try:
        result = _table().put_item(Item=to_ddb(item))
        return from_ddb(item), 201
    except ClientError as e:
        return error_response(e)
```

### Environment Configuration
**AWS Integration:**
- `AWS_PROFILE=cmz` (configured in .zshrc)
- `AWS_REGION=us-west-2`
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (configured)

**DynamoDB Tables:**
- `FAMILY_DYNAMO_TABLE_NAME=quest-dev-family`
- `FAMILY_DYNAMO_PK_NAME=familyId`
- Similar patterns for other domain tables

**Local Development:**
- `DYNAMODB_ENDPOINT_URL`: Override for local DynamoDB testing
- `PORT`: API server port (default 8080)

## AWS & MCP Integration

The project includes comprehensive AWS tooling via 24 MCP servers:

**Core AWS Services (11 servers):**
- DynamoDB, S3, Athena, Cognito, Cost Explorer, Resources
- CDK, Terraform, Serverless (SAM), Diagrams

**Python Development (7 servers):**
- FastMCP, PRIMS, Jupyter, Python Interpreter, Django

**API & Development (6 servers):**
- OpenAPI tools, Sequential Thinking, File System access

All AWS MCP servers are configured for the CMZ account (195275676211) in us-west-2 region.

## Project Structure & Generated Code

```
backend/api/
├── openapi_spec.yaml              # SOURCE OF TRUTH - All API definitions
├── src/main/python/               # Generated + implementation code
│   ├── openapi_server/
│   │   ├── controllers/           # GENERATED - Route handlers (DO NOT EDIT)
│   │   ├── models/                # GENERATED - Data models (DO NOT EDIT)  
│   │   ├── impl/                  # IMPLEMENTATION - Business logic only
│   │   │   ├── animals.py         # Animal chatbot logic
│   │   │   ├── family.py          # Family management CRUD
│   │   │   └── utils/
│   │   │       └── dynamo.py      # DynamoDB utilities & patterns
│   │   ├── test/                  # GENERATED - Test stubs (DO NOT EDIT)
│   │   └── openapi/openapi.yaml   # Generated spec copy
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container definition
│   └── tox.ini                    # Test configuration
└── generated/app/                 # Backup of generated code (timestamped)
```

## OpenAPI Specification Structure

The API includes these major endpoint groups:
- **UI**: Public homepage, admin dashboard
- **Auth**: Authentication and authorization
- **Users**: User management and profiles  
- **Families**: Parent-student group operations
- **Animals**: Chatbot personalities and configurations
- **Conversations**: Chat sessions and history
- **Knowledge**: Educational content management
- **Analytics**: Usage metrics and reporting
- **Media**: Asset management
- **Admin/System**: Administrative operations

## Current Development Context

**Active Branch**: `kcs/POST_animal_details` - Implementing animal details endpoint
**Modified Files**: 
- `openapi_spec.yaml` (API specification updates)
- `impl/animals.py` (business logic implementation in progress)

**AWS Spend**: ~$2.15/month (primarily AWS End User Messaging for chatbot interactions)
**DynamoDB Tables**: 10 active tables with pay-per-request billing

## History Tracking Requirement

**IMPORTANT: All contributors must create session history logs before committing.**

### Process
1. Create file: `/history/{your_name}_{YYYY-MM-DD}_{start_time}h-{end_time}h.md`
2. Document your complete development session including:
   - All user prompts and requests
   - MCP server usage (Sequential, Context7, Magic, etc.)
   - Commands executed (make, git, npm, etc.)
   - Files created, modified, or deleted
   - Technical decisions and problem-solving steps
   - Build/deployment actions
   - Quality checks (lint, test, typecheck)

### Purpose
- Enable seamless project handoff between team members
- Preserve context for Claude Code sessions
- Document decision rationale and problem-solving approaches
- Track MCP integration patterns and tool usage
- Maintain architectural decision records

### Session Window
- Use 4-hour time windows for session tracking
- Start new files for sessions that extend beyond 4 hours
- Include cross-references between related session files

**Example**: See `history/kc.stegbauer_2025-09-07_09h-13h.md` for comprehensive session documentation

## API Validation Implementation Template

**Use this prompt for systematic implementation of API validation tickets:**

```
Implement the next 5 high-priority Jira tickets from our API validation epic, following the same systematic approach we used for PR003946-90, PR003946-72, PR003946-73, PR003946-69, and PR003946-66.

## Context
- CMZ chatbot backend API using OpenAPI-first development
- Flask/Connexion with DynamoDB persistence
- Docker containerized development environment
- All business logic must go in `impl/` directory (never in generated code)

## Required Process
1. **Use sequential reasoning MCP** to predict test outcomes and plan implementation
2. **Implement all tickets systematically** with proper error handling
3. **Verify functionality via cURL testing** against running Docker container
4. **Address any GitHub Advanced Security scanner issues** (unused imports, etc.)
5. **Create comprehensive MR** targeting `dev` branch with full documentation

## Technical Requirements
- Follow existing patterns in `openapi_server/impl/`
- Maintain OpenAPI specification compliance
- Use consistent Error schema with code/message/details structure
- Include proper audit timestamps and server-generated IDs
- Implement foreign key validation where applicable
- Ensure soft-delete semantics consistency

## Quality Gates
- All functionality verified working via API testing
- No breaking changes to existing features
- GitHub Advanced Security issues resolved
- Professional MR description with API verification examples
- Clean, maintainable code following project conventions

Please start by listing the next 5 tickets, then use sequential reasoning to plan the implementation approach.
```

**Why This Template Works:**
- References proven successful implementation pattern
- Emphasizes systematic sequential reasoning + implementation + testing workflow
- Captures key architectural constraints (impl/ directory, OpenAPI-first)
- Includes security scanning and professional documentation requirements
- Provides clear actionable starting steps