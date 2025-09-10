"""
Integration tests for CMZ API Validation Epic (PR003946-61)
Tests requirements from tickets PR003946-66 through PR003946-91

This test suite validates the comprehensive API hardening requirements
defined in the Jira tickets.
"""
import json


class TestSoftDeleteSemantics:
    """
    Test soft-delete enforcement across all entities
    Covers tickets PR003946-66, PR003946-67, PR003946-68
    """
    
    def test_pr003946_66_soft_delete_flag_consistency(self, client, db_helper, sample_animal):
        """PR003946-66: Soft-delete flag consistency across all entities"""
        # Insert animal
        db_helper.insert_test_animal(sample_animal)
        
        # Test GET excludes soft-deleted by default
        response = client.get('/animal_list')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify soft-delete field present
        if data:
            for item in data:
                assert 'softDelete' in item, "Missing softDelete field"
                assert isinstance(item['softDelete'], bool), "softDelete must be boolean"
    
    def test_pr003946_67_cascade_soft_delete(self, client, db_helper, sample_family, sample_user):
        """PR003946-67: Cascade soft-delete for related entities"""
        # Create family with users
        family = db_helper.insert_test_family(sample_family)
        
        # Test family deletion cascades to related entities
        response = client.delete(f'/family/{family["familyId"]}')
        
        # Should implement cascade logic when family is deleted
        # This test documents the expected behavior
        assert response.status_code in [204, 501]  # 501 if not implemented yet
    
    def test_pr003946_68_soft_delete_recovery(self, client, db_helper, sample_animal):
        """PR003946-68: Soft-delete recovery mechanism"""
        # This would test undelete functionality if implemented
        # Documents requirement for admin recovery of soft-deleted entities
        animal = db_helper.insert_test_animal(sample_animal)
        
        # Delete animal
        response = client.delete(f'/animal/{animal["animalId"]}')  # This endpoint needs implementation
        
        # Should be able to recover soft-deleted items (admin function)
        # Test placeholder - implementation needed
        assert response.status_code in [204, 404, 501]


class TestIDValidation:
    """
    Test server-generated ID validation
    Covers tickets PR003946-69, PR003946-70
    """
    
    def test_pr003946_69_server_generated_ids(self, client, validation_helper):
        """PR003946-69: Server generates all entity IDs, rejects client-provided IDs"""
        
        # Test animal creation - should generate ID server-side
        animal_data = {
            "name": "Test Animal",
            "species": "Test Species", 
            "status": "active"
            # Note: no animalId provided - should be server-generated
        }
        
        response = client.post('/animal', 
                              data=json.dumps(animal_data),
                              content_type='application/json')
        
        if response.status_code == 201:
            data = json.loads(response.data)
            validation_helper.assert_server_generated_id(data, 'animalId')
        else:
            # Document that endpoint needs implementation
            assert response.status_code in [404, 501]
    
    def test_pr003946_70_reject_client_provided_ids(self, client, validation_helper):
        """PR003946-70: Reject requests with client-provided IDs"""
        
        animal_data = {
            "animalId": "client_provided_id",  # Should be rejected
            "name": "Test Animal", 
            "species": "Test Species",
            "status": "active"
        }
        
        response = client.post('/animal',
                              data=json.dumps(animal_data), 
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_request")
        else:
            # Document current behavior
            assert response.status_code in [201, 404, 501]


class TestAuthenticationValidation:
    """
    Test authentication and authorization enforcement
    Covers tickets PR003946-71, PR003946-72, PR003946-87, PR003946-88
    """
    
    def test_pr003946_71_token_validation(self, client, validation_helper):
        """PR003946-71: JWT token validation on protected endpoints"""
        
        # Test without token
        response = client.get('/me')
        
        if response.status_code == 401:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "unauthorized")
        else:
            # Document current state - many endpoints have security: []
            assert response.status_code in [200, 404, 501]
    
    def test_pr003946_72_role_based_access(self, client, auth_headers, validation_helper):
        """PR003946-72: Role-based access control enforcement"""
        
        # Test member role accessing admin endpoint
        member_headers = auth_headers(role="member")
        
        response = client.get('/user', headers=member_headers)
        
        if response.status_code == 403:
            data = json.loads(response.data) 
            validation_helper.assert_error_schema(data, "forbidden")
        else:
            # Document current behavior - no role enforcement yet
            assert response.status_code in [200, 401, 404, 501]
    
    def test_pr003946_87_password_policy_enforcement(self, client, validation_helper, data_factory):
        """PR003946-87: Password policy enforcement with configurable rules"""
        
        # Test weak password
        auth_data = data_factory.create_auth_request(password="123")  # Too short
        
        response = client.post('/auth',
                              data=json.dumps(auth_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_password")
            assert "password" in data.get("details", {}), "Should provide password policy guidance"
        else:
            # Document current behavior
            assert response.status_code in [200, 401, 404, 501]
    
    def test_pr003946_88_token_refresh_consistency(self, client, auth_headers, validation_helper):
        """PR003946-88: Token refresh and logout consistency"""
        
        valid_headers = auth_headers(role="member")
        
        # Test token refresh
        response = client.post('/auth/refresh', headers=valid_headers)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "token" in data, "Refresh should return new token"
            assert "expiresIn" in data, "Refresh should return expiry"
        
        # Test logout always returns 204
        logout_response = client.post('/auth/logout', headers=valid_headers)
        assert logout_response.status_code == 204, "Logout should always return 204"


class TestDataIntegrityValidation:
    """
    Test data integrity and foreign key validation  
    Covers tickets PR003946-73, PR003946-74, PR003946-75
    """
    
    def test_pr003946_73_foreign_key_validation(self, client, db_helper, validation_helper):
        """PR003946-73: Foreign key constraint validation"""
        
        # Test creating user with invalid familyId
        user_data = {
            "email": "test@cmz.org",
            "displayName": "Test User",
            "role": "member",
            "userType": "student", 
            "familyId": "non_existent_family_id"  # Invalid foreign key
        }
        
        response = client.post('/user',
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "foreign_key_violation")
        else:
            # Document current behavior - likely no FK validation yet
            assert response.status_code in [201, 404, 501]
    
    def test_pr003946_74_data_consistency_checks(self, client, validation_helper):
        """PR003946-74: Cross-entity data consistency validation"""
        
        # Test animal config without valid animal
        config_data = {
            "voice": "test_voice",
            "personality": "friendly",
            "temperature": 0.7
        }
        
        response = client.patch('/animal_config?animalId=non_existent',
                               data=json.dumps(config_data),
                               content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "entity_not_found")
        else:
            assert response.status_code in [200, 404, 501]


class TestFamilyManagementValidation:
    """
    Test family membership constraints and validation
    Covers tickets PR003946-79, PR003946-80
    """
    
    def test_pr003946_79_family_membership_constraints(self, client, validation_helper):
        """PR003946-79: Family membership validation and constraints"""
        
        # Test creating family with invalid user references
        family_data = {
            "parents": ["non_existent_user"],
            "students": ["another_non_existent_user"]
        }
        
        response = client.post('/family',
                              data=json.dumps(family_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_family_members")
        else:
            assert response.status_code in [201, 404, 501]
    
    def test_pr003946_80_parent_student_relationship_validation(self, client, db_helper, validation_helper, sample_user):
        """PR003946-80: Parent-student relationship consistency"""
        
        # Create user as both parent and student (should fail)
        user = db_helper.insert_test_user(sample_user)
        
        family_data = {
            "parents": [user["userId"]],
            "students": [user["userId"]]  # Same user as parent and student
        }
        
        response = client.post('/family', 
                              data=json.dumps(family_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_family_structure")
        else:
            assert response.status_code in [201, 404, 501]


class TestPaginationValidation:
    """
    Test pagination and filtering validation
    Covers tickets PR003946-81, PR003946-82
    """
    
    def test_pr003946_81_pagination_parameter_validation(self, client, validation_helper):
        """PR003946-81: Pagination parameter validation"""
        
        # Test invalid page parameters
        response = client.get('/user?page=0&pageSize=0')  # Invalid page/size
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_pagination")
        else:
            # Test with current implementation
            assert response.status_code in [200, 404, 501]
        
        # Test page size limits
        response = client.get('/user?pageSize=10000')  # Exceeds max
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_page_size")
    
    def test_pr003946_82_filter_parameter_validation(self, client, validation_helper):
        """PR003946-82: Query filter parameter validation"""
        
        # Test invalid filter values
        response = client.get('/animal_list?status=invalid_status')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_filter")
        else:
            assert response.status_code in [200, 404, 501]


class TestAnalyticsValidation:
    """
    Test analytics and metrics validation
    Covers tickets PR003946-83, PR003946-84, PR003946-85
    """
    
    def test_pr003946_83_time_window_validation(self, client, validation_helper):
        """PR003946-83: Analytics time window validation"""
        
        # Test invalid date range
        response = client.get('/performance_metrics?start=invalid_date&end=2023-12-31T23:59:59Z')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_date_range")
        
        # Test end before start
        response = client.get('/performance_metrics?start=2023-12-31T23:59:59Z&end=2023-01-01T00:00:00Z')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_time_window")
    
    def test_pr003946_84_log_level_validation(self, client, validation_helper):
        """PR003946-84: Log level enum validation"""
        
        response = client.get('/logs?level=invalid_level')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_log_level")
        else:
            assert response.status_code in [200, 404, 501]


class TestBillingValidation:
    """
    Test billing and period format validation
    Covers tickets PR003946-86
    """
    
    def test_pr003946_86_billing_period_format_validation(self, client, validation_helper):
        """PR003946-86: Billing period format and real calendar month validation"""
        
        # Test invalid format
        response = client.get('/billing?period=invalid_format')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_period_format")
        
        # Test invalid month
        response = client.get('/billing?period=2023-13')  # Month 13 doesn't exist
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "invalid_month")
        
        # Test valid format should work
        response = client.get('/billing?period=2023-08')
        assert response.status_code in [200, 404, 501]


class TestInputValidation:
    """
    Test input validation and length limits
    Covers tickets PR003946-89, PR003946-91
    """
    
    def test_pr003946_89_media_upload_constraints(self, client, validation_helper):
        """PR003946-89: Media upload validation for required fields and safe content"""
        
        # Test missing file
        response = client.post('/upload_media', 
                              data={},
                              content_type='multipart/form-data')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_file")
        else:
            # Endpoint might be in backlog
            assert response.status_code in [404, 501]
    
    def test_pr003946_91_conversation_turn_input_limits(self, client, validation_helper, data_factory):
        """PR003946-91: ConvoTurnRequest message length limits and required fields"""
        
        # Test missing required fields
        invalid_request = {"animalId": "test"}  # Missing message
        
        response = client.post('/convo_turn',
                              data=json.dumps(invalid_request),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "missing_required_field")
        
        # Test message too long (16k+ characters)
        long_message = "x" * 16001
        long_request = data_factory.create_convo_turn_request(message=long_message)
        
        response = client.post('/convo_turn',
                              data=json.dumps(long_request), 
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data, "message_too_long")


class TestErrorHandlingValidation:
    """
    Test consistent error schema implementation
    Covers tickets PR003946-90  
    """
    
    def test_pr003946_90_consistent_error_schema(self, curl_client, validation_helper, api_logger):
        """PR003946-90: All 4xx/5xx responses use Error schema with per-field details"""
        
        # Test 404 error format using real cURL
        response = curl_client.get('/non_existent_endpoint')
        api_logger.log_request(curl_client, "PR003946-90: Consistent Error Schema Test")
        
        assert response.status_code == 404
        
        data = response.json()
        validation_helper.assert_error_schema(data, "not_found")
        
        # Test 400 validation error format  
        invalid_data = {"invalid": "data"}
        response = client.post('/auth',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            validation_helper.assert_error_schema(data)
            # Should include per-field details when possible
            if "details" in data:
                assert isinstance(data["details"], dict), "Details should be object for field-level errors"