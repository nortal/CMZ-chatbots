"""Flask serializers for OpenAPI model conversion"""
from typing import Any, Dict
from ...ports.serialization import UserSerializer, UserDetailsSerializer, FamilySerializer, AnimalSerializer
from ...domain.common.entities import User, UserDetails, Family, Animal, AnimalConfig
from ...domain.common.serializers import serialize_user, serialize_user_details, serialize_family, serialize_animal
from ...utils.core import model_to_json_keyed_dict
from openapi_server.models.user import User as OpenAPIUser
from openapi_server.models.user_input import UserInput as OpenAPIUserInput
from openapi_server.models.user_details import UserDetails as OpenAPIUserDetails
from openapi_server.models.user_details_input import UserDetailsInput as OpenAPIUserDetailsInput
from openapi_server.models.animal import Animal as OpenAPIAnimal
from openapi_server.models.animal_config import AnimalConfig as OpenAPIAnimalConfig
from openapi_server.models.auth_request import AuthRequest as OpenAPIAuthRequest
from openapi_server.models.auth_response import AuthResponse as OpenAPIAuthResponse


class FlaskUserSerializer(UserSerializer):
    """Flask/OpenAPI serializer for User entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format (OpenAPI model) to business dict"""
        return self.from_openapi(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format (OpenAPI model)"""
        user = User(**entity_data) if not isinstance(entity_data, User) else entity_data
        return self.to_openapi(user)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI UserInput model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            # Use existing utility for OpenAPI model conversion
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, user: User) -> OpenAPIUser:
        """Convert User domain entity to OpenAPI User model"""
        user_data = serialize_user(user)
        return OpenAPIUser.from_dict(user_data)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        # For Flask adapter, this would typically not be used
        # but included for interface completeness
        return event_data
    
    def to_lambda_response(self, user: User) -> Dict[str, Any]:
        """Convert User domain entity to Lambda response dict"""
        # For Flask adapter, this would typically not be used
        # but included for interface completeness
        return serialize_user(user)


class FlaskUserDetailsSerializer(UserDetailsSerializer):
    """Flask/OpenAPI serializer for UserDetails entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format (OpenAPI model) to business dict"""
        return self.from_openapi(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format (OpenAPI model)"""
        user_details = UserDetails(**entity_data) if not isinstance(entity_data, UserDetails) else entity_data
        return self.to_openapi(user_details)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI UserDetailsInput model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            # Use existing utility for OpenAPI model conversion
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, user_details: UserDetails) -> OpenAPIUserDetails:
        """Convert UserDetails domain entity to OpenAPI UserDetails model"""
        details_data = serialize_user_details(user_details)
        return OpenAPIUserDetails.from_dict(details_data)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        return event_data
    
    def to_lambda_response(self, user_details: UserDetails) -> Dict[str, Any]:
        """Convert UserDetails domain entity to Lambda response dict"""
        return serialize_user_details(user_details)


class FlaskFamilySerializer(FamilySerializer):
    """Flask/OpenAPI serializer for Family entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format to business dict"""
        return self.from_openapi(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format"""
        family = Family(**entity_data) if not isinstance(entity_data, Family) else entity_data
        return self.to_openapi(family)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI Family model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, family: Family) -> Dict[str, Any]:
        """Convert Family domain entity to dict (OpenAPI Family model would be imported when available)"""
        return serialize_family(family)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        return event_data
    
    def to_lambda_response(self, family: Family) -> Dict[str, Any]:
        """Convert Family domain entity to Lambda response dict"""
        return serialize_family(family)


class FlaskAnimalSerializer(AnimalSerializer):
    """Flask/OpenAPI serializer for Animal entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format to business dict"""
        return self.from_openapi(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format"""
        animal = Animal(**entity_data) if not isinstance(entity_data, Animal) else entity_data
        return self.to_openapi(animal)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI Animal model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, animal: Animal) -> OpenAPIAnimal:
        """Convert Animal domain entity to OpenAPI Animal model"""
        animal_data = serialize_animal(animal)
        return OpenAPIAnimal.from_dict(animal_data)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        return event_data
    
    def to_lambda_response(self, animal: Animal) -> Dict[str, Any]:
        """Convert Animal domain entity to Lambda response dict"""
        return serialize_animal(animal)


class FlaskAnimalConfigSerializer:
    """Flask/OpenAPI serializer for Animal Configuration"""
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI AnimalConfig model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, config_data: Dict[str, Any]) -> OpenAPIAnimalConfig:
        """Convert configuration dict to OpenAPI AnimalConfig model"""
        return OpenAPIAnimalConfig.from_dict(config_data)


class FlaskAuthSerializer:
    """Flask/OpenAPI serializer for Authentication operations"""
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI AuthRequest model to business dict"""
        if hasattr(openapi_model, "attribute_map"):
            return model_to_json_keyed_dict(openapi_model) or {}
        elif isinstance(openapi_model, dict):
            return openapi_model
        else:
            return dict(openapi_model or {})
    
    def to_openapi_response(self, auth_data: Dict[str, Any]) -> OpenAPIAuthResponse:
        """Convert authentication response dict to OpenAPI AuthResponse model"""
        return OpenAPIAuthResponse.from_dict(auth_data)