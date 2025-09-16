#!/usr/bin/env python3
"""
Post-Generation Validation Script for CMZ API
Ensures generated controllers properly connect to implementations
and validates frontend-backend contract consistency
"""

import os
import re
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class APIValidation:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_path = project_root / "backend/api"
        self.frontend_path = project_root / "frontend"
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("🔍 Starting comprehensive API validation...")

        # Load OpenAPI spec
        spec = self.load_openapi_spec()
        if not spec:
            return False

        # Validate controller generation
        self.validate_controllers(spec)

        # Validate implementation connections
        self.validate_impl_connections(spec)

        # Validate frontend-backend contract
        self.validate_frontend_contract(spec)

        # Check for common issues
        self.check_common_issues()

        # Report results
        return self.report_results()

    def load_openapi_spec(self) -> Dict:
        """Load and parse OpenAPI specification"""
        spec_path = self.backend_path / "openapi_spec.yaml"
        try:
            with open(spec_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load OpenAPI spec: {e}")
            return None

    def validate_controllers(self, spec: Dict):
        """Ensure controllers have proper signatures for request bodies"""
        print("📝 Validating controller signatures...")

        # Check both generated and source paths
        generated_path = self.backend_path / "generated/app/openapi_server/controllers"
        source_path = self.backend_path / "src/main/python/openapi_server/controllers"

        # Validate that at least one controllers path exists
        if not source_path.exists() and not generated_path.exists():
            self.errors.append(
                f"Neither source controllers path ({source_path}) nor generated controllers path ({generated_path}) exists."
            )
            return

        # Use source if it exists, otherwise use generated
        controllers_path = source_path if source_path.exists() else generated_path

        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue

                operation_id = operation.get('operationId')
                if not operation_id:
                    continue

                # Check if operation has request body
                has_body = 'requestBody' in operation

                # Find corresponding controller
                controller_file = self.find_controller_file(operation_id, controllers_path)
                if not controller_file:
                    self.errors.append(f"Controller not found for {operation_id}")
                    continue

                # Validate function signature
                self.validate_function_signature(controller_file, operation_id, has_body, operation)

    def find_controller_file(self, operation_id: str, controllers_path: Path) -> Path:
        """Find controller file containing operation"""
        # Convert camelCase to snake_case for function names
        snake_case_id = self.to_snake_case(operation_id)

        for controller_file in controllers_path.glob("*.py"):
            with open(controller_file, 'r') as f:
                content = f.read()
                # Try both original and snake_case versions
                if f"def {operation_id}(" in content or f"def {snake_case_id}(" in content:
                    return controller_file
        return None

    def validate_function_signature(self, file_path: Path, operation_id: str, has_body: bool, operation: Dict):
        """Validate that function has correct parameters"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Convert to snake_case for function name
        snake_case_id = self.to_snake_case(operation_id)

        # Find function definition (try both versions)
        pattern = rf"def ({operation_id}|{snake_case_id})\((.*?)\):"
        match = re.search(pattern, content)

        if not match:
            self.errors.append(f"Function {operation_id} not found in {file_path.name}")
            return

        params = match.group(2).strip()  # group(2) is the parameters part

        # Check for body parameter
        if has_body:
            if 'body' not in params and params == '':
                self.errors.append(f"❌ {operation_id}: Missing body parameter (has requestBody in spec)")

                # Auto-fix suggestion
                self.warnings.append(f"  Fix: Add 'body' parameter to {operation_id}")

        # Check for path parameters
        path_params = operation.get('parameters', [])
        for param in path_params:
            if param.get('in') == 'path':
                param_name = param.get('name')
                if param_name:
                    # Convert to Python-safe name (same logic as Connexion)
                    safe_name = param_name.replace('-', '_')

                    # Handle Python reserved keywords
                    python_reserved = {
                        'id', 'type', 'class', 'def', 'return', 'if', 'else',
                        'elif', 'try', 'except', 'finally', 'for', 'while',
                        'break', 'continue', 'pass', 'import', 'from', 'as',
                        'global', 'nonlocal', 'lambda', 'with', 'yield', 'assert',
                        'del', 'in', 'is', 'not', 'or', 'and', 'None', 'True', 'False'
                    }
                    if safe_name in python_reserved:
                        safe_name = safe_name + '_'

                    if safe_name not in params:
                        self.errors.append(f"❌ {operation_id}: Missing path parameter '{safe_name}' (from '{param_name}')")

    def validate_impl_connections(self, spec: Dict):
        """Ensure implementations exist for all controllers"""
        print("🔗 Validating implementation connections...")

        impl_path = self.backend_path / "src/main/python/openapi_server/impl"

        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue

                operation_id = operation.get('operationId')
                if not operation_id:
                    continue

                # Check if implementation exists
                impl_found = self.check_implementation_exists(operation_id, impl_path)
                if not impl_found:
                    self.warnings.append(f"⚠️  No implementation found for {operation_id}")

    def check_implementation_exists(self, operation_id: str, impl_path: Path) -> bool:
        """Check if implementation function exists"""
        # Common patterns for implementation functions
        patterns = [
            f"def handle_{operation_id}",
            f"def {operation_id}",
            f"handle_{self.to_snake_case(operation_id)}"
        ]

        for impl_file in impl_path.glob("*.py"):
            if impl_file.name == "__init__.py":
                continue

            with open(impl_file, 'r') as f:
                content = f.read()
                for pattern in patterns:
                    if pattern in content:
                        return True

        # Check generic handlers
        handlers_file = impl_path / "handlers.py"
        if handlers_file.exists():
            with open(handlers_file, 'r') as f:
                if "handle_" in f.read():
                    return True

        return False

    def validate_frontend_contract(self, spec: Dict):
        """Validate frontend API calls match backend endpoints"""
        print("🔄 Validating frontend-backend contract...")

        api_service = self.frontend_path / "src/services/api.ts"
        if not api_service.exists():
            self.warnings.append("Frontend API service not found")
            return

        with open(api_service, 'r') as f:
            frontend_code = f.read()

        # Extract API endpoints from frontend
        endpoint_pattern = r"['\"`](/[a-zA-Z_/]+)['\"`]"
        frontend_endpoints = set(re.findall(endpoint_pattern, frontend_code))

        # Get backend endpoints from spec
        backend_endpoints = set(spec.get('paths', {}).keys())

        # Find mismatches
        frontend_only = frontend_endpoints - backend_endpoints
        backend_only = backend_endpoints - frontend_endpoints

        if frontend_only:
            self.errors.append(f"❌ Frontend calls non-existent endpoints: {frontend_only}")

        if len(backend_only) > 10:  # Only warn if many endpoints unused
            self.warnings.append(f"⚠️  {len(backend_only)} backend endpoints not used by frontend")

    def check_common_issues(self):
        """Check for known common issues"""
        print("🔧 Checking for common issues...")

        # Check for "do some magic!" placeholder
        controllers_path = self.backend_path / "src/main/python/openapi_server/controllers"
        for controller_file in controllers_path.glob("*.py"):
            with open(controller_file, 'r') as f:
                if "do some magic!" in f.read():
                    self.errors.append(f"❌ Placeholder 'do some magic!' found in {controller_file.name}")

        # Check for broken imports
        impl_path = self.backend_path / "src/main/python/openapi_server/impl"
        for impl_file in impl_path.glob("*.py"):
            with open(impl_file, 'r') as f:
                content = f.read()
                if "from openapi_server.controllers" in content:
                    self.warnings.append(f"⚠️  Suspicious import in {impl_file.name} (controllers importing from impl)")

    def report_results(self) -> bool:
        """Report validation results"""
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS")
        print("="*60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")

        print("\n" + "="*60)

        return len(self.errors) == 0

    def to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def main():
    """Main execution"""
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Run validation
    validator = APIValidation(project_root)
    success = validator.validate_all()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()