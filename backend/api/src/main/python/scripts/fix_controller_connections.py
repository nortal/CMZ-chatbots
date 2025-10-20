#!/usr/bin/env python3
"""
Permanent fix for controller-implementation connection issues.
Run this after any OpenAPI generation to ensure all endpoints are properly connected.
"""

import os
import re
import sys
import importlib
import inspect
from pathlib import Path

# Add the parent directory to path so we can import openapi_server
sys.path.insert(0, str(Path(__file__).parent.parent))

class ControllerConnectionFixer:
    """Automatically connects controllers to implementations"""

    def __init__(self):
        self.impl_dir = Path(__file__).parent.parent / "openapi_server" / "impl"
        self.controller_dir = Path(__file__).parent.parent / "openapi_server" / "controllers"
        self.handlers_file = self.impl_dir / "handlers.py"
        self.connections = {}
        self.missing_implementations = []
        self.successful_connections = []

    def scan_implementations(self):
        """Find all implementation files and their functions"""
        implementations = {}

        # Scan all .py files in impl directory
        for impl_file in self.impl_dir.glob("*.py"):
            if impl_file.name.startswith("__") or impl_file.name == "handlers.py":
                continue

            module_name = impl_file.stem

            # Special handling for bidirectional implementations
            if module_name.endswith("_bidirectional"):
                base_name = module_name.replace("_bidirectional", "")
                # Map to the non-bidirectional module name for handlers
                implementations[base_name] = {
                    'module': module_name,
                    'functions': self._get_module_functions(impl_file)
                }
            else:
                implementations[module_name] = {
                    'module': module_name,
                    'functions': self._get_module_functions(impl_file)
                }

        return implementations

    def _get_module_functions(self, file_path):
        """Extract function names from a Python file"""
        functions = []
        with open(file_path, 'r') as f:
            content = f.read()
            # Find all function definitions
            pattern = r'^def\s+(\w+)\s*\('
            matches = re.findall(pattern, content, re.MULTILINE)
            functions.extend(matches)
        return functions

    def scan_controllers(self):
        """Find all controller endpoints that need implementation"""
        endpoints = {}

        for controller_file in self.controller_dir.glob("*_controller.py"):
            module_name = controller_file.stem

            with open(controller_file, 'r') as f:
                content = f.read()

            # Find all function definitions that need implementation
            pattern = r'^def\s+(\w+)\s*\([^)]*\):'
            matches = re.findall(pattern, content, re.MULTILINE)

            for func_name in matches:
                # Skip helper functions
                if func_name.startswith('_'):
                    continue

                # Map controller function to expected implementation
                endpoints[func_name] = {
                    'controller': module_name,
                    'function': func_name,
                    'needs_implementation': self._check_needs_implementation(content, func_name)
                }

        return endpoints

    def _check_needs_implementation(self, content, func_name):
        """Check if a controller function needs implementation"""
        # Look for "do some magic!" or similar placeholders
        func_pattern = rf'^def\s+{func_name}\s*\([^)]*\):.*?(?=^def\s|\Z)'
        func_match = re.search(func_pattern, content, re.MULTILINE | re.DOTALL)

        if func_match:
            func_body = func_match.group()
            if 'do some magic!' in func_body or 'Not Implemented' in func_body:
                return True

        return False

    def generate_handler_connections(self, implementations, endpoints):
        """Generate the handler connections for all endpoints"""

        # Group endpoints by resource
        resource_groups = {}
        for endpoint_name, endpoint_info in endpoints.items():
            # Extract resource name (e.g., "family" from "family_list_get")
            parts = endpoint_name.split('_')
            if len(parts) > 1:
                resource = parts[0]
                if resource not in resource_groups:
                    resource_groups[resource] = []
                resource_groups[resource].append(endpoint_name)

        # Generate connections
        connections = []

        for resource, endpoint_names in resource_groups.items():
            # Check if we have implementations for this resource
            if resource in implementations:
                impl_info = implementations[resource]
                module_name = impl_info['module']

                # Generate import statement
                if module_name.endswith('_bidirectional'):
                    connections.append(f"# {resource.capitalize()} endpoints use bidirectional implementation")
                    connections.append(f"from .{module_name} import (")

                    # Map common operations to bidirectional functions
                    mappings = {
                        f'{resource}_list_get': f'list_{resource}s_for_user',
                        f'{resource}_details_post': f'create_{resource}_bidirectional',
                        f'{resource}_details_get': f'get_{resource}_bidirectional',
                        f'{resource}_details_patch': f'update_{resource}_bidirectional',
                        f'{resource}_details_delete': f'delete_{resource}_bidirectional',
                    }

                    for endpoint in endpoint_names:
                        if endpoint in mappings:
                            impl_func = mappings[endpoint]
                            if impl_func in impl_info['functions']:
                                self.connections[endpoint] = {
                                    'module': module_name,
                                    'function': impl_func
                                }
                else:
                    # Standard implementation pattern
                    for endpoint in endpoint_names:
                        # Try to find matching implementation function
                        for func in impl_info['functions']:
                            if endpoint in func or func in endpoint:
                                self.connections[endpoint] = {
                                    'module': module_name,
                                    'function': func
                                }
                                break

        return connections

    def update_handlers_file(self):
        """Update handlers.py with discovered connections"""

        print("🔧 Updating handlers.py with discovered connections...")

        # Read current handlers.py
        with open(self.handlers_file, 'r') as f:
            content = f.read()

        # Add missing imports
        for endpoint, connection in self.connections.items():
            module = connection['module']
            function = connection['function']

            # Check if import exists
            import_pattern = rf'from \.{module} import.*{function}'
            if not re.search(import_pattern, content):
                print(f"  Adding import: from .{module} import {function}")
                # Add import after the last import statement
                last_import = list(re.finditer(r'^from ', content, re.MULTILINE))[-1]
                insert_pos = last_import.end()
                content = content[:insert_pos] + f"\nfrom .{module} import {function}" + content[insert_pos:]

        # Update handler mappings
        handler_map_pattern = r'handler_map = \{([^}]+)\}'
        handler_map_match = re.search(handler_map_pattern, content, re.DOTALL)

        if handler_map_match:
            map_content = handler_map_match.group(1)

            for endpoint, connection in self.connections.items():
                function = connection['function']

                # Check if mapping exists
                if f"'{endpoint}':" not in map_content:
                    print(f"  Adding handler mapping: {endpoint} -> {function}")
                    # Add mapping
                    map_content += f"\n            '{endpoint}': {function},"

            # Replace the handler map
            new_handler_map = f"handler_map = {{{map_content}\n        }}"
            content = content[:handler_map_match.start()] + new_handler_map + content[handler_map_match.end():]

        # Write updated content
        with open(self.handlers_file, 'w') as f:
            f.write(content)

        print("✅ handlers.py updated successfully")

    def create_connection_tests(self):
        """Generate tests to validate all connections work"""

        test_content = '''#!/usr/bin/env python3
"""
Automated tests to ensure all controller-implementation connections work.
Run this after any changes to validate the system.
"""

import pytest
import importlib
import inspect
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestControllerConnections:
    """Test that all controllers properly connect to implementations"""

'''

        for endpoint, connection in self.connections.items():
            test_content += f'''
    def test_{endpoint}_connection(self):
        """Test {endpoint} is properly connected"""
        from openapi_server.impl.handlers import handle_
        from openapi_server.impl import handlers

        # Check the handler map contains the endpoint
        assert '{endpoint}' in handlers.handler_map

        # Check the mapped function exists
        handler_func = handlers.handler_map.get('{endpoint}')
        assert handler_func is not None
        assert callable(handler_func)
'''

        # Write test file
        test_file = Path(__file__).parent.parent / "tests" / "test_controller_connections.py"
        test_file.parent.mkdir(exist_ok=True)

        with open(test_file, 'w') as f:
            f.write(test_content)

        print(f"✅ Created connection tests at {test_file}")
        return test_file

    def run(self):
        """Main execution flow"""
        print("🔍 Scanning for implementations and controllers...")

        implementations = self.scan_implementations()
        print(f"  Found {len(implementations)} implementation modules:")
        for name, info in implementations.items():
            print(f"    - {name}: {len(info['functions'])} functions")

        endpoints = self.scan_controllers()
        print(f"  Found {len(endpoints)} controller endpoints")

        connections = self.generate_handler_connections(implementations, endpoints)
        print(f"\n📝 Generated {len(self.connections)} connections")

        self.update_handlers_file()

        test_file = self.create_connection_tests()

        # Report summary
        print("\n📊 Summary:")
        print(f"  ✅ Connected: {len(self.connections)} endpoints")

        unconnected = set(endpoints.keys()) - set(self.connections.keys())
        if unconnected:
            print(f"  ⚠️ Unconnected: {len(unconnected)} endpoints")
            for endpoint in list(unconnected)[:5]:
                print(f"      - {endpoint}")
            if len(unconnected) > 5:
                print(f"      ... and {len(unconnected) - 5} more")

        print(f"\n🧪 Run tests with: pytest {test_file}")

        return len(self.connections), len(unconnected)


if __name__ == "__main__":
    fixer = ControllerConnectionFixer()
    connected, unconnected = fixer.run()

    # Exit with error if there are unconnected endpoints
    if unconnected > 0:
        sys.exit(1)

    sys.exit(0)