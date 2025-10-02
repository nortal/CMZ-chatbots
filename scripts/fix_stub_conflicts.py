#!/usr/bin/env python3
"""
Fix stub implementation conflicts in OpenAPI-generated code.

This script ensures that stub implementations don't override real implementations
by detecting and resolving conflicts between stub files and the main handlers.py.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

def find_impl_directory() -> Path:
    """Find the implementation directory."""
    base_paths = [
        Path.cwd() / "backend/api/src/main/python/openapi_server/impl",
        Path.cwd() / "src/main/python/openapi_server/impl",
        Path("/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/openapi_server/impl")
    ]

    for path in base_paths:
        if path.exists():
            return path

    raise FileNotFoundError("Could not find impl directory")

def find_stub_functions(file_path: Path) -> List[str]:
    """Find functions that just return not_implemented."""
    stub_functions = []

    if not file_path.exists():
        return stub_functions

    content = file_path.read_text()

    # Find functions that return not_implemented_error
    pattern = r'def\s+(handle_\w+)\([^)]*\)[^:]*:\s*(?:.*?\n)*?\s*return\s+not_implemented_error'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        func_name = match.group(1)
        stub_functions.append(func_name)

    return stub_functions

def find_real_implementations(handlers_path: Path) -> Set[str]:
    """Find real implementations in handlers.py."""
    real_implementations = set()

    if not handlers_path.exists():
        return real_implementations

    content = handlers_path.read_text()

    # Find all handler functions that don't just return not_implemented
    pattern = r'def\s+(handle_\w+)\([^)]*\)[^:]*:'
    matches = re.finditer(pattern, content)

    for match in matches:
        func_name = match.group(1)
        # Check if this function has real implementation (not just returning not_implemented)
        func_start = match.end()
        # Look for the next function or end of file
        next_func = re.search(r'\ndef\s+\w+\(', content[func_start:])
        func_end = func_start + next_func.start() if next_func else len(content)
        func_body = content[func_start:func_end]

        if 'not_implemented_error' not in func_body and 'not_implemented' not in func_body:
            real_implementations.add(func_name)

    return real_implementations

def rename_stub_file(file_path: Path) -> Path:
    """Rename stub file to prevent it from being imported."""
    if not file_path.exists():
        return file_path

    new_path = file_path.with_suffix('.py.stub')
    file_path.rename(new_path)
    print(f"  Renamed {file_path.name} to {new_path.name}")
    return new_path

def create_redirect_file(file_path: Path, real_functions: List[str]) -> None:
    """Create a file that redirects to real implementations in handlers.py."""
    redirect_content = '''"""
Auto-generated redirect module to prevent stub conflicts.
This file redirects to real implementations in handlers.py.
"""

from typing import Any, Tuple

# Import real implementations from handlers
from . import handlers

'''

    for func_name in real_functions:
        redirect_content += f'''
def {func_name}(*args, **kwargs) -> Tuple[Any, int]:
    """Redirect to real implementation in handlers.py"""
    return handlers.{func_name}(*args, **kwargs)
'''

    # Add any other functions that might be needed
    redirect_content += '''

# Default handler for operations not yet implemented
def not_implemented_error(operation: str) -> Tuple[dict, int]:
    """Return not implemented error for operations without implementation."""
    from openapi_server.models.error import Error
    error = Error(
        code="not_implemented",
        message=f"Operation {operation} not yet implemented",
        details={"module": __name__, "operation": operation}
    )
    return error.to_dict(), 501
'''

    file_path.write_text(redirect_content)
    print(f"  Created redirect file: {file_path.name}")

def fix_controller_import_order(controllers_dir: Path) -> None:
    """Fix controller import order to prefer handlers.py over module files."""
    if not controllers_dir.exists():
        return

    for controller_file in controllers_dir.glob("*_controller.py"):
        if controller_file.name == "__init__.py":
            continue

        content = controller_file.read_text()

        # Fix the import pattern to check handlers.py first
        old_pattern = r'''try:
            # Pattern 1: Direct module import
            impl_module = __import__\(f"openapi_server\.impl\.\{impl_module_name\}", fromlist=\[impl_function_name\]\)
            impl_function = getattr\(impl_module, impl_function_name\)
        except \(ImportError, AttributeError\):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server\.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers\.handle_'''

        new_pattern = '''try:
            # Pattern 1: Check handlers.py first (real implementations)
            from openapi_server.impl import handlers
            # Try to get the specific handler function
            impl_function = getattr(handlers, impl_function_name, None)
            if not impl_function:
                # Fall back to generic handle_ function that routes based on caller name
                impl_function = handlers.handle_
        except (ImportError, AttributeError):
            # Pattern 2: Try module-specific import as fallback
            try:
                impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
                impl_function = getattr(impl_module, impl_function_name)
            except (ImportError, AttributeError):
                impl_function = None'''

        if old_pattern.replace('\\', '') in content:
            content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)
            controller_file.write_text(content)
            print(f"  Fixed import order in {controller_file.name}")

def main():
    """Main function to fix stub conflicts."""
    print("🔧 Fixing stub implementation conflicts...")

    try:
        impl_dir = find_impl_directory()
        print(f"Found impl directory: {impl_dir}")

        handlers_path = impl_dir / "handlers.py"

        # Find all real implementations in handlers.py
        real_implementations = find_real_implementations(handlers_path)
        print(f"Found {len(real_implementations)} real implementations in handlers.py")

        # Check each module file for stub conflicts
        conflicts_found = False
        for module_file in impl_dir.glob("*.py"):
            if module_file.name in ["__init__.py", "handlers.py", "error_handler.py", "dependency_injection.py"]:
                continue

            if module_file.name.startswith("utils"):
                continue

            # Check for stub functions
            stub_functions = find_stub_functions(module_file)
            if not stub_functions:
                continue

            # Check if any stubs conflict with real implementations
            conflicts = [f for f in stub_functions if f in real_implementations]

            if conflicts:
                conflicts_found = True
                print(f"\n⚠️  Found conflicts in {module_file.name}:")
                print(f"  Stub functions that override real implementations: {conflicts}")

                # Option 1: Rename the stub file
                # rename_stub_file(module_file)

                # Option 2: Create redirect file
                create_redirect_file(module_file, conflicts)

        # Fix controller import order
        controllers_dir = impl_dir.parent / "controllers"
        if controllers_dir.exists():
            print("\n🔧 Fixing controller import order...")
            fix_controller_import_order(controllers_dir)

        if conflicts_found:
            print("\n✅ Stub conflicts resolved!")
        else:
            print("\n✅ No stub conflicts found.")

        # Create validation script
        create_validation_script(impl_dir.parent.parent.parent.parent.parent)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def create_validation_script(repo_root: Path) -> None:
    """Create a validation script to check for stub conflicts."""
    script_path = repo_root / "scripts" / "validate_no_stub_conflicts.sh"

    script_content = '''#!/bin/bash
# Validate that no stub implementations override real implementations

echo "🔍 Checking for stub implementation conflicts..."

# Check if any module files have not_implemented_error returns
STUB_FILES=$(find backend/api/src/main/python/openapi_server/impl -name "*.py" \\
    ! -name "handlers.py" \\
    ! -name "__init__.py" \\
    ! -name "error_handler.py" \\
    ! -name "dependency_injection.py" \\
    -exec grep -l "return not_implemented_error" {} \\;)

if [ -n "$STUB_FILES" ]; then
    echo "⚠️  Warning: Found stub files that might override real implementations:"
    echo "$STUB_FILES"

    # Check if these stubs conflict with handlers.py
    for stub_file in $STUB_FILES; do
        # Extract function names from stub file
        STUB_FUNCS=$(grep -E "^def handle_" "$stub_file" | sed 's/def \\(handle_[^(]*\\).*/\\1/')

        for func in $STUB_FUNCS; do
            # Check if this function exists in handlers.py
            if grep -q "^def $func" backend/api/src/main/python/openapi_server/impl/handlers.py; then
                echo "  ❌ ERROR: $func in $(basename $stub_file) overrides implementation in handlers.py"
                exit 1
            fi
        done
    done
fi

echo "✅ No stub conflicts found"
'''

    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"\n📝 Created validation script: {script_path}")

if __name__ == "__main__":
    main()