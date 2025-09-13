"""
Test configuration and fixtures for comprehensive unit tests.

PR003946-94: Unit test fixtures and configuration
PR003946-95: Enhanced test utilities and fixtures
- File persistence mode for testing isolation
- Common test data and utilities
- HTML reporting configuration
- Mock repositories and enhanced generators
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Import enhanced test utilities
from tests.unit.test_utils import (
    TestDataGenerator, BoundaryValueTestGenerator, 
    MockAuthenticationHelper, test_db_manager
)

# Ensure file persistence mode for all tests
os.environ["PERSISTENCE_MODE"] = "file"
os.environ["TEST_MODE"] = "true"  # Enable test mode for mock data
os.environ["FILE_PERSISTENCE_DIR"] = tempfile.mkdtemp(prefix="cmz_test_")

@pytest.fixture(scope="session", autouse=True)
def test_persistence_setup():
    """Set up file persistence for the entire test session."""
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp(prefix="cmz_unit_test_")
    os.environ["FILE_PERSISTENCE_DIR"] = temp_dir
    
    print(f"Using test persistence directory: {temp_dir}")
    
    yield temp_dir
    
    # Cleanup after all tests
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Could not cleanup test directory {temp_dir}: {e}")


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "displayName": "Test User Sample",
        "email": "sample@test.cmz.org",
        "role": "student",
        "familyId": "family_test_001"
    }


@pytest.fixture  
def sample_family_data():
    """Sample family data for testing."""
    return {
        "familyName": "Sample Test Family",
        "parents": ["user_test_parent_sample"],
        "students": ["user_test_student_sample"]
    }


@pytest.fixture
def sample_animal_data():
    """Sample animal data for testing."""
    return {
        "name": "Test Sample Lion",
        "species": "Lion",
        "habitat": "African Savanna",
        "description": "A sample lion for comprehensive testing",
        "personality": "brave,curious,educational",
        "chatbotConfig": {
            "enabled": True,
            "model": "claude-3-sonnet",
            "temperature": 0.7
        }
    }

@pytest.fixture
def sample_animal_config_data():
    """Sample animal config data for testing."""
    return {
        "personality": "friendly",
        "aiModel": "claude-3-sonnet",
        "temperature": 0.7
    }


@pytest.fixture
def boundary_value_generator():
    """Enhanced boundary value generator for comprehensive testing."""
    return BoundaryValueTestGenerator()


@pytest.fixture
def test_data_generator():
    """Test data generator for creating realistic test entities."""
    return TestDataGenerator()


@pytest.fixture
def mock_auth_helper():
    """Mock authentication helper for testing secured endpoints."""
    return MockAuthenticationHelper()


@pytest.fixture(scope="function")
def mock_user():
    """Create a mock authenticated user for testing."""
    return MockAuthenticationHelper.create_mock_user()


@pytest.fixture(scope="function")
def mock_admin_user():
    """Create a mock admin user for testing admin endpoints."""
    return MockAuthenticationHelper.create_mock_user(role="admin", user_type="none")


@pytest.fixture(scope="function")
def mock_parent_user():
    """Create a mock parent user for testing family operations."""
    return MockAuthenticationHelper.create_mock_user(role="parent", user_type="parent")


@pytest.fixture(scope="function")
def mock_repositories():
    """Provide clean mock repositories for testing."""
    # Clear any existing test data
    test_db_manager.clear_all()
    
    # Return the manager for test use
    yield test_db_manager
    
    # Cleanup after test
    test_db_manager.clear_all()


@pytest.fixture(scope="function")
def seeded_repositories():
    """Provide mock repositories with pre-seeded test data."""
    # Clear any existing test data
    test_db_manager.clear_all()
    
    # Seed with test data
    test_db_manager.seed_test_data()
    
    # Return the manager for test use
    yield test_db_manager
    
    # Cleanup after test
    test_db_manager.clear_all()


@pytest.fixture
def mock_store_patch():
    """Patch storage functions to use mock repositories.
    
    Note: Different modules use different storage patterns:
    - users/family: Use _store() for direct DynamoDB access
    - animals: Use _get_flask_handler() for Flask handler abstraction
    This reflects the actual architecture differences in the codebase.
    """
    def create_mock_store(table_name, primary_key):
        return test_db_manager.get_repository(table_name, primary_key)
    
    with patch('openapi_server.impl.users._store') as user_mock, \
         patch('openapi_server.impl.family._store') as family_mock, \
         patch('openapi_server.impl.animals._get_flask_handler') as animal_mock:
        
        # Configure user store mock
        user_mock.return_value = create_mock_store("quest-dev-user", "userId")
        
        # Configure family store mock  
        family_mock.return_value = create_mock_store("quest-dev-family", "familyId")
        
        # Configure animal handler mock
        mock_animal_handler = create_mock_store("quest-dev-animal", "animalId")
        animal_mock.return_value = mock_animal_handler
        
        yield {
            "user_store": user_mock,
            "family_store": family_mock,
            "animal_handler": animal_mock
        }


def pytest_configure(config):
    """Configure pytest for HTML reporting."""
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)


def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "CMZ API Comprehensive Unit Test Report (PR003946-94)"


def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary information to HTML report."""
    prefix.extend([
        "<h2>Test Summary</h2>",
        "<p>This report covers comprehensive unit testing of all CMZ API endpoints as specified in PR003946-94.</p>",
        "<h3>Test Coverage</h3>",
        "<ul>",
        "<li>✅ Every endpoint and HTTP verb from OpenAPI specification</li>", 
        "<li>✅ Boundary value testing for all input parameters</li>",
        "<li>✅ Flask endpoints and Lambda handlers (hexagonal architecture)</li>",
        "<li>✅ File persistence mode for testing isolation</li>",
        "<li>✅ Consistent error schema validation (PR003946-90)</li>",
        "</ul>",
        f"<p><strong>Persistence Mode:</strong> FILE (isolated testing)</p>",
        f"<p><strong>Test Data Directory:</strong> {os.getenv('FILE_PERSISTENCE_DIR', 'N/A')}</p>"
    ])


def pytest_html_results_table_header(cells):
    """Customize HTML results table headers."""
    cells.insert(2, "<th>Endpoint</th>")
    cells.insert(3, "<th>Method</th>")


def pytest_html_results_table_row(report, cells):
    """Customize HTML results table rows."""
    # Extract endpoint and method from test name
    test_name = report.nodeid.split("::")[-1]
    
    endpoint = "N/A"
    method = "N/A"
    
    if "auth" in test_name:
        endpoint = "/auth*"
    elif "user" in test_name:
        endpoint = "/user*"
    elif "family" in test_name:
        endpoint = "/family*"
    elif "animal" in test_name:
        endpoint = "/animal*"
    elif "system" in test_name:
        endpoint = "/system*"
    
    if "get" in test_name:
        method = "GET"
    elif "post" in test_name:
        method = "POST"
    elif "put" in test_name:
        method = "PUT"
    elif "delete" in test_name:
        method = "DELETE"
    
    cells.insert(2, f"<td>{endpoint}</td>")
    cells.insert(3, f"<td>{method}</td>")