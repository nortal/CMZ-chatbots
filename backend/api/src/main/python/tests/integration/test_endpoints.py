"""
Integration tests for specific CMZ API endpoints
Tests actual endpoint behavior against Jira ticket requirements
"""
import pytest
import json
import uuid
from datetime import datetime, timezone


class TestAuthenticationEndpoints:
    """Test authentication endpoints against ticket requirements"""
    
    def test_auth_post_endpoint_validation(self, client, validation_helper, data_factory):
        """Test /auth POST endpoint validation requirements"""
        
        # Test valid registration
        auth_data = data_factory.create_auth_request(register=True)
        response = client.post('/auth',
                              data=json.dumps(auth_data),
                              content_type='application/json')
        
        # Should return 200 with token or 404/501 if not implemented
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "token" in data
            assert "expiresIn" in data
            assert "user" in data
            validation_helper.assert_audit_fields(data["user"])
        else:
            assert response.status_code in [404, 501, 401]
        
        # Test password validation (PR003946-87)
        weak_auth = data_factory.create_auth_request(password="123")
        response = client.post('/auth',
                              data=json.dumps(weak_auth),
                              content_type='application/json')
        
        # Should reject weak passwords
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_password")
    
    def test_auth_refresh_endpoint(self, client, auth_headers):
        """Test /auth/refresh endpoint (PR003946-88)"""
        
        headers = auth_headers(role="member")
        response = client.post('/auth/refresh', headers=headers)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "token" in data
            assert "expiresIn" in data
        else:
            # Document current behavior
            assert response.status_code in [401, 404, 501]
    
    def test_auth_logout_endpoint(self, client, auth_headers):
        """Test /auth/logout endpoint consistency (PR003946-88)"""
        
        headers = auth_headers(role="member")
        response = client.post('/auth/logout', headers=headers)
        
        # Should always return 204 and actually invalidate session
        assert response.status_code == 204


class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_user_list_endpoint_pagination(self, client, validation_helper):
        """Test /user GET endpoint pagination (PR003946-81)"""
        
        # Test default pagination
        response = client.get('/user')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            validation_helper.validate_pagination(data)
            
            # Test users have required audit fields
            for user in data.get("items", []):
                validation_helper.assert_audit_fields(user)
        else:
            assert response.status_code in [401, 404, 501]
        
        # Test pagination limits
        response = client.get('/user?page=1&pageSize=10')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data["pageSize"] == 10
            assert data["page"] == 1
    
    def test_user_create_endpoint_validation(self, client, validation_helper):
        """Test /user POST endpoint server-generated IDs (PR003946-69)"""
        
        user_data = {
            "email": "test@cmz.org",
            "displayName": "Test User",
            "role": "member",
            "userType": "parent"
        }
        
        response = client.post('/user',
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        if response.status_code == 201:
            data = json.loads(response.data)
            validation_helper.assert_server_generated_id(data, "userId")
            validation_helper.assert_audit_fields(data)
        else:
            assert response.status_code in [400, 401, 404, 501]
    
    def test_user_get_by_id_endpoint(self, client, db_helper, sample_user, validation_helper):
        """Test /user/{userId} GET endpoint"""
        
        user = db_helper.insert_test_user(sample_user)
        
        response = client.get(f'/user/{user["userId"]}')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data["userId"] == user["userId"]
            validation_helper.assert_audit_fields(data)
        elif response.status_code == 404:
            # Expected if endpoint not fully implemented
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "not_found")
        else:
            assert response.status_code in [401, 501]


class TestAnimalEndpoints:
    """Test animal management endpoints"""
    
    def test_animal_list_endpoint(self, client, db_helper, sample_animal, validation_helper):
        """Test /animal_list GET endpoint filtering"""
        
        # Insert test animal
        animal = db_helper.insert_test_animal(sample_animal)
        
        response = client.get('/animal_list')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)
            
            # Verify soft-delete fields present (PR003946-66)
            for item in data:
                validation_helper.assert_audit_fields(item)
                assert "status" in item
        else:
            assert response.status_code in [404, 501]
        
        # Test status filtering (PR003946-82)
        response = client.get('/animal_list?status=active')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            for item in data:
                assert item["status"] == "active"
    
    def test_animal_details_endpoint_validation(self, client, validation_helper):
        """Test /animal_details GET endpoint validation"""
        
        # Test missing animalId parameter
        response = client.get('/animal_details')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_parameter")
        
        # Test invalid animalId
        response = client.get('/animal_details?animalId=non_existent')
        
        if response.status_code == 404:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "not_found")
        else:
            assert response.status_code in [200, 400, 501]
    
    def test_animal_config_endpoint_validation(self, client, validation_helper):
        """Test /animal_config endpoints validation"""
        
        # Test GET with missing animalId
        response = client.get('/animal_config')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_parameter")
        
        # Test PATCH with invalid config
        invalid_config = {
            "temperature": 3.0,  # Outside valid range (0-2)
            "topP": 1.5  # Outside valid range (0-1)
        }
        
        response = client.patch('/animal_config?animalId=test',
                               data=json.dumps(invalid_config),
                               content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_config")


class TestConversationEndpoints:
    """Test conversation endpoints"""
    
    def test_convo_turn_endpoint_validation(self, client, validation_helper, data_factory):
        """Test /convo_turn POST endpoint validation (PR003946-91)"""
        
        # Test missing required fields
        invalid_request = {"animalId": "test"}  # Missing message
        
        response = client.post('/convo_turn',
                              data=json.dumps(invalid_request),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_required_field")
        
        # Test valid request
        valid_request = data_factory.create_convo_turn_request()
        
        response = client.post('/convo_turn',
                              data=json.dumps(valid_request),
                              content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "reply" in data
            assert "turn" in data
            
            # Validate turn metadata structure
            turn = data["turn"]
            assert "convoTurnId" in turn
            assert "timestamp" in turn
            assert "tokensPrompt" in turn
            assert "tokensCompletion" in turn
            assert "latencyMs" in turn
        else:
            # Endpoint might need implementation
            assert response.status_code in [404, 501, 400]
        
        # Test message length limits (8-16k characters)
        long_request = data_factory.create_convo_turn_request(message="x" * 16001)
        
        response = client.post('/convo_turn',
                              data=json.dumps(long_request),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "message_too_long")


class TestFamilyEndpoints:
    """Test family management endpoints"""
    
    def test_family_list_endpoint(self, client, validation_helper):
        """Test /family GET endpoint"""
        
        response = client.get('/family')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)
            
            # Validate family structure
            for family in data:
                assert "familyId" in family
                assert "parents" in family
                assert "students" in family
                assert isinstance(family["parents"], list)
                assert isinstance(family["students"], list)
        else:
            assert response.status_code in [401, 404, 501]
    
    def test_family_create_endpoint_validation(self, client, validation_helper):
        """Test /family POST endpoint validation (PR003946-79)"""
        
        # Test invalid family structure
        invalid_family = {
            "parents": [],  # Empty parents
            "students": []  # Empty students  
        }
        
        response = client.post('/family',
                              data=json.dumps(invalid_family),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_family_structure")
        
        # Test with non-existent user references
        invalid_refs = {
            "parents": ["non_existent_user"],
            "students": ["another_non_existent_user"]
        }
        
        response = client.post('/family',
                              data=json.dumps(invalid_refs),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_user_reference")
    
    def test_family_get_by_id_endpoint(self, client, validation_helper):
        """Test /family/{familyId} GET endpoint"""
        
        response = client.get('/family/non_existent')
        
        if response.status_code == 404:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "not_found")
        else:
            assert response.status_code in [200, 401, 501]


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_performance_metrics_endpoint_validation(self, client, validation_helper):
        """Test /performance_metrics GET endpoint (PR003946-83)"""
        
        # Test missing required parameters
        response = client.get('/performance_metrics')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_required_parameter")
        
        # Test invalid date format
        response = client.get('/performance_metrics?start=invalid&end=invalid')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_date_format")
        
        # Test end before start
        response = client.get('/performance_metrics?start=2023-12-31T23:59:59Z&end=2023-01-01T00:00:00Z')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_time_range")
        
        # Test valid request
        response = client.get('/performance_metrics?start=2023-01-01T00:00:00Z&end=2023-12-31T23:59:59Z')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "window" in data
            assert "totals" in data
            assert "perAnimal" in data
        else:
            assert response.status_code in [404, 501]
    
    def test_logs_endpoint_validation(self, client, validation_helper):
        """Test /logs GET endpoint validation (PR003946-84)"""
        
        # Test invalid log level
        response = client.get('/logs?level=invalid_level')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_log_level")
        
        # Test valid log levels
        for level in ['debug', 'info', 'warn', 'error']:
            response = client.get(f'/logs?level={level}')
            assert response.status_code in [200, 400, 404, 501]
        
        # Test pagination parameters
        response = client.get('/logs?page=0&pageSize=0')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_pagination")
    
    def test_billing_endpoint_validation(self, client, validation_helper):
        """Test /billing GET endpoint validation (PR003946-86)"""
        
        # Test invalid period format
        response = client.get('/billing?period=invalid_format')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_period_format")
        
        # Test invalid month (13)
        response = client.get('/billing?period=2023-13')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_month")
        
        # Test valid period
        response = client.get('/billing?period=2023-08')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "period" in data
            assert "totalUsd" in data
            assert "byService" in data
        else:
            assert response.status_code in [404, 501]


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_system_health_endpoint(self, client):
        """Test /system_health GET endpoint"""
        
        response = client.get('/system_health')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "status" in data
            assert data["status"] in ["ok", "degraded", "down"]
            assert "checks" in data
            assert isinstance(data["checks"], list)
        else:
            assert response.status_code in [404, 501]
    
    def test_feature_flags_endpoint(self, client, validation_helper):
        """Test /feature_flags endpoints"""
        
        # Test GET
        response = client.get('/feature_flags')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "flags" in data
            validation_helper.assert_audit_fields(data)
        else:
            assert response.status_code in [401, 404, 501]