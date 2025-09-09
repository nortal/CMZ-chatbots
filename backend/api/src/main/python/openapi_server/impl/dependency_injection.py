"""Dependency injection container for hexagonal architecture"""
import os
from .domain.user_service import UserService
from .domain.animal_service import AnimalService
from .adapters.dynamodb.repositories import DynamoUserRepository, DynamoUserDetailsRepository, DynamoAnimalRepository
from .adapters.flask.handlers import FlaskUserHandler
from .adapters.flask.serializers import FlaskUserSerializer, FlaskUserDetailsSerializer
from .adapters.flask.animal_handlers import FlaskAnimalHandler
from .adapters.flask.serializers import FlaskAnimalSerializer, FlaskAnimalConfigSerializer
from .adapters.aws_lambda.handlers import LambdaUserHandler
from .adapters.aws_lambda.serializers import LambdaUserSerializer, LambdaUserDetailsSerializer
from .adapters.aws_lambda.animal_handlers import LambdaAnimalHandler
from .adapters.aws_lambda.serializers import LambdaAnimalSerializer, LambdaAnimalConfigSerializer
from .adapters.audit_service import StandardAuditService
from .utils.orm.store import get_store

# Environment configuration
USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")
USER_PK_NAME = os.getenv("USER_DYNAMO_PK_NAME", "userId")
USER_DETAILS_TABLE_NAME = os.getenv("USER_DETAILS_TABLE_NAME", "quest-dev-user-details")
USER_DETAILS_PK_NAME = os.getenv("USER_DETAILS_PK_NAME", "userDetailsId")
USER_DETAILS_INDEX_ATTR = os.getenv("USER_DETAILS_INDEX_ATTR", "GSI_userId")
ANIMAL_TABLE_NAME = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")
ANIMAL_PK_NAME = os.getenv("ANIMAL_DYNAMO_PK_NAME", "animalId")


# Singleton instances (lazy loaded)
_user_service = None
_flask_user_handler = None
_lambda_user_handler = None
_animal_service = None
_flask_animal_handler = None
_lambda_animal_handler = None


def create_user_service() -> UserService:
    """Create UserService with all dependencies"""
    global _user_service
    if _user_service is None:
        # Create repository dependencies
        user_store = get_store(USER_TABLE_NAME, USER_PK_NAME)
        user_details_store = get_store(USER_DETAILS_TABLE_NAME, USER_DETAILS_PK_NAME)
        
        user_repo = DynamoUserRepository(user_store)
        user_details_repo = DynamoUserDetailsRepository(user_details_store, USER_DETAILS_INDEX_ATTR)
        
        # Create audit service
        audit_service = StandardAuditService()
        
        # Create domain service
        _user_service = UserService(user_repo, user_details_repo, audit_service)
    
    return _user_service


def create_flask_user_handler() -> FlaskUserHandler:
    """Create Flask user handler with all dependencies"""
    global _flask_user_handler
    if _flask_user_handler is None:
        # Create domain service
        user_service = create_user_service()
        
        # Create serializers
        user_serializer = FlaskUserSerializer()
        user_details_serializer = FlaskUserDetailsSerializer()
        
        # Create handler
        _flask_user_handler = FlaskUserHandler(user_service, user_serializer, user_details_serializer)
    
    return _flask_user_handler


def create_lambda_user_handler() -> LambdaUserHandler:
    """Create Lambda user handler with all dependencies"""
    global _lambda_user_handler
    if _lambda_user_handler is None:
        # Create domain service
        user_service = create_user_service()
        
        # Create serializers
        user_serializer = LambdaUserSerializer()
        user_details_serializer = LambdaUserDetailsSerializer()
        
        # Create handler
        _lambda_user_handler = LambdaUserHandler(user_service, user_serializer, user_details_serializer)
    
    return _lambda_user_handler


def create_animal_service() -> AnimalService:
    """Create AnimalService with all dependencies"""
    global _animal_service
    if _animal_service is None:
        # Create repository dependencies
        animal_store = get_store(ANIMAL_TABLE_NAME, ANIMAL_PK_NAME)
        animal_repo = DynamoAnimalRepository(animal_store)
        
        # Create audit service
        audit_service = StandardAuditService()
        
        # Create domain service
        _animal_service = AnimalService(animal_repo, audit_service)
    
    return _animal_service


def create_flask_animal_handler() -> FlaskAnimalHandler:
    """Create Flask animal handler with all dependencies"""
    global _flask_animal_handler
    if _flask_animal_handler is None:
        # Create domain service
        animal_service = create_animal_service()
        
        # Create serializers
        animal_serializer = FlaskAnimalSerializer()
        config_serializer = FlaskAnimalConfigSerializer()
        
        # Create handler
        _flask_animal_handler = FlaskAnimalHandler(animal_service, animal_serializer, config_serializer)
    
    return _flask_animal_handler


def create_lambda_animal_handler() -> LambdaAnimalHandler:
    """Create Lambda animal handler with all dependencies"""
    global _lambda_animal_handler
    if _lambda_animal_handler is None:
        # Create domain service
        animal_service = create_animal_service()
        
        # Create serializers
        animal_serializer = LambdaAnimalSerializer()
        config_serializer = LambdaAnimalConfigSerializer()
        
        # Create handler
        _lambda_animal_handler = LambdaAnimalHandler(animal_service, animal_serializer, config_serializer)
    
    return _lambda_animal_handler


# Direct access for testing and debugging
def get_user_repository():
    """Get user repository directly for testing"""
    user_store = get_store(USER_TABLE_NAME, USER_PK_NAME)
    return DynamoUserRepository(user_store)


def get_user_details_repository():
    """Get user details repository directly for testing"""
    user_details_store = get_store(USER_DETAILS_TABLE_NAME, USER_DETAILS_PK_NAME)
    return DynamoUserDetailsRepository(user_details_store, USER_DETAILS_INDEX_ATTR)


def get_audit_service():
    """Get audit service directly for testing"""
    return StandardAuditService()


def get_animal_repository():
    """Get animal repository directly for testing"""
    animal_store = get_store(ANIMAL_TABLE_NAME, ANIMAL_PK_NAME)
    return DynamoAnimalRepository(animal_store)


# Reset function for testing
def reset_singletons():
    """Reset all singleton instances (for testing)"""
    global _user_service, _flask_user_handler, _lambda_user_handler, _animal_service, _flask_animal_handler, _lambda_animal_handler
    _user_service = None
    _flask_user_handler = None
    _lambda_user_handler = None
    _animal_service = None
    _flask_animal_handler = None
    _lambda_animal_handler = None