#!/usr/bin/env python3
"""
Frontend-Backend Contract Testing
Ensures API endpoints called by frontend match backend implementation
"""

import json
import re
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Set

class ContractTester:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.frontend_path = project_root / "frontend"
        self.backend_url = "http://localhost:8080"
        self.test_results = []

    def run_contract_tests(self) -> bool:
        """Run all contract tests"""
        print("🔍 Running Frontend-Backend Contract Tests...")

        # Extract frontend API calls
        frontend_endpoints = self.extract_frontend_endpoints()
        print(f"📱 Found {len(frontend_endpoints)} frontend API calls")

        # Test each endpoint
        for endpoint_info in frontend_endpoints:
            self.test_endpoint_contract(endpoint_info)

        # Report results
        return self.report_results()

    def extract_frontend_endpoints(self) -> List[Dict]:
        """Extract all API endpoint calls from frontend code"""
        endpoints = []

        # Search in services/api.ts
        api_service = self.frontend_path / "src/services/api.ts"
        if api_service.exists():
            with open(api_service, 'r') as f:
                content = f.read()

                # Pattern to find API calls
                # Match apiRequest<Type>('/endpoint', options)
                pattern = r"apiRequest(?:<[^>]+>)?\s*\(\s*['\"`]([^'\"]+)['\"`](?:,\s*\{([^}]+)\})?"

                for match in re.finditer(pattern, content):
                    endpoint = match.group(1)
                    options = match.group(2) or ""

                    # Determine HTTP method
                    method = "GET"
                    if "method:" in options:
                        method_match = re.search(r"method:\s*['\"`]([A-Z]+)['\"`]", options)
                        if method_match:
                            method = method_match.group(1)

                    endpoints.append({
                        'endpoint': endpoint,
                        'method': method,
                        'source': 'api.ts'
                    })

        # Search in hooks
        hooks_dir = self.frontend_path / "src/hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.ts"):
                with open(hook_file, 'r') as f:
                    content = f.read()

                    # Find fetch calls
                    fetch_pattern = r"fetch\s*\(\s*['\"`]([^'\"]+)['\"`]"
                    for match in re.finditer(fetch_pattern, content):
                        endpoint = match.group(1)
                        # Remove base URL if present
                        endpoint = re.sub(r"^https?://[^/]+", "", endpoint)
                        endpoints.append({
                            'endpoint': endpoint,
                            'method': 'GET',  # Default, could be improved
                            'source': hook_file.name
                        })

        return endpoints

    def test_endpoint_contract(self, endpoint_info: Dict):
        """Test if endpoint exists and responds correctly"""
        endpoint = endpoint_info['endpoint']
        method = endpoint_info['method']

        # Skip if endpoint has parameters
        if '{' in endpoint or '${' in endpoint:
            self.test_results.append({
                'endpoint': endpoint,
                'method': method,
                'status': 'SKIPPED',
                'reason': 'Parameterized endpoint'
            })
            return

        try:
            # Make test request
            url = f"{self.backend_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, timeout=2)
            elif method == 'POST':
                response = requests.post(url, json={}, timeout=2)
            elif method == 'PUT':
                response = requests.put(url, json={}, timeout=2)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=2)
            else:
                response = requests.get(url, timeout=2)

            # Check response
            if response.status_code == 404:
                self.test_results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'FAIL',
                    'reason': 'Endpoint not found (404)'
                })
            elif response.status_code >= 500:
                self.test_results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'ERROR',
                    'reason': f'Server error ({response.status_code})'
                })
            elif response.status_code == 401:
                # Authentication required - this is expected
                self.test_results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'PASS',
                    'reason': 'Auth required (expected)'
                })
            else:
                self.test_results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'PASS',
                    'reason': f'Response: {response.status_code}'
                })

        except requests.exceptions.ConnectionError:
            self.test_results.append({
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'reason': 'Backend not running'
            })
        except Exception as e:
            self.test_results.append({
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'reason': str(e)
            })

    def report_results(self) -> bool:
        """Report test results"""
        print("\n" + "="*60)
        print("📊 CONTRACT TEST RESULTS")
        print("="*60)

        passed = [r for r in self.test_results if r['status'] == 'PASS']
        failed = [r for r in self.test_results if r['status'] == 'FAIL']
        errors = [r for r in self.test_results if r['status'] == 'ERROR']
        skipped = [r for r in self.test_results if r['status'] == 'SKIPPED']

        if failed:
            print(f"\n❌ FAILED ({len(failed)}):")
            for result in failed:
                print(f"  {result['method']} {result['endpoint']}: {result['reason']}")

        if errors:
            print(f"\n⚠️  ERRORS ({len(errors)}):")
            for result in errors:
                print(f"  {result['method']} {result['endpoint']}: {result['reason']}")

        print(f"\n✅ Passed: {len(passed)}")
        print(f"⏭️  Skipped: {len(skipped)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"⚠️  Errors: {len(errors)}")

        success_rate = len(passed) / max(1, len(passed) + len(failed))
        print(f"\n📈 Success Rate: {success_rate:.1%}")
        print("="*60)

        return len(failed) == 0 and len(errors) == 0


def main():
    """Main execution"""
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    tester = ContractTester(project_root)
    success = tester.run_contract_tests()

    exit(0 if success else 1)


if __name__ == "__main__":
    main()