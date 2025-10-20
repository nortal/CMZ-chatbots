# Hexagonal Architecture Refactor Plan

## Executive Summary

Transform the current Flask OpenAPI implementation into a hexagonal architecture that supports both Flask web deployment and AWS Lambda serverless deployment from the same business logic core.

## Current State Analysis

### Existing Implementation Patterns
1. **Admin Module** (admin.py): Comprehensive CRUD with enhanced patterns
   - model_to_json_keyed_dict() for OpenAPI → dict conversion
   - PynamoDB models with custom serialization (.to_user_dict(), .to_details_dict())
   - Enhanced DynamoStore with GSI support and soft delete handling
   - Audit trail creation and validation

2. **Family Module** (family.py): Simpler CRUD pattern
   - Basic store operations (get, list, create, update, delete)
   - Standard audit patterns (created, modified timestamps)
   - Error handling with 409 conflict responses

3. **Animals Module** (animals.py): Empty (implementation target)

### Current Architecture Issues
- Business logic mixed with Flask concerns in handler functions
- Direct coupling to OpenAPI models and Flask request/response
- Difficult to unit test business logic in isolation
- Cannot reuse business logic for Lambda deployment
- Inconsistent error handling patterns across modules

## Target Hexagonal Architecture

### Core Principles
1. **Business Logic Purity**: Pure functions with no I/O dependencies
2. **Dependency Inversion**: Business logic depends on abstractions, not implementations
3. **Port/Adapter Pattern**: Clean interfaces for different deployment targets
4. **Single Source of Truth**: Same business logic for Flask and Lambda

### Directory Structure
```
impl/
├── domain/                    # Pure business logic (hexagon core)
│   ├── __init__.py
│   ├── user_service.py       # User business logic
│   ├── family_service.py     # Family business logic
│   ├── animal_service.py     # Animal business logic
│   └── common/
│       ├── __init__.py
│       ├── entities.py       # Business entities/models
│       ├── validators.py     # Business validation rules
│       ├── exceptions.py     # Domain exceptions
│       └── audit.py          # Audit trail logic
├── ports/                    # Interfaces (abstractions)
│   ├── __init__.py
│   ├── repository.py         # Data access interfaces
│   ├── serialization.py     # Serialization interfaces
│   └── audit.py              # Audit interfaces
├── adapters/                 # Implementation of ports
│   ├── __init__.py
│   ├── dynamodb/
│   │   ├── __init__.py
│   │   ├── repositories.py   # DynamoDB repository implementations
│   │   └── serializers.py    # DynamoDB serialization
│   ├── flask/
│   │   ├── __init__.py
│   │   ├── handlers.py       # Flask route handlers
│   │   └── serializers.py    # OpenAPI serialization
│   └── lambda/
│       ├── __init__.py
│       ├── handlers.py       # Lambda event handlers
│       └── serializers.py    # Lambda JSON serialization
└── utils/                    # Shared utilities (keep existing)
    ├── orm/                  # Keep existing PynamoDB models
    └── core.py               # Keep existing utilities
```

## Implementation Plan

### Phase 1: Domain Layer Foundation
**Objective**: Extract pure business logic from current handlers

#### 1.1 Create Domain Entities
```python
# domain/common/entities.py
@dataclass
class User:
    user_id: str
    email: str
    display_name: str
    role: str
    user_type: str = "none"
    family_id: Optional[str] = None
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None
```

#### 1.2 Create Business Services
```python
# domain/user_service.py
class UserService:
    def __init__(self, user_repo: UserRepository, audit: AuditService):
        self._user_repo = user_repo
        self._audit = audit
    
    def create_user(self, user_data: dict) -> User:
        """Pure business logic for user creation"""
        # Validation
        # Business rules
        # Audit trail creation
        # Return domain entity
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Pure business logic for user retrieval"""
        
    def list_users(self, filters: dict) -> List[User]:
        """Pure business logic for user listing"""
```

#### 1.3 Create Domain Exceptions
```python
# domain/common/exceptions.py
class DomainException(Exception):
    """Base domain exception"""

class UserNotFound(DomainException):
    """User not found exception"""

class ValidationError(DomainException):
    """Business validation error"""

class ConflictError(DomainException):
    """Business conflict error"""
```

### Phase 2: Ports (Interfaces)
**Objective**: Define abstractions for external dependencies

#### 2.1 Repository Interfaces
```python
# ports/repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.common.entities import User

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    def get(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def list(self, hide_soft_deleted: bool = True) -> List[User]:
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    def soft_delete(self, user_id: str) -> None:
        pass
```

#### 2.2 Serialization Interfaces  
```python
# ports/serialization.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from domain.common.entities import User

class UserSerializer(ABC):
    @abstractmethod
    def from_external(self, data: Any) -> Dict:
        """Convert external format to business dict"""
        pass
    
    @abstractmethod
    def to_external(self, user: User) -> Any:
        """Convert domain entity to external format"""
        pass
```

### Phase 3: Adapters Implementation
**Objective**: Implement ports for specific technologies

#### 3.1 DynamoDB Adapter
```python
# adapters/dynamodb/repositories.py
from ports.repository import UserRepository
from utils.orm.models.user import UserModel

class DynamoUserRepository(UserRepository):
    def __init__(self, store: DynamoStore):
        self._store = store
    
    def create(self, user: User) -> User:
        # Convert domain entity to PynamoDB model
        # Use existing store.create()
        # Convert back to domain entity
    
    def get(self, user_id: str) -> Optional[User]:
        # Use existing store.get()
        # Convert PynamoDB model to domain entity
```

#### 3.2 Flask Adapter
```python
# adapters/flask/handlers.py
from domain.user_service import UserService
from adapters.flask.serializers import FlaskUserSerializer

class FlaskUserHandler:
    def __init__(self, user_service: UserService, serializer: FlaskUserSerializer):
        self._user_service = user_service
        self._serializer = serializer
    
    def create_user(self, body) -> tuple:
        """Flask route handler"""
        try:
            user_data = self._serializer.from_external(body)
            user = self._user_service.create_user(user_data)
            return self._serializer.to_external(user), 201
        except ValidationError as e:
            return {"error": str(e)}, 400
        except ConflictError as e:
            return {"error": str(e)}, 409
```

#### 3.3 Lambda Adapter
```python
# adapters/lambda/handlers.py
from domain.user_service import UserService
from adapters.lambda.serializers import LambdaUserSerializer

class LambdaUserHandler:
    def __init__(self, user_service: UserService, serializer: LambdaUserSerializer):
        self._user_service = user_service
        self._serializer = serializer
    
    def create_user(self, event: dict, context) -> dict:
        """Lambda event handler"""
        try:
            user_data = self._serializer.from_external(json.loads(event['body']))
            user = self._user_service.create_user(user_data)
            return {
                'statusCode': 201,
                'body': json.dumps(self._serializer.to_external(user))
            }
        except ValidationError as e:
            return {'statusCode': 400, 'body': json.dumps({"error": str(e)})}
        except ConflictError as e:
            return {'statusCode': 409, 'body': json.dumps({"error": str(e)})}
```

### Phase 4: Integration and Migration
**Objective**: Connect new architecture with existing systems

#### 4.1 Dependency Injection Setup
```python
# dependency_injection.py
from domain.user_service import UserService
from adapters.dynamodb.repositories import DynamoUserRepository
from adapters.flask.handlers import FlaskUserHandler
from ports.audit import AuditService

def create_user_service() -> UserService:
    user_repo = DynamoUserRepository(get_store(USER_TABLE_NAME, USER_PK_NAME))
    audit_service = AuditService()
    return UserService(user_repo, audit_service)

def create_flask_user_handler() -> FlaskUserHandler:
    user_service = create_user_service()
    serializer = FlaskUserSerializer()
    return FlaskUserHandler(user_service, serializer)

def create_lambda_user_handler() -> LambdaUserHandler:
    user_service = create_user_service()
    serializer = LambdaUserSerializer()
    return LambdaUserHandler(user_service, serializer)
```

#### 4.2 Update Existing Controllers
```python
# Current: impl/admin.py
def handle_create_user(body: UserInput) -> User:
    # Existing implementation

# New: impl/admin.py  
from dependency_injection import create_flask_user_handler

_flask_handler = create_flask_user_handler()

def handle_create_user(body: UserInput) -> User:
    return _flask_handler.create_user(body)
```

#### 4.3 Create Lambda Entry Points
```python
# lambda_handlers.py (new file)
from dependency_injection import create_lambda_user_handler

lambda_user_handler = create_lambda_user_handler()

def lambda_create_user(event, context):
    return lambda_user_handler.create_user(event, context)

def lambda_get_user(event, context):
    return lambda_user_handler.get_user(event, context)
```

## Migration Strategy

### Step 1: Admin Module First
- Start with User and UserDetails entities (most complete implementation)
- Extract business logic from admin.py handlers
- Create domain services and repository adapters
- Test both Flask and Lambda deployments

### Step 2: Family Module Second  
- Simpler patterns, good for validating architecture
- Migrate family.py handlers
- Ensure consistent patterns with User module

### Step 3: Animals Module Third
- Implement from scratch using established patterns
- Validate architecture completeness
- Performance benchmarking

### Step 4: System-Wide Consistency
- Apply patterns to remaining modules
- Consolidate common utilities
- Performance optimization
- Documentation and testing

## Testing Strategy

### Unit Testing
```python
# Test pure business logic
def test_user_service_create():
    mock_repo = Mock(spec=UserRepository)
    mock_audit = Mock(spec=AuditService)
    service = UserService(mock_repo, mock_audit)
    
    user = service.create_user({"email": "test@test.com"})
    
    assert user.email == "test@test.com"
    mock_repo.create.assert_called_once()
```

### Integration Testing
- Flask adapter tests with real Flask app
- Lambda adapter tests with Lambda events
- DynamoDB adapter tests with local DynamoDB

### End-to-End Testing
- Full Flask deployment tests
- Full Lambda deployment tests
- Performance comparison tests

## Benefits

### Development Benefits
1. **Pure Business Logic**: Easier to test and reason about
2. **Deployment Flexibility**: Same logic for Flask and Lambda
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new adapters (GraphQL, gRPC, etc.)

### Operational Benefits
1. **Cost Optimization**: Choose Flask vs Lambda based on usage patterns
2. **Scalability**: Lambda for spiky workloads, Flask for steady state
3. **Development Speed**: Faster iteration with pure business logic
4. **Quality**: Better test coverage and reliability

## Implementation Timeline

- **Week 1-2**: Phase 1 - Domain layer foundation (User entities and services)
- **Week 3**: Phase 2 - Ports definition and interfaces
- **Week 4-5**: Phase 3 - Adapters implementation (DynamoDB, Flask, Lambda)
- **Week 6**: Phase 4 - Integration and migration (User module complete)
- **Week 7**: Family module migration
- **Week 8**: Animals module implementation
- **Week 9-10**: System-wide consistency and optimization

## Success Metrics

1. **Code Coverage**: >90% for domain layer business logic
2. **Performance**: <10% overhead compared to current implementation
3. **Deployment**: Single codebase deploys to both Flask and Lambda
4. **Maintainability**: Pure functions enable faster feature development
5. **Quality**: Reduced bug reports due to better separation and testing