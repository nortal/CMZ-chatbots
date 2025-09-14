#!/usr/bin/env python3
"""
Simplified naming convention validator for the CMZ project
Focuses on finding animal_id vs animalId inconsistencies
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import List, Set

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_naming_conventions_simple.py <project_root>")
        sys.exit(1)

    project_root = Path(sys.argv[1])
    openapi_spec_path = project_root / "backend/api/openapi_spec.yaml"
    impl_dir = project_root / "backend/api/src/main/python/openapi_server/impl"

    errors = []
    warnings = []

    print("🔍 Validating naming conventions (simplified)...")

    # Check OpenAPI spec uses camelCase consistently
    try:
        with open(openapi_spec_path, 'r') as f:
            spec_content = f.read()

        # Count occurrences
        animal_id_count = len(re.findall(r'\banimal_id\b', spec_content))
        animalId_count = len(re.findall(r'\banimalId\b', spec_content))

        print(f"OpenAPI spec: animal_id={animal_id_count}, animalId={animalId_count}")

        if animal_id_count > 0:
            errors.append(f"OpenAPI spec contains {animal_id_count} instances of snake_case 'animal_id'")

    except Exception as e:
        errors.append(f"Failed to read OpenAPI spec: {e}")

    # Check implementation files
    mixed_files = []
    for py_file in impl_dir.rglob("*.py"):
        try:
            with open(py_file, 'r') as f:
                content = f.read()

            has_animal_id = 'animal_id' in content
            has_animalId = 'animalId' in content

            if has_animal_id and has_animalId:
                mixed_files.append(py_file.relative_to(project_root))

        except Exception as e:
            errors.append(f"Failed to read {py_file}: {e}")

    if mixed_files:
        warnings.append(f"Files with mixed naming conventions: {len(mixed_files)}")
        for file in mixed_files[:5]:  # Show first 5
            warnings.append(f"  • {file}")
        if len(mixed_files) > 5:
            warnings.append(f"  • ... and {len(mixed_files) - 5} more")

    # Report results
    if errors:
        print("❌ ERRORS:")
        for error in errors:
            print(f"  • {error}")

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")

    if not errors and not warnings:
        print("✅ All naming conventions are consistent!")

    # Create simple recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("  1. OpenAPI spec should use camelCase (animalId) for JSON consistency")
    print("  2. Python code should use snake_case (animal_id) following PEP 8")
    print("  3. Use conversion functions between API layer and implementation")
    print("  4. Consider creating utility functions for field name mapping")

    return len(errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)