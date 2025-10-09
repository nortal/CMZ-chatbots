#!/usr/bin/env python3
"""
Fix OpenAPI Handler Mappings

This script fixes the handler mapping issues in handlers.py by:
1. Finding all operationIds from controllers
2. Adding missing mappings to the handler_map
3. Creating stub handlers for unmapped operations
"""

import os
import re
from pathlib import Path

def find_all_operation_ids():
    """Find all operation IDs from generated controllers"""
    controllers_path = Path("backend/api/src/main/python/openapi_server/controllers")
    operation_ids = set()

    for controller_file in controllers_path.glob("*_controller.py"):
        with open(controller_file, 'r') as f:
            content = f.read()
            # Find all function definitions
            functions = re.findall(r'^def\s+(\w+)\(', content, re.MULTILINE)
            operation_ids.update(functions)

    return sorted(operation_ids)

def get_current_mappings():
    """Get current mappings from handlers.py"""
    handlers_path = Path("backend/api/src/main/python/openapi_server/impl/handlers.py")
    with open(handlers_path, 'r') as f:
        content = f.read()

    # Find the handler_map dictionary
    map_match = re.search(r'handler_map\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if not map_match:
        return {}

    map_content = map_match.group(1)
    mappings = {}

    # Extract key-value pairs
    for line in map_content.split('\n'):
        match = re.match(r'\s*[\'"](\w+)[\'"]:\s*(\w+)', line)
        if match:
            mappings[match.group(1)] = match.group(2)

    return mappings

def create_handler_function_stub(operation_id):
    """Create a stub handler function for an operation"""
    return f"""
def handle_{operation_id}(*args, **kwargs) -> Tuple[Any, int]:
    \"\"\"Handler for {operation_id}\"\"\"
    from openapi_server.models.error import Error
    error = Error(
        code="not_implemented",
        message=f"Operation {{operation_id}} not yet implemented",
        details={{"operation": "{operation_id}"}}
    )
    return error.to_dict(), 501
"""

def update_handlers_file():
    """Update handlers.py with missing mappings and functions"""
    handlers_path = Path("backend/api/src/main/python/openapi_server/impl/handlers.py")

    # Read current content
    with open(handlers_path, 'r') as f:
        content = f.read()

    # Find all operation IDs
    all_ops = find_all_operation_ids()
    current_mappings = get_current_mappings()

    print(f"Found {len(all_ops)} operations in controllers")
    print(f"Current mappings: {len(current_mappings)}")

    # Find missing mappings
    missing_ops = set(all_ops) - set(current_mappings.keys())
    print(f"Missing mappings: {len(missing_ops)}")

    if missing_ops:
        print("\nMissing operations that need mapping:")
        for op in sorted(missing_ops):
            print(f"  - {op}")

        # Find the handler_map in the content
        map_match = re.search(r'(handler_map\s*=\s*\{)([^}]+)(\})', content, re.DOTALL)
        if map_match:
            # Add new mappings
            new_mappings = []
            for op in sorted(missing_ops):
                # Determine the handler name based on patterns
                if op == 'root_get':
                    handler_name = 'handle_homepage_get'
                elif op == 'admin_get':
                    handler_name = 'handle_admin_dashboard_get'
                elif op == 'member_get':
                    handler_name = 'handle_member_dashboard_get'
                else:
                    handler_name = f'handle_{op}'

                new_mappings.append(f"            '{op}': {handler_name},")

            # Insert new mappings before the closing brace
            old_map_content = map_match.group(2)
            # Remove trailing comma and whitespace
            old_map_content = old_map_content.rstrip().rstrip(',')

            new_map_content = old_map_content + ',\n' + '\n'.join(new_mappings)

            # Replace the map in content
            new_content = content[:map_match.start()] + \
                         map_match.group(1) + new_map_content + map_match.group(3) + \
                         content[map_match.end():]

            # Write back
            with open(handlers_path, 'w') as f:
                f.write(new_content)

            print(f"\n✅ Added {len(missing_ops)} missing mappings to handler_map")

            # Now check if handler functions exist
            for op in sorted(missing_ops):
                if op in ['root_get', 'admin_get', 'member_get']:
                    continue  # These use existing handlers

                handler_name = f'handle_{op}'
                if f'def {handler_name}' not in new_content:
                    print(f"⚠️  Handler function {handler_name} doesn't exist - needs implementation")

def main():
    """Main function"""
    print("🔧 Fixing OpenAPI Handler Mappings\n")

    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)

    update_handlers_file()

    print("\n✅ Handler mappings updated!")
    print("\nNext steps:")
    print("1. Review the updated handlers.py file")
    print("2. Implement any missing handler functions")
    print("3. Rebuild and restart the API")
    print("4. Test the endpoints again")

if __name__ == "__main__":
    main()