#!/usr/bin/env python3
"""
Fix parameter naming mismatches in generated OpenAPI controllers.

This script fixes the recurring issue where OpenAPI spec uses camelCase (animalId)
but Connexion/Python expects snake_case (animal_id).
"""
import os
import re
import glob
import sys

def fix_controller_parameters(file_path):
    """Fix parameter naming in a single controller file."""
    print(f"Checking {os.path.basename(file_path)}...")

    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content
    changes_made = []

    # Define parameter naming fixes
    # Pattern: (function_prefix, wrong_param, correct_param)
    fixes = [
        # Animal controller fixes
        ('animal_get', 'animalId', 'animal_id'),
        ('animal_put', 'animalId', 'animal_id'),
        ('animal_delete', 'animalId', 'animal_id'),
        ('animal_id_get', 'id', 'animal_id'),
        ('animal_id_put', 'id', 'animal_id'),
        ('animal_id_delete', 'id', 'animal_id'),

        # User controller fixes
        ('user_get', 'userId', 'user_id'),
        ('user_put', 'userId', 'user_id'),
        ('user_delete', 'userId', 'user_id'),
        ('user_id_get', 'id', 'user_id'),
        ('user_id_put', 'id', 'user_id'),
        ('user_id_delete', 'id', 'user_id'),

        # Family controller fixes
        ('family_get', 'familyId', 'family_id'),
        ('family_put', 'familyId', 'family_id'),
        ('family_delete', 'familyId', 'family_id'),
        ('family_id_get', 'id', 'family_id'),
        ('family_id_put', 'id', 'family_id'),
        ('family_id_delete', 'id', 'family_id'),

        # Conversation controller fixes
        ('conversation_get', 'conversationId', 'conversation_id'),
        ('conversation_delete', 'conversationId', 'conversation_id'),
        ('conversation_history_get', 'conversationId', 'conversation_id'),

        # Knowledge controller fixes
        ('knowledge_article_get', 'articleId', 'article_id'),
        ('knowledge_article_delete', 'articleId', 'article_id'),

        # Media controller fixes
        ('media_get', 'mediaId', 'media_id'),
        ('media_delete', 'mediaId', 'media_id'),
    ]

    for func_name, wrong_param, correct_param in fixes:
        # Fix function definition
        pattern = rf'def {func_name}\({wrong_param}([,\)])'
        replacement = rf'def {func_name}({correct_param}\1'

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made.append(f"  - Fixed {func_name}({wrong_param}) -> {func_name}({correct_param})")

        # Also fix references to the parameter in the function body
        # But only within the specific function
        func_pattern = rf'(def {func_name}\(.*?\):.*?)(\n(?:def|\Z))'
        func_match = re.search(func_pattern, content, re.DOTALL)

        if func_match:
            func_body = func_match.group(1)
            # Replace parameter references in function body
            func_body = re.sub(rf'\b{wrong_param}\b', correct_param, func_body)
            content = content[:func_match.start()] + func_body + content[func_match.start(1) + len(func_body):]

    # Generic pattern to catch any remaining xxxId parameters
    generic_pattern = r'def (\w+)\(([^)]*?)([a-z]+)Id([^a-zA-Z])'

    def replace_camel_id(match):
        func_name = match.group(1)
        params_before = match.group(2)
        prefix = match.group(3)
        after = match.group(4)

        # Convert camelCase to snake_case
        snake_param = f"{prefix}_id"

        if f"Fixed {func_name}" not in str(changes_made):
            changes_made.append(f"  - Fixed {func_name}({prefix}Id) -> {func_name}({snake_param})")

        return f"def {func_name}({params_before}{snake_param}{after}"

    content = re.sub(generic_pattern, replace_camel_id, content)

    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)

        if changes_made:
            print(f"  Fixed {len(changes_made)} parameter(s):")
            for change in changes_made:
                print(change)
    else:
        print(f"  No changes needed")

    return len(changes_made) > 0

def main():
    """Main function to fix all controller files."""
    print("=== Fixing Parameter Naming Issues ===")
    print()

    # Find all controller files
    controller_pattern = "backend/api/src/main/python/openapi_server/controllers/*_controller.py"
    controller_files = glob.glob(controller_pattern)

    if not controller_files:
        print(f"No controller files found matching: {controller_pattern}")
        return 1

    print(f"Found {len(controller_files)} controller file(s)")
    print()

    total_fixed = 0
    for controller_file in controller_files:
        if fix_controller_parameters(controller_file):
            total_fixed += 1

    print()
    print(f"=== Summary ===")
    print(f"Fixed parameter naming in {total_fixed} file(s)")

    if total_fixed > 0:
        print("\n⚠️  Remember to rebuild and restart the API:")
        print("  make build-api && make run-api")

    return 0

if __name__ == "__main__":
    sys.exit(main())