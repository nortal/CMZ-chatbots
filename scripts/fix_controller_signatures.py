#!/usr/bin/env python3
"""
Automatically fix controller signatures after OpenAPI generation
This ensures body parameters are properly included in function signatures
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Set

class ControllerFixer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_path = project_root / "backend/api"
        self.fixes_applied = []

    def fix_all_controllers(self):
        """Fix all controller signatures based on OpenAPI spec"""
        print("🔧 Fixing controller signatures...")

        # Load OpenAPI spec
        spec = self.load_openapi_spec()
        if not spec:
            return False

        controllers_path = self.backend_path / "src/main/python/openapi_server/controllers"

        # Process each endpoint
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue

                operation_id = operation.get('operationId')
                if not operation_id:
                    continue

                # Find and fix controller
                self.fix_controller_function(operation_id, operation, controllers_path)

        # Report results
        self.report_fixes()
        return True

    def load_openapi_spec(self) -> Dict:
        """Load OpenAPI specification"""
        spec_path = self.backend_path / "openapi_spec.yaml"
        try:
            with open(spec_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load OpenAPI spec: {e}")
            return None

    def fix_controller_function(self, operation_id: str, operation: Dict, controllers_path: Path):
        """Fix a specific controller function signature"""
        # Find controller file
        controller_file = None
        for file_path in controllers_path.glob("*.py"):
            with open(file_path, 'r') as f:
                if f"def {operation_id}(" in f.read():
                    controller_file = file_path
                    break

        if not controller_file:
            return

        # Determine required parameters
        params = self.get_required_params(operation)

        # Fix the function signature
        self.update_function_signature(controller_file, operation_id, params)

    def get_required_params(self, operation: Dict) -> list:
        """Get list of required parameters for operation"""
        params = []

        # Path and query parameters
        for param in operation.get('parameters', []):
            param_name = param.get('name')
            if param_name:
                # Convert to Python-safe name
                safe_name = param_name.replace('-', '_')

                # Handle Python reserved keywords
                # Connexion automatically adds underscore to reserved keywords
                python_reserved = {
                    'id', 'type', 'class', 'def', 'return', 'if', 'else',
                    'elif', 'try', 'except', 'finally', 'for', 'while',
                    'break', 'continue', 'pass', 'import', 'from', 'as',
                    'global', 'nonlocal', 'lambda', 'with', 'yield', 'assert',
                    'del', 'in', 'is', 'not', 'or', 'and', 'None', 'True', 'False'
                }
                if safe_name in python_reserved:
                    safe_name = safe_name + '_'

                params.append(safe_name)

        # Request body parameter
        if 'requestBody' in operation:
            params.append('body')

        return params

    def update_function_signature(self, file_path: Path, operation_id: str, params: list):
        """Update function signature in controller file"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Find current function definition
        pattern = rf"(def {operation_id}\()([^)]*?)(\):)"
        match = re.search(pattern, content)

        if not match:
            return

        current_params = match.group(2).strip()
        expected_params = ', '.join(params) if params else ''

        # Only fix if different
        if current_params != expected_params:
            # Replace function signature
            new_signature = f"def {operation_id}({expected_params}):"
            old_signature = match.group(0)

            updated_content = content.replace(old_signature, new_signature)

            # Also fix the implementation call if needed
            if 'body' in params and 'body' not in current_params:
                # Fix implementation function call
                impl_pattern = rf"(impl_function\()([^)]*?)(\))"
                impl_match = re.search(impl_pattern, updated_content)
                if impl_match:
                    impl_params = ', '.join(params) if params else ''
                    new_impl_call = f"impl_function({impl_params})"
                    updated_content = re.sub(impl_pattern, new_impl_call, updated_content)

            # Write fixed content
            with open(file_path, 'w') as f:
                f.write(updated_content)

            self.fixes_applied.append({
                'file': file_path.name,
                'function': operation_id,
                'old_params': current_params or '(none)',
                'new_params': expected_params or '(none)'
            })

    def report_fixes(self):
        """Report applied fixes"""
        if self.fixes_applied:
            print(f"\n✅ Fixed {len(self.fixes_applied)} controller signatures:")
            for fix in self.fixes_applied:
                print(f"  📝 {fix['file']}: {fix['function']}")
                print(f"     Old: ({fix['old_params']})")
                print(f"     New: ({fix['new_params']})")
        else:
            print("\n✅ All controller signatures are correct!")


def main():
    """Main execution"""
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    fixer = ControllerFixer(project_root)
    fixer.fix_all_controllers()


if __name__ == "__main__":
    main()