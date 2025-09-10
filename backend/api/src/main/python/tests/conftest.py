"""
Integration test configuration for CMZ API
Tests against Jira ticket requirements for comprehensive validation
"""
import os
import pytest
import boto3
from moto import mock_aws
from flask import Flask
import connexion
from typing import Dict, Any, Generator
import json
import uuid
import subprocess
import shlex
from datetime import datetime, timezone

from openapi_server.encoder import JSONEncoder
from openapi_server.models import *


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture(scope="session")
def test_config():
    """Test configuration based on Jira requirements"""
    return {
        "aws_region": "us-west-2",
        "dynamodb_endpoint": None,  # Use moto mock
        "test_tables": {
            "animals": "test-cmz-animals",
            "users": "test-cmz-users", 
            "families": "test-cmz-families",
            "conversations": "test-cmz-conversations",
            "knowledge": "test-cmz-knowledge",
            "analytics": "test-cmz-analytics"
        },
        "auth": {
            "secret_key": "test-secret-key",
            "algorithm": "HS256",
            "token_expiry": 3600
        }
    }


# =============================================================================
# Flask App Fixture
# =============================================================================

@pytest.fixture(scope="session")
def app(test_config):
    """Create Flask app for integration testing"""
    os.environ.update({
        "AWS_DEFAULT_REGION": test_config["aws_region"],
        "DYNAMODB_ENDPOINT_URL": "",  # Empty for moto
        "JWT_SECRET_KEY": test_config["auth"]["secret_key"]
    })
    
    # Create Connexion app
    connexion_app = connexion.App(__name__, specification_dir='../openapi_server/openapi/')
    connexion_app.app.json_encoder = JSONEncoder
    connexion_app.add_api('openapi.yaml', pythonic_params=True)
    
    app = connexion_app.app
    app.config['TESTING'] = True
    
    return app


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


# =============================================================================
# cURL Test Client 
# =============================================================================

class CurlTestClient:
    """Real cURL-based test client for integration testing"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.last_command = None
        self.last_response = None
        
    def _execute_curl(self, method: str, url: str, **kwargs) -> dict:
        """Execute cURL command and return parsed response"""
        full_url = f"{self.base_url}{url}" if not url.startswith('http') else url
        
        # Build cURL command
        cmd_parts = ["curl", "-s", "-i", "-X", method.upper()]
        
        # Add headers
        headers = kwargs.get('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept', 'application/json')
        
        for key, value in headers.items():
            cmd_parts.extend(["-H", f"{key}: {value}"])
            
        # Add data for POST/PUT/PATCH
        if kwargs.get('json') and method.upper() in ['POST', 'PUT', 'PATCH']:
            data = json.dumps(kwargs['json'])
            cmd_parts.extend(["-d", data])
            
        # Add query parameters
        params = kwargs.get('params', {})
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            full_url += f"?{query_string}" if "?" not in full_url else f"&{query_string}"
            
        cmd_parts.append(full_url)
        
        # Store command for logging
        self.last_command = " ".join(shlex.quote(part) for part in cmd_parts)
        
        try:
            # Execute command
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            
            # Parse response
            output = result.stdout
            
            # Split headers and body
            if "\r\n\r\n" in output:
                headers_part, body_part = output.split("\r\n\r\n", 1)
            elif "\n\n" in output:
                headers_part, body_part = output.split("\n\n", 1)
            else:
                headers_part, body_part = output, ""
                
            # Extract status code
            status_code = 500
            if headers_part:
                first_line = headers_part.split('\n')[0]
                try:
                    status_code = int(first_line.split()[1])
                except (IndexError, ValueError):
                    pass
                    
            # Parse JSON body
            data = {}
            if body_part.strip():
                try:
                    data = json.loads(body_part.strip())
                except json.JSONDecodeError:
                    data = {"raw_response": body_part.strip()}
                    
            # Create response object
            response = CurlResponse(
                status_code=status_code,
                data=data,
                headers=headers_part,
                raw_output=output
            )
            
            self.last_response = response
            return response
            
        except subprocess.TimeoutExpired:
            return CurlResponse(
                status_code=408,
                data={"error": "Request timeout"},
                headers="",
                raw_output="Timeout after 30 seconds"
            )
        except Exception as e:
            return CurlResponse(
                status_code=500,
                data={"error": str(e)},
                headers="",
                raw_output=f"Error: {str(e)}"
            )
    
    def get(self, url: str, **kwargs):
        """Execute GET request"""
        return self._execute_curl("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs):
        """Execute POST request"""
        return self._execute_curl("POST", url, **kwargs)
        
    def put(self, url: str, **kwargs):
        """Execute PUT request"""
        return self._execute_curl("PUT", url, **kwargs)
        
    def delete(self, url: str, **kwargs):
        """Execute DELETE request"""
        return self._execute_curl("DELETE", url, **kwargs)
        
    def patch(self, url: str, **kwargs):
        """Execute PATCH request"""
        return self._execute_curl("PATCH", url, **kwargs)


class CurlResponse:
    """Response object that mimics Flask test client response"""
    
    def __init__(self, status_code: int, data: dict, headers: str, raw_output: str):
        self.status_code = status_code
        self._data = data
        self.headers_text = headers
        self.raw_output = raw_output
        
    @property
    def data(self):
        """Return raw data (for compatibility)"""
        return json.dumps(self._data).encode()
        
    def json(self):
        """Return parsed JSON data"""
        return self._data
        
    def get_json(self):
        """Return parsed JSON data (Flask compatibility)"""
        return self._data


@pytest.fixture
def curl_client():
    """cURL-based test client for real API testing"""
    return CurlTestClient()


@pytest.fixture
def api_logger():
    """Logger for cURL commands and responses"""
    logs = []
    
    class ApiLogger:
        def log_request(self, client: CurlTestClient, test_name: str):
            """Log the last cURL command and response"""
            if client.last_command and client.last_response:
                log_entry = {
                    "test": test_name,
                    "command": client.last_command,
                    "status_code": client.last_response.status_code,
                    "response": client.last_response._data,
                    "raw_output": client.last_response.raw_output
                }
                logs.append(log_entry)
                
                # Also print to console for immediate feedback
                print(f"\n{'='*60}")
                print(f"TEST: {test_name}")
                print(f"{'='*60}")
                print(f"CURL COMMAND:")
                print(f"  {client.last_command}")
                print(f"\nRESPONSE STATUS: {client.last_response.status_code}")
                print(f"RESPONSE DATA:")
                print(f"  {json.dumps(client.last_response._data, indent=2)}")
                
        def get_logs(self):
            return logs
            
        def save_logs(self, filename: str = "curl_test_logs.json"):
            """Save all logs to file"""
            with open(filename, 'w') as f:
                json.dump(logs, f, indent=2)
                
    return ApiLogger()


# =============================================================================
# DynamoDB Mock Setup
# =============================================================================

@pytest.fixture(scope="session")
def dynamodb_mock():
    """Mock DynamoDB for integration tests"""
    with mock_aws():
        yield boto3.resource('dynamodb', region_name='us-west-2')


@pytest.fixture(scope="session") 
def test_tables(dynamodb_mock, test_config):
    """Create test DynamoDB tables matching production schema"""
    tables = {}
    
    # Animals table
    tables['animals'] = dynamodb_mock.create_table(
        TableName=test_config["test_tables"]["animals"],
        KeySchema=[
            {'AttributeName': 'animalId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'animalId', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'status-index',
                'KeySchema': [{'AttributeName': 'status', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ],
        BillingMode='PROVISIONED',
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    # Users table
    tables['users'] = dynamodb_mock.create_table(
        TableName=test_config["test_tables"]["users"],
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},
            {'AttributeName': 'familyId', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'email-index',
                'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            },
            {
                'IndexName': 'family-index', 
                'KeySchema': [{'AttributeName': 'familyId', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ],
        BillingMode='PROVISIONED',
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    # Families table
    tables['families'] = dynamodb_mock.create_table(
        TableName=test_config["test_tables"]["families"],
        KeySchema=[
            {'AttributeName': 'familyId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'familyId', 'AttributeType': 'S'}
        ],
        BillingMode='PROVISIONED',
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    return tables


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_animal():
    """Sample animal data for testing"""
    return {
        "animalId": f"animal_{uuid.uuid4().hex[:8]}",
        "name": "Test Pokey",
        "species": "Coendou prehensilis", 
        "status": "active",
        "created": {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": {
                "userId": "system",
                "email": "system@cmz.org",
                "displayName": "System"
            }
        },
        "modified": {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": {
                "userId": "system", 
                "email": "system@cmz.org",
                "displayName": "System"
            }
        },
        "softDelete": False
    }


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "userId": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@cmz.org",
        "displayName": "Test User",
        "role": "member",
        "userType": "parent",
        "familyId": None,
        "created": {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": {
                "userId": "system",
                "email": "system@cmz.org", 
                "displayName": "System"
            }
        },
        "modified": {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": {
                "userId": "system",
                "email": "system@cmz.org",
                "displayName": "System"  
            }
        },
        "softDelete": False
    }


@pytest.fixture 
def sample_family(sample_user):
    """Sample family data for testing"""
    parent_id = sample_user["userId"]
    student_id = f"user_{uuid.uuid4().hex[:8]}"
    
    return {
        "familyId": f"family_{uuid.uuid4().hex[:8]}",
        "parents": [parent_id],
        "students": [student_id],
        "created": {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": {
                "userId": parent_id,
                "email": sample_user["email"],
                "displayName": sample_user["displayName"]
            }
        },
        "modified": {
            "at": datetime.now(timezone.utc).isoformat(), 
            "by": {
                "userId": parent_id,
                "email": sample_user["email"],
                "displayName": sample_user["displayName"]
            }
        },
        "softDelete": False
    }


# =============================================================================  
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing"""
    def _generate_headers(role="member", user_id=None):
        import jwt
        from datetime import datetime, timedelta
        
        if user_id is None:
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            
        payload = {
            "sub": user_id,
            "role": role, 
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, "test-secret-key", algorithm="HS256")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    return _generate_headers


# =============================================================================
# Validation Helper Fixtures
# =============================================================================

@pytest.fixture
def validation_helper():
    """Helper functions for validation testing"""
    class ValidationHelper:
        
        @staticmethod
        def assert_error_schema(response_data: dict, expected_code: str = None):
            """Validate error response follows Error schema (PR003946-90)"""
            assert "code" in response_data, "Error response missing 'code' field"
            assert "message" in response_data, "Error response missing 'message' field"
            assert isinstance(response_data["code"], str), "Error code must be string"
            assert isinstance(response_data["message"], str), "Error message must be string"
            
            if expected_code:
                assert response_data["code"] == expected_code, f"Expected code {expected_code}, got {response_data['code']}"
        
        @staticmethod 
        def assert_audit_fields(data: dict):
            """Validate audit fields are present"""
            assert "created" in data, "Missing created audit field"
            assert "modified" in data, "Missing modified audit field" 
            assert "softDelete" in data, "Missing softDelete field"
            
            for field in ["created", "modified"]:
                if data[field]:
                    assert "at" in data[field], f"Missing 'at' in {field}"
                    assert "by" in data[field], f"Missing 'by' in {field}"
        
        @staticmethod
        def assert_server_generated_id(data: dict, id_field: str):
            """Validate server generated IDs (PR003946-69)"""
            assert id_field in data, f"Missing {id_field} field"
            assert isinstance(data[id_field], str), f"{id_field} must be string"
            assert len(data[id_field]) > 0, f"{id_field} cannot be empty"
        
        @staticmethod
        def validate_pagination(response_data: dict):
            """Validate pagination structure"""
            assert "items" in response_data, "Missing items in paginated response"
            assert "page" in response_data, "Missing page in paginated response"
            assert "pageSize" in response_data, "Missing pageSize in paginated response"
            assert "total" in response_data, "Missing total in paginated response"
            
            assert isinstance(response_data["items"], list), "Items must be array"
            assert isinstance(response_data["page"], int), "Page must be integer"
            assert isinstance(response_data["pageSize"], int), "PageSize must be integer"
            assert isinstance(response_data["total"], int), "Total must be integer"
    
    return ValidationHelper()


# =============================================================================
# Database Helper Fixtures
# =============================================================================

@pytest.fixture
def db_helper(test_tables, test_config):
    """Database helper for integration tests"""
    class DatabaseHelper:
        def __init__(self):
            self.tables = test_tables
            self.config = test_config
            
        def insert_test_animal(self, animal_data: dict):
            """Insert test animal into DynamoDB"""
            table = self.tables['animals']
            table.put_item(Item=animal_data)
            return animal_data
        
        def insert_test_user(self, user_data: dict):
            """Insert test user into DynamoDB"""  
            table = self.tables['users']
            table.put_item(Item=user_data)
            return user_data
        
        def insert_test_family(self, family_data: dict):
            """Insert test family into DynamoDB"""
            table = self.tables['families'] 
            table.put_item(Item=family_data)
            return family_data
        
        def get_animal(self, animal_id: str):
            """Get animal from DynamoDB"""
            table = self.tables['animals']
            response = table.get_item(Key={"animalId": animal_id})
            return response.get('Item')
        
        def get_user(self, user_id: str):
            """Get user from DynamoDB"""
            table = self.tables['users']
            response = table.get_item(Key={"userId": user_id})
            return response.get('Item')
        
        def clean_all_tables(self):
            """Clean all test tables"""
            for table in self.tables.values():
                # Scan and delete all items
                response = table.scan()
                with table.batch_writer() as batch:
                    for item in response['Items']:
                        batch.delete_item(Key={k: item[k] for k in table.key_schema})
    
    return DatabaseHelper()


# =============================================================================
# Test Data Factories
# =============================================================================

@pytest.fixture
def data_factory():
    """Factory for generating test data"""
    class TestDataFactory:
        
        @staticmethod
        def create_auth_request(username: str = None, password: str = None, register: bool = False):
            """Create AuthRequest test data"""
            return {
                "username": username or f"test_{uuid.uuid4().hex[:8]}@cmz.org",
                "password": password or "test_password_123",
                "register": register
            }
        
        @staticmethod  
        def create_convo_turn_request(animal_id: str = None, message: str = None):
            """Create ConvoTurnRequest test data"""
            return {
                "animalId": animal_id or f"animal_{uuid.uuid4().hex[:8]}",
                "message": message or "Hello, how are you?",
                "sessionId": f"session_{uuid.uuid4().hex[:8]}",
                "metadata": {"test": True}
            }
        
        @staticmethod
        def create_invalid_data_set():
            """Create various invalid data sets for validation testing"""
            return {
                "empty_string": "",
                "null_value": None,
                "invalid_email": "not-an-email",
                "too_long_string": "x" * 10000,
                "invalid_date": "not-a-date",
                "invalid_enum": "invalid_enum_value",
                "negative_number": -1,
                "invalid_uuid": "not-a-uuid"
            }
    
    return TestDataFactory()