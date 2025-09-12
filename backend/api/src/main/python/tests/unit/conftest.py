"""
Test configuration and fixtures for comprehensive unit tests.

PR003946-94: Unit test fixtures and configuration
- File persistence mode for testing isolation
- Common test data and utilities
- HTML reporting configuration
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# Ensure file persistence mode for all tests
os.environ["PERSISTENCE_MODE"] = "file"
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
        "animalName": "Test Sample Lion",
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
def boundary_value_generator():
    """Generator for boundary value testing."""
    class BoundaryValueGenerator:
        def null_empty_values(self):
            return [None, "", " ", "   ", "\t", "\n"]
        
        def long_strings(self, base_length=100):
            return [
                "a" * (base_length - 1),
                "a" * base_length, 
                "a" * (base_length + 1),
                "a" * (base_length * 2),
                "a" * 1000,
                "a" * 10000
            ]
        
        def special_characters(self):
            return [
                "test@example.com",
                "José García",
                "测试用户",
                "🦁🐅🐘🦅",
                "<script>alert('test')</script>",
                "'; DROP TABLE test; --",
                "test\nwith\nnewlines",
                '"quoted"',
                "back\\slash\\test",
                "unicode: àáâãäåæç"
            ]
        
        def numeric_boundaries(self):
            return [
                -999999999, -1, 0, 1, 999999999,
                2147483647, 2147483648, -2147483648, -2147483649,
                3.14159, -3.14159, 0.0, 1.0, -1.0
            ]
        
        def invalid_ids(self):
            return [
                "", " ", "   ",           # Empty/whitespace
                "invalid id spaces",      # Spaces
                "invalid/id/slashes",     # Slashes
                "invalid@id#symbols",     # Special chars
                "a" * 200,               # Too long
                "123",                   # Numbers only
                "ID_WITH_CAPS",          # All caps
                "mixed_CASE_id",         # Mixed case
                None                     # Null
            ]
    
    return BoundaryValueGenerator()


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