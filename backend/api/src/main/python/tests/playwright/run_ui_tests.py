#!/usr/bin/env python3
"""
UI Test Runner for CMZ Chatbot Platform
PR003946-96: Integrated playwright testing

Slash command integration: /test-ui
Provides comprehensive UI testing with health reporting
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class UITestRunner:
    """Comprehensive UI test runner with reporting and analysis"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.reports_dir = self.script_dir / "reports"
        self.playwright_config = self.script_dir / "config" / "playwright.config.js"
        self.feature_mapping = self.script_dir / "config" / "feature-mapping.json"
        
    def setup_environment(self):
        """Setup test environment and dependencies"""
        print("🔧 Setting up UI testing environment...")
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # Set environment variables for file persistence mode
        os.environ["PERSISTENCE_MODE"] = "file"
        os.environ["BACKEND_URL"] = os.getenv("BACKEND_URL", "http://localhost:8080")
        os.environ["FRONTEND_URL"] = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Check if node_modules exists, install if needed
        node_modules = self.script_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing Playwright dependencies...")
            self.run_command(["npm", "install"], cwd=self.script_dir)
            
        # Install browsers if needed
        print("🌐 Ensuring browsers are installed...")
        self.run_command(["npx", "playwright", "install"], cwd=self.script_dir)
            
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run shell command with error handling"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.script_dir,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError as e:
            print(f"❌ Command not found: {' '.join(cmd)}")
            print(f"   Error: {e}")
            sys.exit(1)
            
    def run_tests(self, 
                  features: Optional[List[str]] = None,
                  browsers: Optional[List[str]] = None, 
                  headed: bool = False,
                  debug: bool = False,
                  performance_only: bool = False,
                  mobile_only: bool = False) -> Dict:
        """Run Playwright tests with specified options"""
        
        print("🎭 Running Playwright UI tests...")
        
        # Build Playwright command
        cmd = ["npx", "playwright", "test"]
        
        # Add configuration
        cmd.extend(["--config", str(self.playwright_config)])
        
        # Add feature-specific tests
        if features:
            for feature in features:
                spec_file = self.script_dir / "specs" / "ui-features" / f"{feature}.spec.js"
                if spec_file.exists():
                    cmd.append(str(spec_file))
                else:
                    print(f"⚠️  Feature test not found: {feature}")
                    
        # Add browser selection
        if browsers:
            for browser in browsers:
                cmd.extend(["--project", browser])
        elif mobile_only:
            cmd.extend(["--project", "Mobile Chrome", "--project", "Mobile Safari"])
            
        # Add execution options
        if headed:
            cmd.append("--headed")
        if debug:
            cmd.append("--debug")
        if performance_only:
            cmd.append("--grep=performance")
            
        # Add reporting options
        cmd.extend([
            "--reporter=json",
            "--reporter=html",
            "--reporter=junit"
        ])
        
        # Set output paths
        cmd.extend([
            f"--output-dir={self.reports_dir}/test-results"
        ])
        
        print(f"🚀 Executing: {' '.join(cmd[2:])}")  # Hide npx playwright for cleaner output
        
        # Run tests
        result = self.run_command(cmd)
        
        # Process results
        test_results = self.process_test_results(result)
        
        return test_results
        
    def process_test_results(self, result: subprocess.CompletedProcess) -> Dict:
        """Process and analyze test results"""
        
        # Load JSON results if available
        json_results_path = self.reports_dir / "test-results.json"
        
        test_data = {
            "exit_code": result.returncode,
            "execution_time": datetime.now().isoformat(),
            "success": result.returncode == 0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "pass_rate": 0
        }
        
        if json_results_path.exists():
            try:
                with open(json_results_path, 'r') as f:
                    playwright_results = json.load(f)
                    
                # Extract test statistics
                if "suites" in playwright_results:
                    for suite in playwright_results["suites"]:
                        if "specs" in suite:
                            for spec in suite["specs"]:
                                test_data["total_tests"] += 1
                                if spec.get("outcome") == "expected":
                                    test_data["passed_tests"] += 1
                                else:
                                    test_data["failed_tests"] += 1
                                    
                # Calculate pass rate
                if test_data["total_tests"] > 0:
                    test_data["pass_rate"] = round(
                        (test_data["passed_tests"] / test_data["total_tests"]) * 100, 1
                    )
                    
            except Exception as e:
                print(f"⚠️  Could not parse test results: {e}")
                
        return test_data
        
    def generate_health_report(self) -> str:
        """Generate comprehensive UI health report"""
        print("📊 Generating UI health report...")
        
        report_script = self.script_dir / "scripts" / "generate-ui-health-report.js"
        
        if report_script.exists():
            result = self.run_command(["node", str(report_script)])
            if result.returncode == 0:
                report_path = self.reports_dir / "ui-health-report.html"
                return str(report_path)
            else:
                print(f"⚠️  Failed to generate health report: {result.stderr}")
                
        return ""
        
    def display_results(self, test_results: Dict, report_path: str = ""):
        """Display test results in a user-friendly format"""
        
        print("\n" + "="*60)
        print("🏥 UI TEST RESULTS SUMMARY")
        print("="*60)
        
        # Test execution summary
        status_icon = "✅" if test_results["success"] else "❌"
        print(f"{status_icon} Test Execution: {'PASSED' if test_results['success'] else 'FAILED'}")
        print(f"📊 Pass Rate: {test_results['pass_rate']}%")
        print(f"✅ Passed: {test_results['passed_tests']}")
        print(f"❌ Failed: {test_results['failed_tests']}")
        print(f"📈 Total: {test_results['total_tests']}")
        
        # Quality gate assessment
        quality_gate = "✅ PASS" if test_results["pass_rate"] >= 85 else "❌ FAIL"
        print(f"🎯 Quality Gate: {quality_gate}")
        
        # Report links
        print(f"\n📋 DETAILED REPORTS:")
        
        html_report = self.reports_dir / "html-report" / "index.html"
        if html_report.exists():
            print(f"   🎭 Playwright Report: file://{html_report.absolute()}")
            
        if report_path:
            print(f"   🏥 Health Report: file://{Path(report_path).absolute()}")
            
        json_summary = self.reports_dir / "ui-health-summary.json"
        if json_summary.exists():
            print(f"   📊 JSON Summary: {json_summary}")
            
        # Recommendations
        if test_results["pass_rate"] < 90:
            print(f"\n💡 RECOMMENDATIONS:")
            print(f"   • Focus on failing test cases")
            print(f"   • Review UI element selectors")
            print(f"   • Check backend integration points")
            if test_results["pass_rate"] < 50:
                print(f"   • Consider major refactoring for consistently failing features")
                
        print("="*60 + "\n")
        
    def validate_feature_mapping(self) -> bool:
        """Validate feature mapping configuration"""
        if not self.feature_mapping.exists():
            print(f"❌ Feature mapping not found: {self.feature_mapping}")
            return False
            
        try:
            with open(self.feature_mapping, 'r') as f:
                mapping = json.load(f)
                
            features = mapping.get("features", {})
            print(f"📋 Found {len(features)} UI features in mapping")
            
            for feature_name, feature_data in features.items():
                controls = feature_data.get("controls", [])
                print(f"   • {feature_name}: {len(controls)} controls")
                
            return True
            
        except Exception as e:
            print(f"❌ Invalid feature mapping: {e}")
            return False
            
    def run_full_test_suite(self, **options) -> Dict:
        """Run complete UI test suite with reporting"""
        
        try:
            # Setup
            self.setup_environment()
            
            # Validate configuration
            if not self.validate_feature_mapping():
                return {"success": False, "error": "Invalid feature mapping"}
                
            # Run tests
            results = self.run_tests(**options)
            
            # Generate reports
            report_path = self.generate_health_report()
            
            # Display results
            self.display_results(results, report_path)
            
            return results
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="CMZ Chatbot UI Test Runner")
    
    parser.add_argument(
        "--features", 
        nargs="*",
        help="Specific features to test (authentication, dashboard, chat, admin)"
    )
    parser.add_argument(
        "--browsers",
        nargs="*", 
        choices=["chromium", "firefox", "webkit"],
        help="Specific browsers to test"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run tests in headed mode (visible browser)"
    )
    parser.add_argument(
        "--debug",
        action="store_true", 
        help="Run tests in debug mode"
    )
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Run mobile-only tests"
    )
    parser.add_argument(
        "--performance", 
        action="store_true",
        help="Run performance tests only"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate configuration only, don't run tests"
    )
    
    args = parser.parse_args()
    
    runner = UITestRunner()
    
    if args.validate_only:
        valid = runner.validate_feature_mapping()
        sys.exit(0 if valid else 1)
        
    # Run tests
    results = runner.run_full_test_suite(
        features=args.features,
        browsers=args.browsers,
        headed=args.headed,
        debug=args.debug,
        mobile_only=args.mobile,
        performance_only=args.performance
    )
    
    # Exit with appropriate code
    sys.exit(0 if results.get("success", False) else 1)

if __name__ == "__main__":
    main()