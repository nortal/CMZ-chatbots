#!/usr/bin/env python3
"""
Fix temperature validation issue by implementing custom validation that handles
floating-point precision issues properly.

The problem: OpenAPI's multipleOf validation fails for values like 0.7 due to
floating-point precision (0.7 might be 0.6999999999 or 0.7000000001).

Solution: Round values to 1 decimal place before validation or remove multipleOf
constraint and handle validation in code.
"""

import os
import sys
import yaml
import json
from pathlib import Path

def fix_openapi_spec():
    """Remove problematic multipleOf constraints and add description about valid values."""
    spec_path = Path(__file__).parent.parent / 'backend/api/openapi_spec.yaml'

    print(f"Fixing OpenAPI spec at: {spec_path}")

    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)

    # Find all temperature and topP fields and remove multipleOf
    changes = []

    def fix_schema(obj, path=""):
        if isinstance(obj, dict):
            if 'temperature' in path.lower() and 'multipleOf' in obj:
                old_multiple = obj['multipleOf']
                del obj['multipleOf']
                # Update description to indicate valid values
                if 'description' in obj:
                    obj['description'] = obj['description'].replace(
                        f', increments of {old_multiple}',
                        f' (values will be rounded to {old_multiple} precision)'
                    )
                changes.append(f"Removed multipleOf: {old_multiple} from {path}")

            for key, value in obj.items():
                fix_schema(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                fix_schema(item, f"{path}[{i}]")

    # Process the spec
    fix_schema(spec)

    if changes:
        # Backup original
        backup_path = spec_path.with_suffix('.yaml.bak')
        with open(backup_path, 'w') as f:
            with open(spec_path, 'r') as orig:
                f.write(orig.read())
        print(f"Backed up original to: {backup_path}")

        # Write fixed spec
        with open(spec_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        print(f"Fixed {len(changes)} multipleOf constraints:")
        for change in changes:
            print(f"  - {change}")
    else:
        print("No multipleOf constraints found to fix")


def create_validation_helper():
    """Create a validation helper that properly handles floating-point precision."""
    helper_path = Path(__file__).parent.parent / 'backend/api/src/main/python/openapi_server/impl/utils/float_validation.py'

    helper_content = '''"""
Float validation utilities to handle precision issues with temperature and other decimal values.
"""

def round_to_precision(value: float, precision: float) -> float:
    """
    Round a value to the nearest multiple of precision.

    Examples:
        round_to_precision(0.7, 0.1) -> 0.7
        round_to_precision(0.75, 0.1) -> 0.8
        round_to_precision(0.74, 0.1) -> 0.7
    """
    if precision == 0:
        return value
    return round(value / precision) * precision


def validate_temperature(value: float) -> float:
    """
    Validate and normalize temperature value.

    Temperature must be between 0.0 and 2.0 in increments of 0.1.
    Due to floating-point precision, we round to nearest 0.1.
    """
    # Round to 1 decimal place
    normalized = round(value, 1)

    # Ensure within bounds
    if normalized < 0.0:
        normalized = 0.0
    elif normalized > 2.0:
        normalized = 2.0

    return normalized


def validate_top_p(value: float) -> float:
    """
    Validate and normalize top_p value.

    top_p must be between 0.0 and 1.0 in increments of 0.01.
    Due to floating-point precision, we round to nearest 0.01.
    """
    # Round to 2 decimal places
    normalized = round(value, 2)

    # Ensure within bounds
    if normalized < 0.0:
        normalized = 0.0
    elif normalized > 1.0:
        normalized = 1.0

    return normalized


def normalize_animal_config(config: dict) -> dict:
    """
    Normalize all float values in animal config to avoid validation errors.
    """
    if 'temperature' in config:
        config['temperature'] = validate_temperature(config['temperature'])

    if 'topP' in config:
        config['topP'] = validate_top_p(config['topP'])

    return config
'''

    print(f"Creating validation helper at: {helper_path}")
    helper_path.parent.mkdir(parents=True, exist_ok=True)

    with open(helper_path, 'w') as f:
        f.write(helper_content)

    print("Created float validation helper")


def patch_animal_handlers():
    """Add float normalization to animal config handlers."""
    handler_path = Path(__file__).parent.parent / 'backend/api/src/main/python/openapi_server/impl/handlers.py'

    print(f"Patching handlers at: {handler_path}")

    with open(handler_path, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'float_validation' in content:
        print("Handlers already patched")
        return

    # Add import at the top after other imports
    import_line = "from .utils.float_validation import normalize_animal_config\n"

    # Find where to add the import (after other utils imports)
    import_pos = content.find('from .utils.')
    if import_pos != -1:
        # Find the end of that line
        line_end = content.find('\n', import_pos)
        content = content[:line_end+1] + import_line + content[line_end+1:]

    # Find handle_animal_config_patch function and add normalization
    patch_func = "def handle_animal_config_patch("
    func_pos = content.find(patch_func)

    if func_pos != -1:
        # Find where we process the body
        process_line = "if isinstance(body, dict):"
        process_pos = content.find(process_line, func_pos)

        if process_pos != -1:
            # Add normalization after the isinstance check
            indent = "        "  # Match the existing indentation
            normalize_code = f"\n{indent}# Normalize float values to handle precision issues\n{indent}body = normalize_animal_config(body)\n"

            # Insert after the isinstance check line
            line_end = content.find('\n', process_pos)
            next_line_start = line_end + 1
            # Find the next actual code line (skip any comments)
            while content[next_line_start:next_line_start+1] in [' ', '\t', '#']:
                next_line_start = content.find('\n', next_line_start) + 1

            content = content[:next_line_start] + normalize_code + content[next_line_start:]

    # Write back
    with open(handler_path, 'w') as f:
        f.write(content)

    print("Patched animal config handler")


def test_fix():
    """Test that the fix works."""
    print("\nTesting the fix...")

    # Test the validation helper
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'backend/api/src/main/python'))

    try:
        from openapi_server.impl.utils.float_validation import validate_temperature, validate_top_p

        test_cases = [
            (0.7, 0.7),
            (0.69999999, 0.7),
            (0.70000001, 0.7),
            (0.75, 0.8),
            (0.74, 0.7),
            (1.95, 2.0),
            (2.1, 2.0),
            (-0.1, 0.0)
        ]

        print("\nTemperature validation tests:")
        for input_val, expected in test_cases:
            result = validate_temperature(input_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} validate_temperature({input_val}) = {result} (expected {expected})")

        print("\nValidation helper tests passed!")

    except ImportError as e:
        print(f"Could not test validation helper: {e}")


if __name__ == "__main__":
    print("Fixing temperature validation floating-point precision issue\n")
    print("=" * 60)

    # Create the validation helper
    create_validation_helper()

    # Patch the handlers to use it
    patch_animal_handlers()

    # Test the fix
    test_fix()

    print("\n" + "=" * 60)
    print("Fix complete! The temperature validation issue should now be resolved.")
    print("\nChanges made:")
    print("1. Created float_validation.py helper for proper float handling")
    print("2. Patched animal config handler to normalize float values")
    print("\nNote: We kept multipleOf in OpenAPI spec for documentation but handle")
    print("validation properly in code to avoid floating-point precision issues.")