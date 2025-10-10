#!/usr/bin/env python3
"""
Comprehensive E2E Test Suite for CMZ API
Consolidates all integration and E2E tests including:
- API Validation Epic
- ChatGPT Integration Epic
- Guardrails System E2E
- Animal Config Persistence
- Endpoint Tests
"""

import pytest
import os
import sys

# Ensure proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules to ensure they're included
from test_api_validation_epic import *
from test_chatgpt_integration_epic import *
from test_guardrails_system_e2e import *
from test_animal_config_persistence import *
from test_endpoints import *

# Test suite metadata
TEST_SUITE_INFO = {
    'name': 'CMZ API Comprehensive E2E Test Suite',
    'version': '1.0.0',
    'includes': [
        'API Validation Epic (PR003946)',
        'ChatGPT Integration (PR003946-176-179)',
        'Guardrails System E2E',
        'Animal Config Persistence',
        'General Endpoint Tests'
    ]
}

@pytest.mark.integration
class TestSuiteInfo:
    """Provides information about the test suite"""

    def test_suite_info(self):
        """Display test suite information"""
        print("\n" + "="*60)
        print(f"Running: {TEST_SUITE_INFO['name']}")
        print(f"Version: {TEST_SUITE_INFO['version']}")
        print("Includes:")
        for item in TEST_SUITE_INFO['includes']:
            print(f"  - {item}")
        print("="*60)
        assert True  # Always passes, just for info

def run_all_tests():
    """Programmatic test runner for all E2E tests"""
    # Configure pytest arguments
    args = [
        __file__,
        '-v',
        '--tb=short',
        '--cov=openapi_server',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--junit-xml=reports/junit_e2e.xml',
        '--html=reports/e2e_test_report.html',
        '--self-contained-html',
        '-m', 'not slow',  # Skip slow tests in regular runs
    ]

    # Add markers for specific test categories
    if os.getenv('RUN_SLOW_TESTS'):
        args.remove('-m')
        args.remove('not slow')

    # Run the tests
    return pytest.main(args)

if __name__ == '__main__':
    # Set up environment if needed
    if not os.getenv('AWS_PROFILE'):
        os.environ['AWS_PROFILE'] = 'cmz'

    # Run the comprehensive test suite
    exit_code = run_all_tests()