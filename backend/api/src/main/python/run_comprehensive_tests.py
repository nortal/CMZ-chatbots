#!/usr/bin/env python3
"""
Comprehensive test runner for PR003946-94.

This script runs all unit tests and generates HTML reports with:
- Pass/fail statistics by endpoint
- Boundary value testing results  
- Coverage summary for implemented vs total endpoints
- Expandable test details
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def ensure_reports_directory():
    """Create reports directory if it doesn't exist."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

def run_unit_tests():
    """Run comprehensive unit tests with HTML reporting."""
    print("🧪 Running comprehensive unit tests (PR003946-94)...")
    print(f"📁 Persistence Mode: FILE (isolated testing)")
    print(f"📊 Generating HTML reports...")
    
    reports_dir = ensure_reports_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set environment for testing
    env = os.environ.copy()
    env["PERSISTENCE_MODE"] = "file"
    
    # Run pytest with HTML reporting and coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        f"--html=reports/unit_test_report_{timestamp}.html",
        "--self-contained-html",
        "--tb=short",
        "-v",
        "--durations=10",
        f"--junitxml=reports/junit_unit_{timestamp}.xml"
    ]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        print("\n" + "="*60)
        print("📋 TEST EXECUTION SUMMARY")
        print("="*60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed or had issues")
            
        print(f"📄 HTML Report: reports/unit_test_report_{timestamp}.html")
        print(f"📊 JUnit XML: reports/junit_unit_{timestamp}.xml")
        
        # Show pytest output
        if result.stdout:
            print("\n📝 Test Output:")
            print(result.stdout[-2000:])  # Last 2000 chars to avoid overwhelming output
            
        if result.stderr and result.returncode != 0:
            print("\n⚠️ Error Output:")
            print(result.stderr[-1000:])
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return 1

def run_integration_tests():
    """Run existing integration tests for comparison."""
    print("\n🔗 Running integration tests for comparison...")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/integration/test_api_validation_epic.py",
        "-v", "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 Integration Test Results:")
        if result.stdout:
            # Extract summary line
            lines = result.stdout.split('\n')
            summary_lines = [line for line in lines if 'passed' in line and ('failed' in line or 'error' in line)]
            if summary_lines:
                print(f"   {summary_lines[-1]}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"⚠️ Integration tests failed to run: {e}")
        return False

def generate_coverage_summary():
    """Generate endpoint coverage summary."""
    print("\n📈 ENDPOINT COVERAGE ANALYSIS")
    print("="*60)
    
    # Expected endpoints from OpenAPI spec
    expected_endpoints = [
        '/', '/admin', '/member', '/auth', '/auth/refresh', '/auth/logout', 
        '/auth/reset_password', '/me', '/user', '/user/{userId}', '/family',
        '/family/{familyId}', '/animal_list', '/animal', '/animal/{id}',
        '/animal_config', '/animal_details', '/system_health', '/feature_flags',
        '/performance_metrics', '/billing', '/convo_history', '/convo_turn',
        '/knowledge_article', '/logs', '/media', '/upload_media', 
        '/user_details', '/user_details/{userId}', '/summarize_convo'
    ]
    
    # Endpoints with test coverage (from our test classes)
    tested_endpoints = [
        '/', '/admin', '/member',                    # UI endpoints
        '/auth', '/auth/refresh', '/auth/logout',    # Auth endpoints  
        '/me', '/user', '/user/{userId}',           # User endpoints
        '/family', '/family/{familyId}',            # Family endpoints
        '/animal_list', '/animal', '/animal/{id}',  # Animal endpoints
        '/system_health', '/feature_flags', '/performance_metrics'  # System endpoints
    ]
    
    total_endpoints = len(expected_endpoints)
    tested_count = len(tested_endpoints)
    coverage_percentage = (tested_count / total_endpoints) * 100
    
    print(f"📊 Total Endpoints: {total_endpoints}")
    print(f"✅ Tested Endpoints: {tested_count}")  
    print(f"📈 Coverage: {coverage_percentage:.1f}%")
    
    untested = set(expected_endpoints) - set(tested_endpoints)
    if untested:
        print(f"\n⚠️ Untested Endpoints ({len(untested)}):")
        for endpoint in sorted(untested):
            print(f"   • {endpoint}")
    
    return coverage_percentage

def main():
    """Main test execution function."""
    print("🚀 CMZ API Comprehensive Testing Suite (PR003946-94)")
    print("="*60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run unit tests
    unit_result = run_unit_tests()
    
    # Run integration tests for comparison 
    integration_result = run_integration_tests()
    
    # Generate coverage summary
    coverage = generate_coverage_summary()
    
    print("\n" + "="*60)
    print("🎯 FINAL SUMMARY")
    print("="*60)
    print(f"Unit Tests: {'✅ PASSED' if unit_result == 0 else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_result else '❌ FAILED'}")
    print(f"Endpoint Coverage: {coverage:.1f}%")
    print(f"Persistence Mode: FILE (isolated)")
    
    if unit_result == 0 and coverage > 75:
        print("\n🎉 SUCCESS: Comprehensive testing implementation complete!")
        print("   ✅ All unit tests passing")
        print("   ✅ Good endpoint coverage")
        print("   ✅ HTML reports generated")
        print("   ✅ Ready for GitLab CI integration")
    else:
        print("\n⚠️ NEEDS ATTENTION:")
        if unit_result != 0:
            print("   ❌ Unit tests have failures")
        if coverage <= 75:
            print("   📉 Endpoint coverage below 75%")
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        html_reports = list(reports_dir.glob("unit_test_report_*.html"))
        if html_reports:
            latest_report = max(html_reports, key=lambda x: x.stat().st_mtime)
            print(f"\n📄 Latest HTML Report: {latest_report}")
    
    return unit_result

if __name__ == "__main__":
    sys.exit(main())