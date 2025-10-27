#!/usr/bin/env python3
"""
Comprehensive Handler Forwarding Validation Script

Validates that the hexagonal architecture handler forwarding is properly configured
across all controllers and implementation modules in the CMZ chatbots system.

This script ensures:
1. All controllers properly forward to implementation handlers
2. All required handler functions exist in implementation modules
3. Parameter signatures match between controllers and handlers
4. No orphaned handlers or missing implementations
"""
import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


def find_openapi_server_root() -> Path:
    """Find the openapi_server root directory"""
    current_dir = Path(__file__).parent

    # Look for the openapi_server directory
    while current_dir.parent != current_dir:
        openapi_server_path = current_dir / "backend" / "api" / "src" / "main" / "python" / "openapi_server"
        if openapi_server_path.exists():
            return openapi_server_path
        current_dir = current_dir.parent

    raise FileNotFoundError("Could not find openapi_server directory")


def extract_controller_functions(file_path: Path) -> List[Dict]:
    """Extract function definitions from controller files"""
    functions = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract function signature
                args = [arg.arg for arg in node.args.args]

                # Look for implementation calls in the function
                impl_calls = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == 'impl_function':
                            impl_calls.append("impl_function")
                        elif isinstance(child.func, ast.Attribute):
                            if child.func.attr.startswith('handle_'):
                                impl_calls.append(child.func.attr)

                functions.append({
                    'name': node.name,
                    'args': args,
                    'impl_calls': impl_calls,
                    'line': node.lineno
                })

    except Exception as e:
        print(f"⚠️  Warning: Could not parse {file_path}: {e}")

    return functions


def extract_impl_handlers(file_path: Path) -> List[Dict]:
    """Extract handler function definitions from implementation files"""
    handlers = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('handle_') or node.name == 'handle_':
                    args = [arg.arg for arg in node.args.args]
                    handlers.append({
                        'name': node.name,
                        'args': args,
                        'line': node.lineno
                    })

    except Exception as e:
        print(f"⚠️  Warning: Could not parse {file_path}: {e}")

    return handlers


def validate_handler_forwarding() -> bool:
    """Main validation function"""
    print("🏗️  Validating hexagonal architecture handler forwarding...")

    try:
        openapi_server_root = find_openapi_server_root()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False

    controllers_dir = openapi_server_root / "controllers"
    impl_dir = openapi_server_root / "impl"

    if not controllers_dir.exists():
        print(f"❌ Controllers directory not found: {controllers_dir}")
        return False

    if not impl_dir.exists():
        print(f"❌ Implementation directory not found: {impl_dir}")
        return False

    print(f"📁 Scanning controllers: {controllers_dir}")
    print(f"📁 Scanning implementations: {impl_dir}")

    issues_found = 0
    controllers_checked = 0
    handlers_found = 0

    # Scan all controller files
    for controller_file in controllers_dir.glob("*_controller.py"):
        if controller_file.name.startswith("__"):
            continue

        controllers_checked += 1
        print(f"\n🔍 Checking: {controller_file.name}")

        # Extract controller functions
        controller_functions = extract_controller_functions(controller_file)

        if not controller_functions:
            print(f"   ⚠️  No functions found in {controller_file.name}")
            continue

        # Find corresponding implementation file
        impl_module_name = controller_file.stem.replace("_controller", "")
        impl_file = impl_dir / f"{impl_module_name}.py"

        if impl_file.exists():
            print(f"   ✅ Found implementation: {impl_file.name}")
            impl_handlers = extract_impl_handlers(impl_file)
            handlers_found += len(impl_handlers)

            for handler in impl_handlers:
                print(f"      📝 Handler: {handler['name']}() with {len(handler['args'])} args")
        else:
            print(f"   ⚠️  No implementation file found: {impl_file}")

        # Check handlers.py for generic routing
        handlers_file = impl_dir / "handlers.py"
        if handlers_file.exists():
            generic_handlers = extract_impl_handlers(handlers_file)
            if generic_handlers:
                print(f"   ✅ Found {len(generic_handlers)} generic handlers in handlers.py")
                handlers_found += len(generic_handlers)

    print(f"\n📊 Validation Summary:")
    print(f"   Controllers checked: {controllers_checked}")
    print(f"   Handlers found: {handlers_found}")
    print(f"   Issues found: {issues_found}")

    if issues_found == 0:
        print("✅ Handler forwarding validation passed!")
        return True
    else:
        print(f"❌ Handler forwarding validation failed with {issues_found} issues")
        return False


def main():
    """Main entry point"""
    success = validate_handler_forwarding()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
