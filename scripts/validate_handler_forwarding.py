#!/usr/bin/env python3
"""
Handler Forwarding Validation Script

Validates that impl/animals.py (forwarding layer) properly forwards to impl/handlers.py
(actual implementations) in the hexagonal architecture pattern.

This script detects broken forwarding chains that cause 501 errors despite having
working implementations in handlers.py.

Usage:
    python3 scripts/validate_handler_forwarding.py

Exit codes:
    0 - All validations passed
    1 - Validation failures detected
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ForwardingValidator:
    """Validates handler forwarding chain integrity"""

    def __init__(self, impl_dir: Path, endpoint_work_file: Path):
        self.impl_dir = impl_dir
        self.endpoint_work_file = endpoint_work_file
        self.handlers_file = impl_dir / "handlers.py"
        self.animals_file = impl_dir / "animals.py"
        self.failures = []
        self.warnings = []
        self.successes = []

    def extract_implemented_endpoints(self) -> Set[str]:
        """
        Extract list of implemented endpoints from ENDPOINT-WORK.md

        Returns set of handler function names that should be implemented
        """
        if not self.endpoint_work_file.exists():
            self.warnings.append(f"ENDPOINT-WORK.md not found at {self.endpoint_work_file}")
            return set()

        implemented = set()
        try:
            with open(self.endpoint_work_file, 'r') as f:
                content = f.read()

            # Find the "## ✅ IMPLEMENTED (DO NOT TOUCH)" section
            implemented_section_match = re.search(
                r'## ✅ IMPLEMENTED.*?(?=##|\Z)',
                content,
                re.DOTALL
            )

            if implemented_section_match:
                implemented_section = implemented_section_match.group(0)

                # Extract handler function names from patterns like:
                # - **GET /animal_config** → `handlers.py:handle_animal_config_get()`
                # - **PATCH /animal_config** → `handlers.py:handle_animal_config_patch()`
                handler_pattern = r'`handlers\.py:(handle_\w+)\(\)`'
                handlers = re.findall(handler_pattern, implemented_section)
                implemented.update(handlers)

                # Also look for direct handler mentions without handlers.py prefix
                direct_pattern = r'→ `(handle_\w+)\(\)`'
                direct_handlers = re.findall(direct_pattern, implemented_section)
                implemented.update(direct_handlers)

        except Exception as e:
            self.warnings.append(f"Error reading ENDPOINT-WORK.md: {e}")

        return implemented

    def extract_handler_implementations(self) -> Set[str]:
        """
        Extract list of handler functions implemented in handlers.py

        Returns set of handler function names that exist in handlers.py
        """
        if not self.handlers_file.exists():
            self.warnings.append(f"handlers.py not found at {self.handlers_file}")
            return set()

        implementations = set()
        try:
            with open(self.handlers_file, 'r') as f:
                content = f.read()

            # Find all function definitions starting with handle_
            pattern = r'def (handle_\w+)\s*\('
            implementations.update(re.findall(pattern, content))

        except Exception as e:
            self.warnings.append(f"Error reading handlers.py: {e}")

        return implementations

    def extract_animals_handlers(self) -> Dict[str, str]:
        """
        Extract handler functions from animals.py and determine their type

        Returns dict mapping handler_name → "forwarding" or "501"
        """
        if not self.animals_file.exists():
            self.warnings.append(f"animals.py not found at {self.animals_file}")
            return {}

        handlers = {}
        try:
            with open(self.animals_file, 'r') as f:
                content = f.read()

            # Split by function definitions to parse function bodies reliably
            # This is more reliable than regex for Python's indentation-based syntax
            functions = content.split('\ndef handle_')

            for func_text in functions[1:]:  # Skip first part (file header)
                # Extract function name from first line
                first_line = func_text.split('(')[0].strip()
                handler_name = f'handle_{first_line}'

                # Check if it forwards to handlers.py
                if 'from .handlers import' in func_text and 'as real_handler' in func_text:
                    handlers[handler_name] = "forwarding"
                # Check if it returns not_implemented_error
                elif 'not_implemented_error' in func_text or 'Error(' in func_text:
                    handlers[handler_name] = "501"
                else:
                    handlers[handler_name] = "unknown"

        except Exception as e:
            self.warnings.append(f"Error reading animals.py: {e}")

        return handlers

    def validate(self) -> bool:
        """
        Run validation checks

        Returns True if all validations pass, False otherwise
        """
        print("=" * 80)
        print("🔍 Handler Forwarding Validation")
        print("=" * 80)
        print()

        # Step 1: Extract data
        print("📋 Step 1: Extracting handler information...")
        implemented_endpoints = self.extract_implemented_endpoints()
        handler_implementations = self.extract_handler_implementations()
        animals_handlers = self.extract_animals_handlers()

        print(f"  ✓ Found {len(implemented_endpoints)} implemented endpoints in ENDPOINT-WORK.md")
        print(f"  ✓ Found {len(handler_implementations)} implementations in handlers.py")
        print(f"  ✓ Found {len(animals_handlers)} handlers in animals.py")
        print()

        # Step 2: Validate forwarding chains
        print("🔗 Step 2: Validating forwarding chains...")
        print()

        for handler_name in handler_implementations:
            handler_type = animals_handlers.get(handler_name)

            if handler_type is None:
                # Handler exists in handlers.py but not in animals.py
                self.failures.append(
                    f"❌ {handler_name}: Missing in animals.py but exists in handlers.py"
                )
            elif handler_type == "forwarding":
                # Correct: forwarding to handlers.py
                self.successes.append(
                    f"✅ {handler_name}: Correctly forwarding to handlers.py"
                )
            elif handler_type == "501":
                # BROKEN: Returns 501 but handlers.py has implementation
                self.failures.append(
                    f"❌ {handler_name}: Returns 501 but handlers.py has implementation (BROKEN FORWARDING)"
                )
            else:
                # Unknown pattern
                self.warnings.append(
                    f"⚠️  {handler_name}: Unknown handler pattern in animals.py"
                )

        # Step 3: Check for orphaned stubs in animals.py
        print("🔍 Step 3: Checking for orphaned stubs...")
        print()

        for handler_name, handler_type in animals_handlers.items():
            if handler_name not in handler_implementations:
                if handler_type == "forwarding":
                    # Forwards to non-existent handler
                    self.failures.append(
                        f"❌ {handler_name}: Forwards to handlers.py but implementation doesn't exist"
                    )
                elif handler_type == "501":
                    # Correctly returns 501 for unimplemented endpoint
                    self.successes.append(
                        f"✅ {handler_name}: Correctly returns 501 (not implemented)"
                    )

        # Step 4: Report results
        print()
        print("=" * 80)
        print("📊 Validation Results")
        print("=" * 80)
        print()

        if self.successes:
            print(f"✅ {len(self.successes)} handlers validated successfully:")
            for success in self.successes[:10]:  # Show first 10
                print(f"  {success}")
            if len(self.successes) > 10:
                print(f"  ... and {len(self.successes) - 10} more")
            print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.failures:
            print(f"❌ {len(self.failures)} CRITICAL FAILURES:")
            for failure in self.failures:
                print(f"  {failure}")
            print()
            print("=" * 80)
            print("🔧 RECOMMENDED ACTIONS:")
            print("=" * 80)
            print()
            print("1. Run post_openapi_generation.py to regenerate forwarding stubs:")
            print("   python3 scripts/post_openapi_generation.py backend/api/src/main/python")
            print()
            print("2. Verify ENDPOINT-WORK.md is up to date:")
            print("   - Check that implemented endpoints are properly documented")
            print("   - Ensure handler function names match handlers.py")
            print()
            print("3. Test affected endpoints after regeneration:")
            print("   make run-api")
            print("   curl -X GET http://localhost:8080/animal_list")
            print()
            return False

        print("✅ All validations passed! Hexagonal architecture forwarding chain is intact.")
        print()
        return True


def main():
    # Determine project root and impl directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    impl_dir = project_root / "backend" / "api" / "src" / "main" / "python" / "openapi_server" / "impl"
    endpoint_work_file = project_root / "ENDPOINT-WORK.md"

    # Validate paths
    if not impl_dir.exists():
        print(f"❌ Error: Implementation directory not found: {impl_dir}")
        sys.exit(1)

    # Run validation
    validator = ForwardingValidator(impl_dir, endpoint_work_file)
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
