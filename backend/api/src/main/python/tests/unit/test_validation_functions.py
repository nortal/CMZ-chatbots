"""
Unit tests for validation.py functions to enable TDD workflow.

Tests billing period validation, family relationship validation, and error response consistency.
Provides fast feedback loop for red-green-refactor cycles.
"""
import pytest
from datetime import datetime
from typing import Dict, List, Optional

from openapi_server.impl.utils.validation import (
    create_validation_error, validate_no_client_id, validate_animal_status_filter,
    validate_billing_period, validate_user_references, validate_parent_student_separation,
    validate_family_data,
    ERROR_INVALID_REQUEST, ERROR_INVALID_FILTER, ERROR_INVALID_FORMAT,
    ERROR_INVALID_MONTH, ERROR_INVALID_YEAR, ERROR_VALIDATION_ERROR
)


class TestCreateValidationError:
    """Test validation error creation utility."""
    
    def test_create_validation_error_basic(self):
        """Test basic validation error creation."""
        error = create_validation_error("test_error", "Test message")
        
        assert error["code"] == "test_error"
        assert error["message"] == "Test message"
        assert error["details"] == {"error_type": "test_error"}
    
    def test_create_validation_error_with_details(self):
        """Test validation error creation with custom details."""
        details = {"field": "username", "provided_value": "admin"}
        error = create_validation_error("invalid_user", "Invalid username", details)
        
        assert error["code"] == "invalid_user"
        assert error["message"] == "Invalid username"
        assert error["details"]["field"] == "username"
        assert error["details"]["provided_value"] == "admin"
        assert error["details"]["error_type"] == "invalid_user"
    
    def test_create_validation_error_empty_details(self):
        """Test validation error creation with None details."""
        error = create_validation_error("test_error", "Test message", None)
        
        assert error["details"] == {"error_type": "test_error"}


class TestValidateNoClientId:
    """Test client ID validation (PR003946-70)."""
    
    def test_validate_no_client_id_success(self):
        """Test validation passes when no client ID provided."""
        data = {"name": "Test Animal", "species": "Lion"}
        result = validate_no_client_id(data, "animalId")
        
        assert result is None  # No validation error
    
    def test_validate_no_client_id_null_value(self):
        """Test validation passes when client ID is None."""
        data = {"animalId": None, "name": "Test Animal"}
        result = validate_no_client_id(data, "animalId")
        
        assert result is None
    
    def test_validate_no_client_id_failure(self):
        """Test validation fails when client provides ID."""
        data = {"animalId": "client_generated_id", "name": "Test Animal"}
        result = validate_no_client_id(data, "animalId")
        
        assert result is not None
        assert result["code"] == ERROR_INVALID_REQUEST
        assert "Client-provided animalId not allowed" in result["message"]
        assert result["details"]["field"] == "animalId"
        assert result["details"]["provided_value"] == "client_generated_id"
    
    def test_validate_no_client_id_different_fields(self):
        """Test validation works with different ID field names."""
        test_cases = [
            ("userId", "user_123"),
            ("familyId", "family_456"),
            ("conversationId", "conv_789")
        ]
        
        for field_name, field_value in test_cases:
            data = {field_name: field_value}
            result = validate_no_client_id(data, field_name)
            
            assert result is not None
            assert result["details"]["field"] == field_name
            assert result["details"]["provided_value"] == field_value


class TestValidateAnimalStatusFilter:
    """Test animal status filter validation (PR003946-82)."""
    
    def test_validate_animal_status_filter_valid_statuses(self):
        """Test validation passes for all valid animal statuses."""
        valid_statuses = ["active", "inactive", "hidden", "breeding", "retired"]
        
        for status in valid_statuses:
            result = validate_animal_status_filter(status)
            assert result is None, f"Valid status {status} should not produce error"
    
    def test_validate_animal_status_filter_invalid_status(self):
        """Test validation fails for invalid animal status."""
        result = validate_animal_status_filter("invalid_status")
        
        assert result is not None
        assert result["code"] == ERROR_INVALID_FILTER
        assert "Invalid status filter value: invalid_status" in result["message"]
        assert result["details"]["field"] == "status"
        assert result["details"]["provided_value"] == "invalid_status"
        assert "active" in result["details"]["valid_values"]
        assert "inactive" in result["details"]["valid_values"]
    
    def test_validate_animal_status_filter_case_sensitive(self):
        """Test validation is case-sensitive."""
        invalid_cases = ["Active", "ACTIVE", "InActive", "HIDDEN"]
        
        for invalid_status in invalid_cases:
            result = validate_animal_status_filter(invalid_status)
            assert result is not None, f"Case variation {invalid_status} should fail validation"


class TestValidateBillingPeriod:
    """Test billing period format validation (PR003946-86)."""
    
    def test_validate_billing_period_valid_formats(self):
        """Test validation passes for valid billing period formats."""
        valid_periods = [
            "2023-01",
            "2023-12", 
            "2024-06",
            "2025-03",
            "2022-11"
        ]
        
        for period in valid_periods:
            result = validate_billing_period(period)
            assert result is None, f"Valid period {period} should not produce error"
    
    def test_validate_billing_period_invalid_format(self):
        """Test validation fails for invalid billing period formats."""
        invalid_formats = [
            "2023",          # Missing month
            "2023-1",        # Single digit month
            "23-01",         # Two digit year
            "2023-13",       # Invalid month
            "2023/01",       # Wrong separator
            "01-2023",       # Reversed order
            "2023-00",       # Zero month
            "abc-01",        # Non-numeric year
            "2023-ab"        # Non-numeric month
        ]
        
        for invalid_format in invalid_formats:
            result = validate_billing_period(invalid_format)
            assert result is not None, f"Invalid format {invalid_format} should fail validation"
            assert result["code"] in [ERROR_INVALID_FORMAT, ERROR_INVALID_MONTH]
    
    def test_validate_billing_period_month_range(self):
        """Test validation enforces valid month range (01-12)."""
        # Test invalid months
        invalid_months = ["2023-00", "2023-13", "2023-99"]
        
        for invalid_month in invalid_months:
            result = validate_billing_period(invalid_month)
            assert result is not None
            assert result["code"] == ERROR_INVALID_MONTH
            assert "Invalid month" in result["message"]
    
    def test_validate_billing_period_year_range(self):
        """Test validation enforces reasonable year range."""
        current_year = datetime.now().year
        
        # Test years that are too old
        result = validate_billing_period("2019-06")
        assert result is not None
        assert result["code"] == ERROR_INVALID_YEAR
        assert "Invalid year: 2019" in result["message"]
        
        # Test years that are too far in future
        future_year = current_year + 10
        result = validate_billing_period(f"{future_year}-06")
        assert result is not None
        assert result["code"] == ERROR_INVALID_YEAR
        
        # Test boundary years (should be valid)
        result = validate_billing_period("2020-01")  # Minimum year
        assert result is None
        
        result = validate_billing_period(f"{current_year + 5}-12")  # Maximum year
        assert result is None
    
    def test_validate_billing_period_format_error_details(self):
        """Test validation provides detailed error information for format errors."""
        result = validate_billing_period("invalid-format")
        
        assert result["details"]["field"] == "period"
        assert result["details"]["provided_value"] == "invalid-format"
        assert result["details"]["expected_format"] == "YYYY-MM"


class TestValidateUserReferences:
    """Test user reference validation (PR003946-79)."""
    
    def test_validate_user_references_all_exist(self):
        """Test validation passes when all user references exist."""
        user_ids = ["user_001", "user_002", "user_003"]
        existing_users = ["user_001", "user_002", "user_003", "user_004"]
        
        result = validate_user_references(user_ids, existing_users)
        assert result is None
    
    def test_validate_user_references_empty_list(self):
        """Test validation passes with empty user ID list."""
        result = validate_user_references([], ["user_001", "user_002"])
        assert result is None
        
        result = validate_user_references(None, ["user_001"])
        assert result is None
    
    def test_validate_user_references_missing_users(self):
        """Test validation fails when some user references don't exist."""
        user_ids = ["user_001", "user_002", "user_999"]  # user_999 doesn't exist
        existing_users = ["user_001", "user_002", "user_003"]
        
        result = validate_user_references(user_ids, existing_users)
        
        assert result is not None
        assert result["code"] == ERROR_VALIDATION_ERROR
        assert "Referenced users do not exist: user_999" in result["message"]
        assert result["details"]["entity_type"] == "family"
        assert result["details"]["missing_references"] == ["user_999"]
        assert result["details"]["field"] == "user_references"
    
    def test_validate_user_references_multiple_missing(self):
        """Test validation correctly identifies multiple missing users."""
        user_ids = ["user_001", "user_888", "user_999"]
        existing_users = ["user_001", "user_002"]
        
        result = validate_user_references(user_ids, existing_users)
        
        assert result is not None
        assert "user_888" in result["details"]["missing_references"]
        assert "user_999" in result["details"]["missing_references"]
        assert "user_001" not in result["details"]["missing_references"]


class TestValidateParentStudentSeparation:
    """Test parent-student separation validation (PR003946-80)."""
    
    def test_validate_parent_student_separation_no_overlap(self):
        """Test validation passes when no users are both parent and student."""
        parents = ["parent_001", "parent_002"]
        students = ["student_001", "student_002", "student_003"]
        
        result = validate_parent_student_separation(parents, students)
        assert result is None
    
    def test_validate_parent_student_separation_empty_lists(self):
        """Test validation passes with empty parent or student lists."""
        # Empty parents
        result = validate_parent_student_separation([], ["student_001"])
        assert result is None
        
        # Empty students
        result = validate_parent_student_separation(["parent_001"], [])
        assert result is None
        
        # Both empty
        result = validate_parent_student_separation([], [])
        assert result is None
    
    def test_validate_parent_student_separation_overlap(self):
        """Test validation fails when users appear in both parent and student lists."""
        parents = ["parent_001", "user_dual", "parent_002"]
        students = ["student_001", "user_dual", "student_003"]
        
        result = validate_parent_student_separation(parents, students)
        
        assert result is not None
        assert result["code"] == ERROR_VALIDATION_ERROR
        assert "Users cannot be both parent and student: user_dual" in result["message"]
        assert result["details"]["entity_type"] == "family"
        assert result["details"]["conflicting_users"] == ["user_dual"]
        assert result["details"]["field"] == "parent_student_relationship"
    
    def test_validate_parent_student_separation_multiple_overlap(self):
        """Test validation identifies multiple overlapping users."""
        parents = ["parent_001", "user_dual1", "user_dual2", "parent_002"]
        students = ["user_dual1", "student_001", "user_dual2"]
        
        result = validate_parent_student_separation(parents, students)
        
        assert result is not None
        conflicting_users = set(result["details"]["conflicting_users"])
        assert conflicting_users == {"user_dual1", "user_dual2"}


class TestValidateFamilyData:
    """Test combined family data validation (PR003946-79 & PR003946-80)."""
    
    def test_validate_family_data_success(self):
        """Test validation passes for valid family data."""
        family_data = {
            "parents": ["parent_001", "parent_002"],
            "students": ["student_001", "student_002", "student_003"]
        }
        existing_users = [
            "parent_001", "parent_002", 
            "student_001", "student_002", "student_003",
            "other_user"
        ]
        
        result = validate_family_data(family_data, existing_users)
        assert result is None
    
    def test_validate_family_data_missing_user_references(self):
        """Test validation fails when user references don't exist."""
        family_data = {
            "parents": ["parent_001", "parent_999"],  # parent_999 doesn't exist
            "students": ["student_001"]
        }
        existing_users = ["parent_001", "student_001"]
        
        result = validate_family_data(family_data, existing_users)
        
        assert result is not None
        assert result["code"] == ERROR_VALIDATION_ERROR
        assert "parent_999" in result["details"]["missing_references"]
    
    def test_validate_family_data_parent_student_overlap(self):
        """Test validation fails when users are both parent and student."""
        family_data = {
            "parents": ["parent_001", "dual_user"],
            "students": ["student_001", "dual_user"]
        }
        existing_users = ["parent_001", "dual_user", "student_001"]
        
        result = validate_family_data(family_data, existing_users)
        
        assert result is not None
        assert result["code"] == ERROR_VALIDATION_ERROR
        assert "dual_user" in result["details"]["conflicting_users"]
    
    def test_validate_family_data_missing_keys(self):
        """Test validation handles missing parents/students keys gracefully."""
        # Missing parents key
        family_data = {"students": ["student_001"]}
        existing_users = ["student_001"]
        
        result = validate_family_data(family_data, existing_users)
        assert result is None
        
        # Missing students key
        family_data = {"parents": ["parent_001"]}
        existing_users = ["parent_001"]
        
        result = validate_family_data(family_data, existing_users)
        assert result is None
        
        # Both missing (empty family)
        family_data = {}
        existing_users = []
        
        result = validate_family_data(family_data, existing_users)
        assert result is None
    
    def test_validate_family_data_precedence(self):
        """Test validation returns user reference errors before parent-student conflicts."""
        # This tests that user reference validation happens first
        family_data = {
            "parents": ["parent_001", "nonexistent_user"],
            "students": ["student_001", "parent_001"]  # Also creates parent-student conflict
        }
        existing_users = ["parent_001", "student_001"]
        
        result = validate_family_data(family_data, existing_users)
        
        # Should return user reference error first (nonexistent_user)
        assert result is not None
        assert "nonexistent_user" in result["details"]["missing_references"]
        
        # Now test that parent-student validation runs when user references are valid
        family_data = {
            "parents": ["parent_001", "dual_user"],
            "students": ["student_001", "dual_user"]
        }
        existing_users = ["parent_001", "dual_user", "student_001"]
        
        result = validate_family_data(family_data, existing_users)
        
        assert result is not None
        assert "dual_user" in result["details"]["conflicting_users"]


class TestValidationErrorConstants:
    """Test that error code constants are properly defined."""
    
    def test_error_constants_exist(self):
        """Test that all error code constants are defined."""
        assert ERROR_INVALID_REQUEST == "invalid_request"
        assert ERROR_INVALID_FILTER == "invalid_filter"
        assert ERROR_INVALID_FORMAT == "invalid_format"
        assert ERROR_INVALID_MONTH == "invalid_month"
        assert ERROR_INVALID_YEAR == "invalid_year"
        assert ERROR_VALIDATION_ERROR == "validation_error"
    
    def test_error_constants_used_correctly(self):
        """Test that functions use the correct error constants."""
        # Test validate_no_client_id uses ERROR_INVALID_REQUEST
        result = validate_no_client_id({"id": "test"}, "id")
        assert result["code"] == ERROR_INVALID_REQUEST
        
        # Test validate_animal_status_filter uses ERROR_INVALID_FILTER
        result = validate_animal_status_filter("invalid")
        assert result["code"] == ERROR_INVALID_FILTER
        
        # Test validate_billing_period uses format/month/year errors appropriately
        result = validate_billing_period("invalid")
        assert result["code"] == ERROR_INVALID_FORMAT
        
        result = validate_billing_period("2023-13")
        assert result["code"] == ERROR_INVALID_MONTH
        
        result = validate_billing_period("2019-01")
        assert result["code"] == ERROR_INVALID_YEAR
        
        # Test family validation uses ERROR_VALIDATION_ERROR
        result = validate_user_references(["missing"], [])
        assert result["code"] == ERROR_VALIDATION_ERROR
        
        result = validate_parent_student_separation(["user"], ["user"])
        assert result["code"] == ERROR_VALIDATION_ERROR


class TestValidationIntegration:
    """Integration tests for validation functions working together."""
    
    def test_validation_error_format_consistency(self):
        """Test that all validation functions return consistent error format."""
        # Generate errors from different validation functions
        errors = [
            validate_no_client_id({"id": "test"}, "id"),
            validate_animal_status_filter("invalid"),
            validate_billing_period("invalid"),
            validate_user_references(["missing"], []),
            validate_parent_student_separation(["user"], ["user"])
        ]
        
        for error in errors:
            assert error is not None
            
            # All errors should have consistent structure
            assert "code" in error
            assert "message" in error
            assert "details" in error
            
            # All errors should have error_type in details
            assert "error_type" in error["details"]
            
            # Message should be a non-empty string
            assert isinstance(error["message"], str)
            assert len(error["message"]) > 0
            
            # Code should match the error_type
            assert error["code"] == error["details"]["error_type"]
    
    def test_validation_success_consistency(self):
        """Test that successful validations consistently return None."""
        successful_validations = [
            validate_no_client_id({}, "id"),
            validate_animal_status_filter("active"),
            validate_billing_period("2023-06"),
            validate_user_references(["user"], ["user"]),
            validate_parent_student_separation(["parent"], ["student"])
        ]
        
        for result in successful_validations:
            assert result is None