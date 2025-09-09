"""Lambda serializers for JSON event/response conversion"""
import json
from typing import Any, Dict
from ...ports.serialization import UserSerializer, UserDetailsSerializer, FamilySerializer, AnimalSerializer
from ...domain.common.entities import User, UserDetails, Family, Animal
from ...domain.common.serializers import (
    serialize_user, serialize_user_details, serialize_family, serialize_animal,
    deserialize_user, deserialize_user_details, deserialize_family, deserialize_animal
)


class LambdaUserSerializer(UserSerializer):
    """Lambda JSON serializer for User entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format (Lambda event) to business dict"""
        return self.from_lambda_event(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format (Lambda response)"""
        user = User(**entity_data) if not isinstance(entity_data, User) else entity_data
        return self.to_lambda_response(user)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI model to business dict (not typically used in Lambda)"""
        if isinstance(openapi_model, dict):
            return openapi_model
        elif hasattr(openapi_model, "to_dict"):
            return openapi_model.to_dict()
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, user: User) -> Dict[str, Any]:
        """Convert User domain entity to dict (not typically used in Lambda)"""
        return serialize_user(user)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Lambda event data to business dict
        
        Expects event in format:
        {
            "body": "{\"email\": \"user@example.com\", \"displayName\": \"User Name\"}",
            "pathParameters": {"userId": "123"},
            "queryStringParameters": {"page": "1", "pageSize": "10"}
        }
        """
        # Extract data from different parts of Lambda event
        result = {}
        
        # Parse body JSON if present
        if "body" in event_data and event_data["body"]:
            try:
                body_data = json.loads(event_data["body"])
                result.update(body_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Add path parameters
        if "pathParameters" in event_data and event_data["pathParameters"]:
            result.update(event_data["pathParameters"])
        
        # Add query string parameters
        if "queryStringParameters" in event_data and event_data["queryStringParameters"]:
            result.update(event_data["queryStringParameters"])
        
        return result
    
    def to_lambda_response(self, user: User) -> Dict[str, Any]:
        """
        Convert User domain entity to Lambda response dict
        
        Returns Lambda-formatted response:
        {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "{...user_data...}"
        }
        """
        user_data = serialize_user(user)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(user_data)
        }


class LambdaUserDetailsSerializer(UserDetailsSerializer):
    """Lambda JSON serializer for UserDetails entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format (Lambda event) to business dict"""
        return self.from_lambda_event(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format (Lambda response)"""
        user_details = UserDetails(**entity_data) if not isinstance(entity_data, UserDetails) else entity_data
        return self.to_lambda_response(user_details)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI model to business dict (not typically used in Lambda)"""
        if isinstance(openapi_model, dict):
            return openapi_model
        elif hasattr(openapi_model, "to_dict"):
            return openapi_model.to_dict()
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, user_details: UserDetails) -> Dict[str, Any]:
        """Convert UserDetails domain entity to dict (not typically used in Lambda)"""
        return serialize_user_details(user_details)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        result = {}
        
        # Parse body JSON if present
        if "body" in event_data and event_data["body"]:
            try:
                body_data = json.loads(event_data["body"])
                result.update(body_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Add path parameters
        if "pathParameters" in event_data and event_data["pathParameters"]:
            result.update(event_data["pathParameters"])
        
        # Add query string parameters
        if "queryStringParameters" in event_data and event_data["queryStringParameters"]:
            result.update(event_data["queryStringParameters"])
        
        return result
    
    def to_lambda_response(self, user_details: UserDetails) -> Dict[str, Any]:
        """Convert UserDetails domain entity to Lambda response dict"""
        details_data = serialize_user_details(user_details)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(details_data)
        }


class LambdaFamilySerializer(FamilySerializer):
    """Lambda JSON serializer for Family entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        return self.from_lambda_event(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        family = Family(**entity_data) if not isinstance(entity_data, Family) else entity_data
        return self.to_lambda_response(family)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        if isinstance(openapi_model, dict):
            return openapi_model
        elif hasattr(openapi_model, "to_dict"):
            return openapi_model.to_dict()
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, family: Family) -> Dict[str, Any]:
        return serialize_family(family)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        
        if "body" in event_data and event_data["body"]:
            try:
                body_data = json.loads(event_data["body"])
                result.update(body_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if "pathParameters" in event_data and event_data["pathParameters"]:
            result.update(event_data["pathParameters"])
        
        if "queryStringParameters" in event_data and event_data["queryStringParameters"]:
            result.update(event_data["queryStringParameters"])
        
        return result
    
    def to_lambda_response(self, family: Family) -> Dict[str, Any]:
        family_data = serialize_family(family)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(family_data)
        }


class LambdaAnimalSerializer(AnimalSerializer):
    """Lambda JSON serializer for Animal entities"""
    
    def from_external(self, data: Any) -> Dict[str, Any]:
        return self.from_lambda_event(data)
    
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        animal = Animal(**entity_data) if not isinstance(entity_data, Animal) else entity_data
        return self.to_lambda_response(animal)
    
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        if isinstance(openapi_model, dict):
            return openapi_model
        elif hasattr(openapi_model, "to_dict"):
            return openapi_model.to_dict()
        else:
            return dict(openapi_model or {})
    
    def to_openapi(self, animal: Animal) -> Dict[str, Any]:
        return serialize_animal(animal)
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        
        if "body" in event_data and event_data["body"]:
            try:
                body_data = json.loads(event_data["body"])
                result.update(body_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if "pathParameters" in event_data and event_data["pathParameters"]:
            # Handle both 'animalid' and 'id' path parameters
            path_params = event_data["pathParameters"]
            if "animalid" in path_params:
                result["animalId"] = path_params["animalid"]
                result["id"] = path_params["animalid"]
            result.update(path_params)
        
        if "queryStringParameters" in event_data and event_data["queryStringParameters"]:
            result.update(event_data["queryStringParameters"])
        
        return result
    
    def to_lambda_response(self, animal: Animal) -> Dict[str, Any]:
        animal_data = serialize_animal(animal)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(animal_data)
        }


class LambdaAnimalConfigSerializer:
    """Lambda JSON serializer for Animal Configuration"""
    
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        
        if "body" in event_data and event_data["body"]:
            try:
                body_data = json.loads(event_data["body"])
                result.update(body_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if "pathParameters" in event_data and event_data["pathParameters"]:
            path_params = event_data["pathParameters"]
            if "animalid" in path_params:
                result["animalId"] = path_params["animalid"]
            result.update(path_params)
        
        return result
    
    def to_lambda_response(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(config_data)
        }