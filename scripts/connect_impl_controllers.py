#!/usr/bin/env python3
"""
OpenAPI Controller-Implementation Connection Script

Automatically connects OpenAPI-generated controllers to business logic implementation modules.
Replaces 'do some magic!' placeholders with actual impl function calls.

Usage:
    python3 scripts/connect_impl_controllers.py [--dry-run] [--verbose]

Arguments:
    --dry-run    Show what would be changed without modifying files
    --verbose    Show detailed connection analysis and progress

Examples:
    # Preview changes
    python3 scripts/connect_impl_controllers.py --dry-run --verbose

    # Apply connections
    python3 scripts/connect_impl_controllers.py --verbose
"""

import os
import re
import sys
import ast
import argparse
import logging
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

# Define the mapping between controller modules and impl modules
CONTROLLER_IMPL_MAPPING = {
    'admin_controller.py': 'admin.py',
    'analytics_controller.py': 'analytics.py',
    'animals_controller.py': 'animals.py',
    'auth_controller.py': 'auth.py',
    'conversation_controller.py': 'conversation.py',  # Fixed naming
    'family_controller.py': 'family.py',  # Fixed naming
    'knowledge_controller.py': 'knowledge.py',
    'later_controller.py': 'later.py',
    'media_controller.py': 'media.py',
    'system_controller.py': 'system.py',
    'ui_controller.py': 'ui.py',
    'users_controller.py': 'users.py'
}

# Enhanced function mapping between controller and impl functions
FUNCTION_MAPPING = {
    # Animals controller mappings
    'animal_config_get': 'handle_get_animal_config',
    'animal_config_patch': 'handle_update_animal_config',
    'animal_details_get': 'handle_get_animal',
    'animal_id_delete': 'handle_delete_animal',
    'animal_id_get': 'handle_get_animal',
    'animal_id_put': 'handle_update_animal',
    'animal_list_get': 'handle_list_animals',
    'animal_post': 'handle_create_animal',

    # Auth controller mappings - mapped to existing auth.py functions
    'login_post': 'handle_login',
    'logout_post': 'handle_logout',
    'refresh_post': 'handle_refresh_token',
    'register_post': 'handle_register',

    # Family controller mappings
    'family_get': 'handle_get_family',
    'family_post': 'handle_create_family',
    'family_put': 'handle_update_family',

    # Admin controller mappings
    'admin_users_get': 'handle_list_users',
    'admin_system_health_get': 'handle_system_health',

    # Analytics controller mappings
    'analytics_conversations_get': 'handle_get_conversation_analytics',
    'analytics_usage_get': 'handle_get_usage_analytics',

    # Users controller mappings
    'users_get': 'handle_list_users',
}

class ControllerImplConnector:
    def __init__(self, base_path: str, dry_run: bool = False, verbose: bool = False):
        self.base_path = Path(base_path)
        self.controllers_dir = self.base_path / 'openapi_server' / 'controllers'
        self.impl_dir = self.base_path / 'openapi_server' / 'impl'
        self.dry_run = dry_run
        self.verbose = verbose
        self.replacements_made = 0
        self.files_modified = 0

    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}")

    def find_controller_functions(self, controller_file: Path) -> List[str]:
        """Extract function names from controller file that have 'do some magic!' placeholders"""
        functions_with_placeholders = []

        try:
            with open(controller_file, 'r') as f:
                content = f.read()

            # Find functions that return 'do some magic!'
            pattern = r'def\s+(\w+)\s*\([^)]*\):[^}]*?return\s+[\'"]do some magic![\'"]'
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                function_name = match.group(1)
                functions_with_placeholders.append(function_name)
                self.log(f"Found placeholder function: {function_name}")

        except Exception as e:
            print(f"Error reading controller file {controller_file}: {e}")

        return functions_with_placeholders

    def check_impl_function_exists(self, impl_file: Path, function_name: str) -> bool:
        """Check if function exists in impl file"""
        try:
            with open(impl_file, 'r') as f:
                content = f.read()

            # Look for function definition
            pattern = rf'def\s+{re.escape(function_name)}\s*\('
            return bool(re.search(pattern, content))

        except FileNotFoundError:
            self.log(f"Implementation file {impl_file} not found")
            return False
        except Exception as e:
            print(f"Error reading impl file {impl_file}: {e}")
            return False

    def generate_import_statement(self, impl_module: str) -> str:
        """Generate the import statement for impl module"""
        module_name = impl_module.replace('.py', '')
        return f"from openapi_server.impl import {module_name}"

    def generate_function_call(self, function_name: str, impl_module: str) -> str:
        """Generate the function call to impl module"""
        module_name = impl_module.replace('.py', '')
        return f"return {module_name}.{function_name}(*args, **kwargs)"

    def replace_placeholder_in_function(self, content: str, function_name: str, impl_module: str, impl_function_name: str) -> str:
        """Replace 'do some magic!' placeholder in specific function with impl call"""
        module_name = impl_module.replace('.py', '')

        # Pattern to match the function and its return statement - avoid f-string escaping issues
        escaped_func_name = re.escape(function_name)
        pattern = r'(def\s+' + escaped_func_name + r'\s*\([^)]*\):[^}]*?)return\s+[\'"]do some magic![\'"]'

        def replacement(match):
            function_def = match.group(1)
            # Extract parameters from function definition
            param_pattern = r'def\s+' + escaped_func_name + r'\s*\(([^)]*)\)'
            param_match = re.search(param_pattern, function_def)
            if param_match:
                params = param_match.group(1).strip()
                if params:
                    # Create parameter list for function call
                    param_names = [p.split('=')[0].strip() for p in params.split(',') if p.strip()]
                    param_list = ', '.join(param_names)
                    return function_def + f"return {module_name}.{impl_function_name}({param_list})"
                else:
                    return function_def + f"return {module_name}.{impl_function_name}()"
            else:
                # Fallback to args/kwargs if we can't parse parameters
                return function_def + f"return {module_name}.{impl_function_name}(*args, **kwargs)"

        return re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    def add_import_if_missing(self, content: str, impl_module: str) -> str:
        """Add import statement for impl module if not already present"""
        module_name = impl_module.replace('.py', '')
        import_statement = f"from openapi_server.impl import {module_name}"

        # Check if import already exists
        if import_statement in content:
            self.log(f"Import for {module_name} already exists")
            return content

        # Find the last import statement and add our import after it
        import_pattern = r'(from openapi_server\.models\.[^)]+import[^\n]+\n)'
        matches = list(re.finditer(import_pattern, content))

        if matches:
            last_import = matches[-1]
            insertion_point = last_import.end()
            new_content = (content[:insertion_point] +
                          f"{import_statement}  # noqa: E501\n" +
                          content[insertion_point:])
            self.log(f"Added import statement for {module_name}")
            return new_content
        else:
            # If no model imports found, add after other imports
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_index = i + 1
                elif line.strip() == '':
                    continue
                else:
                    break

            lines.insert(insert_index, f"{import_statement}  # noqa: E501")
            self.log(f"Added import statement for {module_name} at line {insert_index}")
            return '\n'.join(lines)

    def process_controller_file(self, controller_file: Path) -> bool:
        """Process a single controller file and replace placeholders"""
        controller_name = controller_file.name

        if controller_name not in CONTROLLER_IMPL_MAPPING:
            self.log(f"No impl mapping found for {controller_name}")
            return False

        impl_module = CONTROLLER_IMPL_MAPPING[controller_name]
        impl_file = self.impl_dir / impl_module

        self.log(f"Processing {controller_name} -> {impl_module}")

        # Find functions with placeholders
        placeholder_functions = self.find_controller_functions(controller_file)

        if not placeholder_functions:
            self.log(f"No placeholder functions found in {controller_name}")
            return False

        # Read controller content
        try:
            with open(controller_file, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading controller file {controller_file}: {e}")
            return False

        original_content = content
        modified = False

        # Process each function
        for function_name in placeholder_functions:
            # Check if we have a mapping for this controller function
            impl_function_name = FUNCTION_MAPPING.get(function_name)

            if not impl_function_name:
                # Fallback: assume same name if no mapping
                impl_function_name = function_name

            # Check if impl function exists
            if not self.check_impl_function_exists(impl_file, impl_function_name):
                self.log(f"Function {impl_function_name} not found in {impl_module}, skipping {function_name}")
                continue

            self.log(f"Replacing placeholder in {function_name} → {impl_function_name}")

            # Replace the placeholder
            new_content = self.replace_placeholder_in_function(content, function_name, impl_module, impl_function_name)

            if new_content != content:
                content = new_content
                modified = True
                self.replacements_made += 1

        if modified:
            # Add import statement
            content = self.add_import_if_missing(content, impl_module)

            # Write the modified content
            if not self.dry_run:
                try:
                    with open(controller_file, 'w') as f:
                        f.write(content)
                    self.log(f"Modified {controller_file}")
                except Exception as e:
                    print(f"Error writing controller file {controller_file}: {e}")
                    return False
            else:
                self.log(f"[DRY RUN] Would modify {controller_file}")

            self.files_modified += 1
            return True

        return False

    def process_all_controllers(self) -> Dict[str, bool]:
        """Process all controller files"""
        results = {}

        if not self.controllers_dir.exists():
            print(f"Error: Controllers directory not found at {self.controllers_dir}")
            return results

        if not self.impl_dir.exists():
            print(f"Error: Implementation directory not found at {self.impl_dir}")
            return results

        self.log(f"Processing controllers in {self.controllers_dir}")
        self.log(f"Using implementations from {self.impl_dir}")

        # Process each controller file
        for controller_file in self.controllers_dir.glob('*_controller.py'):
            if controller_file.name.startswith('__'):
                continue

            try:
                success = self.process_controller_file(controller_file)
                results[controller_file.name] = success
            except Exception as e:
                print(f"Error processing {controller_file}: {e}")
                results[controller_file.name] = False

        return results

    def print_summary(self, results: Dict[str, bool]):
        """Print summary of processing results"""
        print("\n" + "=" * 60)
        print("CONTROLLER-IMPL CONNECTION SUMMARY")
        print("=" * 60)

        if self.dry_run:
            print("DRY RUN MODE - No files were actually modified")

        print(f"Files processed: {len(results)}")
        print(f"Files modified: {self.files_modified}")
        print(f"Function replacements made: {self.replacements_made}")

        if results:
            print("\nFile-by-file results:")
            for filename, success in results.items():
                status = "✅ MODIFIED" if success else "⏭️  SKIPPED"
                print(f"  {status}: {filename}")

        print("\n" + "=" * 60)

        if self.replacements_made > 0:
            print("🎉 SUCCESS: Controller-impl connections established!")
            print("Run integration tests to verify the connections work properly.")
        elif not self.dry_run:
            print("ℹ️  No modifications needed - controllers may already be connected.")
        else:
            print("ℹ️  DRY RUN complete - use --verbose to see what would be changed.")


def main():
    parser = argparse.ArgumentParser(description="Connect OpenAPI controllers to impl modules")
    parser.add_argument('--base-path', default='backend/api/src/main/python',
                       help='Base path to Python source code')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    # Create connector and process files
    connector = ControllerImplConnector(args.base_path, args.dry_run, args.verbose)
    results = connector.process_all_controllers()
    connector.print_summary(results)

    # Exit with appropriate code
    if connector.replacements_made > 0 or (args.dry_run and connector.files_modified > 0):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # No changes needed or errors occurred


if __name__ == "__main__":
    main()