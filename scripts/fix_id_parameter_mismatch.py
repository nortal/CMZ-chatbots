#!/usr/bin/env python3
"""
Fix parameter name mismatches between OpenAPI controllers and handlers.

This script addresses the recurring issue where Connexion renames 'id' parameters
to 'id_' to avoid shadowing Python's built-in id() function, causing handler
functions to fail with "unexpected keyword argument" errors.

The solution makes all handlers accept both 'id' and 'id_' parameters using
default arguments and **kwargs.
"""

import re
import os
from pathlib import Path
from typing import List, Tuple


def find_handler_functions(content: str) -> List[Tuple[str, str]]:
    """
    Find all handler functions that might have id parameter issues.
    Returns list of (function_name, full_function_signature) tuples.
    """
    # Pattern to find functions with 'id' in their name
    pattern = r'(def\s+handle_\w*id\w*\([^)]*\)):'
    matches = re.findall(pattern, content)
    return matches


def fix_id_parameter(signature: str) -> str:
    """
    Fix a function signature to accept both id and id_ parameters.

    Examples:
        'def handle_animal_id_get(id: str)'
        -> 'def handle_animal_id_get(id: str = None, id_: str = None, **kwargs)'

        'def handle_animal_id_put(id: str, body: Dict[str, Any])'
        -> 'def handle_animal_id_put(body: Dict[str, Any] = None, id: str = None, id_: str = None, **kwargs)'
    """

    # Extract function name and parameters
    match = re.match(r'(def\s+\w+)\(([^)]*)\)', signature)
    if not match:
        return signature

    func_name = match.group(1)
    params = match.group(2).strip()

    # Skip if already fixed (has both id and id_ or **kwargs)
    if 'id_' in params and '**kwargs' in params:
        return signature

    # Parse existing parameters
    param_list = []
    if params:
        # Split by comma but respect nested brackets
        depth = 0
        current = []
        for char in params:
            if char in '([{':
                depth += 1
            elif char in ')]}':
                depth -= 1
            elif char == ',' and depth == 0:
                param_list.append(''.join(current).strip())
                current = []
                continue
            current.append(char)
        if current:
            param_list.append(''.join(current).strip())

    # Separate id and non-id parameters
    id_params = []
    other_params = []

    for param in param_list:
        if param.startswith('id:') or param.startswith('id ') or param == 'id':
            # Make id optional with default None
            if '=' not in param:
                param = param.replace('id:', 'id: str =').replace('id ', 'id: str =')
                if param == 'id':
                    param = 'id: str = None'
                elif ': str' in param and '=' not in param:
                    param = param.replace(': str', ': str = None')
            id_params.append(param)
        elif not param.startswith('*'):
            # Make other parameters optional too
            if '=' not in param and ':' in param:
                param = param.replace(':', ':') + ' = None'
            other_params.append(param)

    # Build new parameter list: other_params, id params, id_, **kwargs
    new_params = []

    # Add non-id parameters first (like body)
    new_params.extend(other_params)

    # Add original id parameter (made optional)
    new_params.extend(id_params)

    # Add id_ parameter if not present
    if not any('id_' in p for p in new_params):
        new_params.append('id_: str = None')

    # Add **kwargs if not present
    if not any('**' in p for p in param_list):
        new_params.append('**kwargs')

    return f"{func_name}({', '.join(new_params)})"


def add_parameter_handling(content: str, func_name: str) -> str:
    """
    Add code to handle both id and id_ parameters in function body.
    """
    # Find the function definition
    pattern = rf'(def\s+{re.escape(func_name)}\([^)]*\):.*?)(\n\s+""".*?""")?(\n\s+try:|\n\s+[a-z])'

    def replacer(match):
        func_def = match.group(1)
        docstring = match.group(2) or ''
        body_start = match.group(3)

        # Check if handling already exists
        if 'animal_id = id if id is not None else id_' in content[match.start():match.start()+500]:
            return match.group(0)

        # Add parameter handling code
        handling_code = '''
    try:
        # Handle both parameter names (Connexion may pass id or id_)
        animal_id = id if id is not None else id_
        if animal_id is None:
            from .error_handler import create_error_response
            return create_error_response(
                "missing_parameter",
                "Missing required parameter: id",
                {}
            ), 400'''

        # If body starts with try:, merge with it
        if body_start == '\n    try:':
            return func_def + docstring + handling_code
        else:
            return func_def + docstring + '\n' + handling_code + '\n' + body_start.lstrip('\n')

    return re.sub(pattern, replacer, content, flags=re.MULTILINE | re.DOTALL)


def fix_handlers_file(file_path: Path) -> bool:
    """
    Fix all id parameter issues in a handlers file.
    Returns True if changes were made.
    """
    content = file_path.read_text()
    original = content

    # Find all handler functions with potential id issues
    functions = find_handler_functions(content)

    for func_sig in functions:
        # Only process functions that have 'id' parameters
        if 'id' in func_sig and 'id_' not in func_sig:
            # Fix the signature
            new_sig = fix_id_parameter(func_sig)
            if new_sig != func_sig:
                content = content.replace(func_sig + ':', new_sig + ':')
                print(f"  Fixed signature: {func_sig} -> {new_sig}")

                # Extract function name for body fixing
                func_match = re.match(r'def\s+(\w+)', func_sig)
                if func_match:
                    func_name = func_match.group(1)
                    # Add parameter handling in function body
                    content = add_parameter_handling(content, func_name)

    if content != original:
        file_path.write_text(content)
        return True
    return False


def main():
    """Main function to fix parameter mismatches."""
    print("Fixing id/id_ parameter mismatches in handler files...")

    # Find all handler files
    base_path = Path("/Users/keithstegbauer/repositories/CMZ-chatbots")
    handlers_path = base_path / "backend/api/src/main/python/openapi_server/impl"

    files_to_check = [
        handlers_path / "handlers.py",
        # Add other handler files as needed
    ]

    fixed_count = 0
    for file_path in files_to_check:
        if file_path.exists():
            print(f"\nChecking {file_path.name}...")
            if fix_handlers_file(file_path):
                fixed_count += 1
                print(f"  ✓ Fixed issues in {file_path.name}")
            else:
                print(f"  ✓ No issues found in {file_path.name}")
        else:
            print(f"  ⚠ File not found: {file_path}")

    print(f"\n✅ Fixed {fixed_count} file(s)")

    # Add to post-generation script
    post_gen_script = base_path / "scripts/post_openapi_generation.py"
    if post_gen_script.exists():
        print("\n💡 Tip: Add this script to post_openapi_generation.py to run automatically after code generation")


if __name__ == "__main__":
    main()