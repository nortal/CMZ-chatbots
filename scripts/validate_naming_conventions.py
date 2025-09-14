#!/usr/bin/env python3
"""
Pre-build validation script for naming conventions
Ensures consistency between OpenAPI spec, generated code, and implementation
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple

class NamingConventionValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.openapi_spec_path = self.project_root / "backend/api/openapi_spec.yaml"
        self.impl_dir = self.project_root / "backend/api/src/main/python/openapi_server/impl"
        self.models_dir = self.project_root / "backend/api/src/main/python/openapi_server/models"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase"""
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    def extract_parameters_from_spec(self) -> Dict[str, Set[str]]:
        """Extract all parameter names from OpenAPI spec"""
        if not self.openapi_spec_path.exists():
            self.errors.append(f"OpenAPI spec not found: {self.openapi_spec_path}")
            return {}

        try:
            with open(self.openapi_spec_path, 'r') as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse OpenAPI spec: {e}")
            return {}

        parameters = {
            'path_params': set(),
            'query_params': set(),
            'body_properties': set(),
            'response_properties': set()
        }

        # Extract from paths
        for path, path_obj in spec.get('paths', {}).items():
            for method, method_obj in path_obj.items():
                if method.startswith('x-'):
                    continue

                # Path parameters
                for param in method_obj.get('parameters', []):
                    if param.get('in') == 'path':
                        parameters['path_params'].add(param['name'])
                    elif param.get('in') == 'query':
                        parameters['query_params'].add(param['name'])

                # Request body properties
                request_body = method_obj.get('requestBody', {})
                if 'content' in request_body:
                    for content_type, content in request_body['content'].items():
                        schema = content.get('schema', {})
                        properties = schema.get('properties', {})
                        parameters['body_properties'].update(properties.keys())

                # Response properties
                for response_code, response in method_obj.get('responses', {}).items():
                    if 'content' in response:
                        for content_type, content in response['content'].items():
                            schema = content.get('schema', {})
                            properties = schema.get('properties', {})
                            parameters['response_properties'].update(properties.keys())

        # Extract from components/schemas
        for schema_name, schema in spec.get('components', {}).get('schemas', {}).items():
            if 'properties' in schema:
                parameters['body_properties'].update(schema['properties'].keys())
                parameters['response_properties'].update(schema['properties'].keys())

        return parameters

    def check_python_files(self, parameters: Dict[str, Set[str]]) -> None:
        """Check Python implementation files for naming consistency"""
        all_params = set()
        for param_set in parameters.values():
            all_params.update(param_set)

        for py_file in self.impl_dir.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                # Look for camelCase parameters that should be snake_case
                for param in all_params:
                    if param in content:
                        snake_param = self.camel_to_snake(param)
                        if snake_param != param:
                            self.warnings.append(
                                f"{py_file.relative_to(self.project_root)}: "
                                f"Found camelCase '{param}', expected snake_case '{snake_param}'"
                            )

                    # Also check for snake_case version
                    snake_param = self.camel_to_snake(param)
                    if snake_param in content and snake_param != param:
                        # This is expected - log as info
                        pass

            except Exception as e:
                self.errors.append(f"Failed to read {py_file}: {e}")

    def check_database_consistency(self) -> None:
        """Check that database field names are consistent with API"""
        # Look for DynamoDB table definitions and queries
        for py_file in self.impl_dir.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                # Check for mixed naming in database operations
                if 'animal_id' in content and 'animalId' in content:
                    self.errors.append(
                        f"{py_file.relative_to(self.project_root)}: "
                        f"Mixed naming conventions found - both 'animal_id' and 'animalId'"
                    )

                # Check for DynamoDB queries using camelCase
                dynamodb_patterns = [
                    r"get_item.*animalId",
                    r"query.*animalId",
                    r"scan.*animalId",
                    r"put_item.*animalId"
                ]

                for pattern in dynamodb_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        self.warnings.append(
                            f"{py_file.relative_to(self.project_root)}: "
                            f"DynamoDB operation using camelCase: {matches}"
                        )

            except Exception as e:
                self.errors.append(f"Failed to read {py_file}: {e}")

    def generate_conversion_map(self, parameters: Dict[str, Set[str]]) -> Dict[str, str]:
        """Generate mapping from camelCase to snake_case for all parameters"""
        conversion_map = {}

        all_params = set()
        for param_set in parameters.values():
            all_params.update(param_set)

        for param in all_params:
            snake_param = self.camel_to_snake(param)
            if snake_param != param:
                conversion_map[param] = snake_param

        return conversion_map

    def create_fix_script(self, conversion_map: Dict[str, str]) -> None:
        """Create a script to fix naming inconsistencies"""
        script_path = self.project_root / "scripts" / "fix_naming_conventions.py"

        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated script to fix naming convention inconsistencies
Generated by validate_naming_conventions.py
"""

import os
import re
from pathlib import Path

# Conversion map from camelCase to snake_case
CONVERSION_MAP = {conversion_map!r}

def fix_file(file_path: Path) -> bool:
    """Fix naming conventions in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Apply conversions using safe string replacements
        for camel_case, snake_case in CONVERSION_MAP.items():
            # Simple string replacements in specific contexts
            # Dictionary keys
            content = content.replace(f'"{camel_case}"', f'"{snake_case}"')
            content = content.replace(f"'{camel_case}'", f"'{snake_case}'")

            # Parameter assignments - use safer replacement approach
            param_pattern = f'{camel_case}='
            param_replacement = f'{snake_case}='
            content = content.replace(param_pattern, param_replacement)

            # DynamoDB operations - use simple string replacement
            for op in ['get_item', 'put_item', 'query', 'scan']:
                # Replace within operation context using string replacement
                old_pattern = f'{op}({camel_case}'
                new_pattern = f'{op}({snake_case}'
                content = content.replace(old_pattern, new_pattern)

        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    impl_dir = project_root / "backend/api/src/main/python/openapi_server/impl"

    fixed_count = 0
    for py_file in impl_dir.rglob("*.py"):
        if fix_file(py_file):
            fixed_count += 1

    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        os.chmod(script_path, 0o644)
        print(f"Created fix script: {script_path}")

    def validate(self) -> bool:
        """Run all validation checks"""
        print("🔍 Validating naming conventions...")

        # Extract parameters from OpenAPI spec
        parameters = self.extract_parameters_from_spec()
        if not parameters:
            return False

        print(f"Found {sum(len(s) for s in parameters.values())} parameters in OpenAPI spec")

        # Check Python implementation files
        self.check_python_files(parameters)

        # Check database consistency
        self.check_database_consistency()

        # Generate conversion map and fix script
        conversion_map = self.generate_conversion_map(parameters)
        if conversion_map:
            self.create_fix_script(conversion_map)
            print(f"Generated conversion map with {len(conversion_map)} mappings")

        # Report results
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("✅ All naming conventions are consistent!")
            return True
        elif not self.errors:
            print("⚠️  Found warnings but no errors")
            return True
        else:
            print("❌ Found critical errors")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_naming_conventions.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    validator = NamingConventionValidator(project_root)
    success = validator.validate()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()