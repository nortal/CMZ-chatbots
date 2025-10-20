#!/usr/bin/env python3
"""
Comprehensive Handler Forwarding Validation Script

Validates that all impl/*.py files (forwarding layer) properly forward to impl/handlers.py
(actual implementations) in the hexagonal architecture pattern.

This script detects broken forwarding chains across ALL domains that cause 501 errors
despite having working implementations in handlers.py.

Usage:
    python3 scripts/validate_handler_forwarding_comprehensive.py

Exit codes:
    0 - All validations passed
    1 - Validation failures detected
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ComprehensiveForwardingValidator:
    """Validates handler forwarding chain integrity across all domains"""

    # Domains to validate (all impl files except these)
    EXCLUDED_FILES = {'__init__.py', 'handlers.py', 'utils', 'chatgpt_integration.py',
                      'cognito_authentication.py', 'dependency_injection.py', 'error_handler.py',
                      'families_mock.py', 'family_bidirectional.py', 'handler_map_documented.py',
                      'streaming_response.py', 'validators.py', 'auth_mock.py',
                      'admin_hexagonal.py', 'test_animals.py'}

    def __init__(self, impl_dir: Path):
        self.impl_dir = impl_dir
        self.handlers_file = impl_dir / "handlers.py"
        self.failures = []
        self.warnings = []
        self.successes = []
        self.domain_stats = {}

    def get_domain_files(self) -> List[Path]:
        """Get all domain impl files to validate"""
        domain_files = []
        for file_path in self.impl_dir.glob("*.py"):
            if file_path.name not in self.EXCLUDED_FILES:
                domain_files.append(file_path)
        return sorted(domain_files)

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

    def extract_domain_handlers(self, domain_file: Path) -> Dict[str, str]:
        """
        Extract handler functions from a domain impl file and determine their type

        Returns dict mapping handler_name → "forwarding" or "501" or "unknown"
        """
        handlers = {}

        if not domain_file.exists():
            self.warnings.append(f"{domain_file.name} not found")
            return handlers

        try:
            with open(domain_file, 'r') as f:
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
            self.warnings.append(f"Error reading {domain_file.name}: {e}")

        return handlers

    def validate_domain(self, domain_file: Path, handler_implementations: Set[str]) -> Dict[str, any]:
        """
        Validate a single domain file

        Returns statistics about the domain validation
        """
        domain_name = domain_file.stem
        domain_handlers = self.extract_domain_handlers(domain_file)

        stats = {
            'name': domain_name,
            'total': 0,
            'forwarding': 0,
            'not_implemented': 0,
            'missing': 0,
            'orphaned': 0,
            'unknown': 0
        }

        # Check handlers that should be in this domain
        for handler_name in handler_implementations:
            # Check if this handler belongs to this domain (basic heuristic)
            # This is a simplified check - in reality, we'd need domain mapping
            handler_type = domain_handlers.get(handler_name)

            if handler_type == "forwarding":
                stats['forwarding'] += 1
                stats['total'] += 1
                self.successes.append(
                    f"✅ {domain_name}.py::{handler_name}: Correctly forwarding to handlers.py"
                )
            elif handler_type == "501":
                stats['not_implemented'] += 1
                stats['total'] += 1
                # Only report as failure if it exists in handlers.py
                if handler_name in handler_implementations:
                    self.failures.append(
                        f"❌ {domain_name}.py::{handler_name}: Returns 501 but handlers.py has implementation (BROKEN FORWARDING)"
                    )

        # Check for handlers in domain file but not in handlers.py
        for handler_name, handler_type in domain_handlers.items():
            if handler_name not in handler_implementations:
                if handler_type == "forwarding":
                    stats['orphaned'] += 1
                    self.failures.append(
                        f"❌ {domain_name}.py::{handler_name}: Forwards to handlers.py but implementation doesn't exist"
                    )
                elif handler_type == "501":
                    stats['not_implemented'] += 1
                    self.successes.append(
                        f"✅ {domain_name}.py::{handler_name}: Correctly returns 501 (not implemented)"
                    )
                else:
                    stats['unknown'] += 1
                    self.warnings.append(
                        f"⚠️  {domain_name}.py::{handler_name}: Unknown handler pattern"
                    )

        return stats

    def validate(self) -> bool:
        """
        Run comprehensive validation checks across all domains

        Returns True if all validations pass, False otherwise
        """
        print("=" * 80)
        print("🔍 Comprehensive Handler Forwarding Validation")
        print("=" * 80)
        print()

        # Step 1: Extract handler implementations from handlers.py
        print("📋 Step 1: Extracting handler implementations from handlers.py...")
        handler_implementations = self.extract_handler_implementations()
        print(f"  ✓ Found {len(handler_implementations)} implementations in handlers.py")
        print()

        # Step 2: Get all domain files to validate
        print("📋 Step 2: Discovering domain files...")
        domain_files = self.get_domain_files()
        print(f"  ✓ Found {len(domain_files)} domain files to validate:")
        for domain_file in domain_files:
            print(f"    - {domain_file.name}")
        print()

        # Step 3: Validate each domain
        print("🔗 Step 3: Validating forwarding chains by domain...")
        print()

        for domain_file in domain_files:
            stats = self.validate_domain(domain_file, handler_implementations)
            self.domain_stats[domain_file.stem] = stats

        # Step 4: Report results
        print()
        print("=" * 80)
        print("📊 Validation Results by Domain")
        print("=" * 80)
        print()

        for domain_name, stats in self.domain_stats.items():
            print(f"📦 {domain_name}.py:")
            print(f"   Forwarding: {stats['forwarding']}")
            print(f"   Not Implemented: {stats['not_implemented']}")
            print(f"   Missing: {stats['missing']}")
            print(f"   Orphaned: {stats['orphaned']}")
            if stats['unknown'] > 0:
                print(f"   Unknown: {stats['unknown']}")
            print()

        # Step 5: Summary
        print("=" * 80)
        print("📊 Overall Summary")
        print("=" * 80)
        print()

        if self.successes:
            print(f"✅ {len(self.successes)} handlers validated successfully")
            print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
            print()

        if self.failures:
            print(f"❌ {len(self.failures)} CRITICAL FAILURES:")
            for failure in self.failures[:20]:  # Show first 20
                print(f"  {failure}")
            if len(self.failures) > 20:
                print(f"  ... and {len(self.failures) - 20} more failures")
            print()
            print("=" * 80)
            print("🔧 RECOMMENDED ACTIONS:")
            print("=" * 80)
            print()
            print("1. Regenerate forwarding stubs for broken domains:")
            print("   rm backend/api/src/main/python/openapi_server/impl/{broken_domain}.py")
            print("   python3 scripts/post_openapi_generation.py backend/api/src/main/python")
            print()
            print("2. Verify handlers.py has implementations for all forwarding stubs:")
            print("   grep 'def handle_' backend/api/src/main/python/openapi_server/impl/handlers.py")
            print()
            print("3. Run this validation again after fixes:")
            print("   python3 scripts/validate_handler_forwarding_comprehensive.py")
            print()
            return False

        print("✅ All validations passed! Hexagonal architecture forwarding chain is intact across all domains.")
        print()
        return True


def main():
    # Determine project root and impl directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    impl_dir = project_root / "backend" / "api" / "src" / "main" / "python" / "openapi_server" / "impl"

    # Validate paths
    if not impl_dir.exists():
        print(f"❌ Error: Implementation directory not found: {impl_dir}")
        sys.exit(1)

    # Run validation
    validator = ComprehensiveForwardingValidator(impl_dir)
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
