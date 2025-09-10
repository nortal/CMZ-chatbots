#!/usr/bin/env python3
"""
CMZ API Integration Test Runner

This script runs integration tests against Jira ticket requirements.
Provides different test modes for TDD development.

Usage:
    python run_integration_tests.py [options]

Examples:
    # Run all integration tests
    python run_integration_tests.py

    # Run only validation tests
    python run_integration_tests.py --validation

    # Run tests for specific ticket
    python run_integration_tests.py --ticket PR003946-90

    # Run with coverage
    python run_integration_tests.py --coverage

    # Run in TDD mode (watch for changes)
    python run_integration_tests.py --tdd
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run shell command with error handling"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def install_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "-r", "requirements-test.txt"
    ], check=False)


def run_integration_tests(args):
    """Run integration tests with specified options"""
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path
    if args.validation:
        cmd.extend(["tests/integration/test_api_validation_epic.py"])
    elif args.endpoints:
        cmd.extend(["tests/integration/test_endpoints.py"])  
    elif args.ticket:
        # Run tests for specific ticket
        cmd.extend([
            "tests/integration/",
            "-k", f"pr{args.ticket.lower().replace('-', '_')}"
        ])
    else:
        cmd.extend(["tests/integration/"])
    
    # Add markers
    if args.auth:
        cmd.extend(["-m", "auth"])
    elif args.data_integrity:
        cmd.extend(["-m", "data_integrity"])
    elif args.soft_delete:
        cmd.extend(["-m", "soft_delete"])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    elif not args.quiet:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=openapi_server", 
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add HTML report
    if args.html_report:
        cmd.extend([
            "--html=reports/integration_test_report.html",
            "--self-contained-html"
        ])
    
    # Add JUnit XML for CI
    if args.junit:
        cmd.extend(["--junit-xml=reports/integration_junit.xml"])
    
    # Run tests
    return run_command(cmd, check=False)


def run_tdd_mode():
    """Run tests in TDD mode with file watching"""
    try:
        import watchdog
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class TestHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith('.py'):
                    print(f"\nFile changed: {event.src_path}")
                    print("Re-running tests...")
                    run_command([
                        sys.executable, "-m", "pytest", 
                        "tests/integration/", 
                        "-v", "--tb=short"
                    ], check=False)
        
        observer = Observer()
        observer.schedule(TestHandler(), ".", recursive=True)
        observer.start()
        
        print("TDD Mode: Watching for file changes...")
        print("Press Ctrl+C to exit")
        
        # Initial test run
        run_command([
            sys.executable, "-m", "pytest",
            "tests/integration/",
            "-v", "--tb=short"
        ], check=False)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        
    except ImportError:
        print("TDD mode requires watchdog: pip install watchdog")
        return False
    
    return True


def generate_test_report():
    """Generate comprehensive test report"""
    
    # Create reports directory
    Path("reports").mkdir(exist_ok=True)
    
    print("Generating comprehensive test report...")
    
    # Run tests with all reporting options
    success = run_command([
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "--html=reports/integration_report.html",
        "--junit-xml=reports/integration_junit.xml",
        "--cov=openapi_server",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml:reports/coverage.xml",
        "-v"
    ], check=False)
    
    if success:
        print("\nTest reports generated:")
        print("- HTML Report: reports/integration_report.html")
        print("- JUnit XML: reports/integration_junit.xml")
        print("- Coverage HTML: reports/coverage/index.html")
        print("- Coverage XML: reports/coverage.xml")
    
    return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CMZ API Integration Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validation              # Run validation tests only
  %(prog)s --ticket PR003946-90      # Run tests for specific ticket
  %(prog)s --coverage --html-report  # Run with coverage and HTML report
  %(prog)s --tdd                     # Run in TDD watch mode
        """
    )
    
    # Test selection
    parser.add_argument("--validation", action="store_true",
                       help="Run API validation epic tests")
    parser.add_argument("--endpoints", action="store_true", 
                       help="Run endpoint-specific tests")
    parser.add_argument("--ticket", 
                       help="Run tests for specific ticket (e.g., PR003946-90)")
    
    # Test markers
    parser.add_argument("--auth", action="store_true",
                       help="Run authentication tests only")
    parser.add_argument("--data-integrity", action="store_true",
                       help="Run data integrity tests only")
    parser.add_argument("--soft-delete", action="store_true",
                       help="Run soft delete tests only")
    
    # Output options  
    parser.add_argument("--coverage", action="store_true",
                       help="Include coverage reporting")
    parser.add_argument("--html-report", action="store_true",
                       help="Generate HTML test report")
    parser.add_argument("--junit", action="store_true",
                       help="Generate JUnit XML report")
    parser.add_argument("--report", action="store_true",
                       help="Generate comprehensive test report")
    
    # Execution options
    parser.add_argument("--parallel", type=int, metavar="N",
                       help="Run tests in parallel with N workers")
    parser.add_argument("--tdd", action="store_true",
                       help="Run in TDD mode (watch for changes)")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install test dependencies first")
    
    # Verbosity
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Quiet output")
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print("Failed to install dependencies")
            return 1
    
    # Handle special modes
    if args.tdd:
        return 0 if run_tdd_mode() else 1
    
    if args.report:
        return 0 if generate_test_report() else 1
    
    # Run integration tests
    success = run_integration_tests(args)
    
    return 0 if success else 1


if __name__ == "__main__":
    import time
    sys.exit(main())