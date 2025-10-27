#!/usr/bin/env python3
"""
Merge OpenAPI extension file with main specification.
Handles paths and components sections systematically.
"""
import yaml
import sys
from pathlib import Path

def merge_openapi_files(main_spec_path, extension_path, output_path):
    """Merge OpenAPI extension into main specification."""

    # Load main specification
    with open(main_spec_path, 'r') as f:
        main_spec = yaml.safe_load(f)

    # Load extension specification
    with open(extension_path, 'r') as f:
        extension_spec = yaml.safe_load(f)

    # Merge paths
    if 'paths' in extension_spec:
        if 'paths' not in main_spec:
            main_spec['paths'] = {}
        main_spec['paths'].update(extension_spec['paths'])

    # Merge components
    if 'components' in extension_spec:
        if 'components' not in main_spec:
            main_spec['components'] = {}

        # Merge schemas
        if 'schemas' in extension_spec['components']:
            if 'schemas' not in main_spec['components']:
                main_spec['components']['schemas'] = {}
            main_spec['components']['schemas'].update(extension_spec['components']['schemas'])

        # Merge parameters
        if 'parameters' in extension_spec['components']:
            if 'parameters' not in main_spec['components']:
                main_spec['components']['parameters'] = {}
            main_spec['components']['parameters'].update(extension_spec['components']['parameters'])

        # Merge responses
        if 'responses' in extension_spec['components']:
            if 'responses' not in main_spec['components']:
                main_spec['components']['responses'] = {}
            main_spec['components']['responses'].update(extension_spec['components']['responses'])

    # Write merged specification
    with open(output_path, 'w') as f:
        yaml.dump(main_spec, f, default_flow_style=False, sort_keys=False, indent=2)

    print(f"✅ Merged OpenAPI specification written to {output_path}")
    print(f"📊 Added {len(extension_spec.get('paths', {}))} new endpoints")
    print(f"🔧 Added {len(extension_spec.get('components', {}).get('schemas', {}))} new schemas")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_openapi_extension.py <main_spec> <extension> <output>")
        sys.exit(1)

    main_spec_path = Path(sys.argv[1])
    extension_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    if not main_spec_path.exists():
        print(f"❌ Main specification file not found: {main_spec_path}")
        sys.exit(1)

    if not extension_path.exists():
        print(f"❌ Extension file not found: {extension_path}")
        sys.exit(1)

    merge_openapi_files(main_spec_path, extension_path, output_path)