#!/usr/bin/env python3
"""
Script to check test coverage and generate report
Task T012: Verify 85% test coverage achieved
"""

import subprocess
import sys
import os
import re

def run_coverage():
    """Run pytest with coverage and parse results"""

    print("=" * 80)
    print("🔍 CMZ Chatbots Test Coverage Report")
    print("=" * 80)

    # Set Python path
    backend_path = os.path.join(os.path.dirname(__file__), '../backend/api')
    os.chdir(backend_path)

    # Identify test directories
    test_dirs = [
        'src/main/python/tests/unit',
        'src/main/python/tests/integration',
        'src/main/python/tests/contract'
    ]

    # Count test files
    test_file_count = 0
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for root, dirs, files in os.walk(test_dir):
                test_file_count += sum(1 for f in files if f.startswith('test_') and f.endswith('.py'))

    print(f"\n📊 Test Statistics:")
    print(f"  - Test files found: {test_file_count}")
    print(f"  - Test directories: {len(test_dirs)}")

    # Run coverage command
    print("\n🧪 Running test coverage analysis...")
    print("-" * 40)

    cmd = [
        sys.executable, '-m', 'pytest',
        '--cov=src/main/python/openapi_server',
        '--cov-report=term-missing:skip-covered',
        '--cov-report=html',
        '-q',
        '--tb=no'
    ]

    # Add test directories
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            cmd.append(test_dir)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, 'PYTHONPATH': 'src/main/python'}
        )

        # Parse coverage percentage
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
        if coverage_match:
            coverage_pct = int(coverage_match.group(1))
        else:
            # Try alternative format
            coverage_match = re.search(r'TOTAL.*?(\d+)%', result.stdout)
            if coverage_match:
                coverage_pct = int(coverage_match.group(1))
            else:
                coverage_pct = 0

        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)

    except Exception as e:
        print(f"Error running coverage: {e}")
        coverage_pct = 0

    # Summary
    print("\n" + "=" * 80)
    print("📈 Coverage Summary")
    print("=" * 80)

    print(f"\n  Current Coverage: {coverage_pct}%")
    print(f"  Target Coverage: 85%")

    if coverage_pct >= 85:
        print(f"  ✅ TARGET ACHIEVED! Coverage is {coverage_pct}%")
    else:
        gap = 85 - coverage_pct
        print(f"  ⚠️  Gap to target: {gap}%")
        print(f"\n  Recommendations to reach 85%:")
        print(f"    - Add more unit tests for handlers.py")
        print(f"    - Test error handling paths")
        print(f"    - Cover DynamoDB utility functions")
        print(f"    - Add integration tests for all endpoints")

    # Check for HTML report
    html_report = 'htmlcov/index.html'
    if os.path.exists(html_report):
        print(f"\n  📄 Detailed HTML report: {os.path.abspath(html_report)}")

    return coverage_pct

def analyze_uncovered_modules():
    """Analyze which modules need more tests"""

    print("\n" + "=" * 80)
    print("🔍 Uncovered Module Analysis")
    print("=" * 80)

    # Key modules to check
    key_modules = [
        'impl/handlers.py',
        'impl/utils/dynamo.py',
        'impl/auth.py',
        'impl/family.py',
        'impl/users.py',
        'impl/animals.py'
    ]

    print("\n  Priority modules for testing:")
    for module in key_modules:
        module_path = f'src/main/python/openapi_server/{module}'
        if os.path.exists(module_path):
            # Count lines for rough estimate
            with open(module_path, 'r') as f:
                lines = len(f.readlines())
            print(f"    - {module}: ~{lines} lines")

    print("\n  Test recommendations by module:")
    print("    handlers.py: Test all 62 handler functions")
    print("    dynamo.py: Test CRUD operations and error handling")
    print("    auth.py: Test all authentication modes")
    print("    family.py: Test forwarding and validation")
    print("    animals.py: Test configuration management")

def main():
    """Main execution"""

    # Run coverage analysis
    coverage_pct = run_coverage()

    # Analyze uncovered modules if below target
    if coverage_pct < 85:
        analyze_uncovered_modules()

    # Final status
    print("\n" + "=" * 80)
    print("✨ Test Coverage Analysis Complete")
    print("=" * 80)

    if coverage_pct >= 85:
        print("\n🎉 Congratulations! You've achieved the 85% coverage target!")
        print("   Phase 1 test coverage goal is COMPLETE!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Current coverage ({coverage_pct}%) is below the 85% target")
        print("   Continue adding tests to reach the goal")
        sys.exit(1)

if __name__ == '__main__':
    main()