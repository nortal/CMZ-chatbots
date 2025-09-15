#!/usr/bin/env python3
"""
Version Validation Script

Validates that the API server returns the expected version information
by comparing the health check response with version.json.

Usage:
    python scripts/validate_version.py [API_URL]

Exit codes:
    0: Success - Version validation passed
    1: Failure - Version mismatch or validation error
"""

import json
import sys
import requests
import os
from typing import Dict, Any, Tuple


def load_version_file() -> Tuple[Dict[str, Any], str]:
    """Load version.json from project root"""
    version_path = os.path.join(os.getcwd(), "version.json")

    try:
        with open(version_path, 'r') as f:
            version_data = json.load(f)
        return version_data, ""
    except FileNotFoundError:
        return {}, f"version.json not found at {version_path}"
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON in version.json: {str(e)}"
    except Exception as e:
        return {}, f"Error reading version.json: {str(e)}"


def query_health_endpoint(api_url: str) -> Tuple[Dict[str, Any], str]:
    """Query the API health endpoint"""
    try:
        response = requests.get(f"{api_url}/system_health", timeout=10)
        response.raise_for_status()
        return response.json(), ""
    except requests.exceptions.ConnectionError:
        return {}, f"Cannot connect to API at {api_url}"
    except requests.exceptions.Timeout:
        return {}, "API request timeout"
    except requests.exceptions.HTTPError as e:
        return {}, f"API returned error: {e.response.status_code}"
    except json.JSONDecodeError:
        return {}, "API returned invalid JSON"
    except Exception as e:
        return {}, f"Unexpected error querying API: {str(e)}"


def validate_version_consistency(version_data: Dict[str, Any], health_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate that version information matches between file and API"""
    errors = []

    # Check UUID consistency
    file_uuid = version_data.get("apiVersionUuid")
    api_uuid = health_data.get("apiVersionUuid")

    if not file_uuid:
        errors.append("version.json missing apiVersionUuid")
    elif not api_uuid:
        errors.append("API response missing apiVersionUuid")
    elif file_uuid != api_uuid:
        errors.append(f"UUID mismatch: version.json={file_uuid}, API={api_uuid}")

    # Check git commit hash
    file_hash = version_data.get("gitCommitHash")
    api_hash = health_data.get("gitCommitHash")

    if file_hash and api_hash and file_hash != api_hash:
        errors.append(f"Git hash mismatch: version.json={file_hash}, API={api_hash}")

    # Check frontend compatibility
    file_compat = {
        "version": version_data.get("frontendCompatibilityVersion"),
        "minVersion": version_data.get("frontendMinVersion"),
        "maxVersion": version_data.get("frontendMaxVersion")
    }
    api_compat = health_data.get("frontendCompatibility", {})

    for key, file_value in file_compat.items():
        api_value = api_compat.get(key)
        if file_value and api_value and file_value != api_value:
            errors.append(f"Frontend {key} mismatch: version.json={file_value}, API={api_value}")

    if errors:
        return False, "; ".join(errors)

    return True, "All version information matches successfully"


def print_validation_results(success: bool, message: str, version_data: Dict[str, Any], health_data: Dict[str, Any]):
    """Print detailed validation results"""
    status_symbol = "✅" if success else "❌"
    print(f"\n{status_symbol} VERSION VALIDATION: {'PASSED' if success else 'FAILED'}")
    print(f"Details: {message}\n")

    if version_data:
        print("📄 version.json:")
        print(f"  UUID: {version_data.get('apiVersionUuid', 'MISSING')}")
        print(f"  Git Hash: {version_data.get('gitCommitHash', 'MISSING')}")
        print(f"  Frontend Compat: {version_data.get('frontendCompatibilityVersion', 'MISSING')}")
        print(f"  Created: {version_data.get('createdDate', 'MISSING')}")

    if health_data:
        print("\n🌐 API Response:")
        print(f"  UUID: {health_data.get('apiVersionUuid', 'MISSING')}")
        print(f"  Git Hash: {health_data.get('gitCommitHash', 'MISSING')}")
        frontend_compat = health_data.get('frontendCompatibility', {})
        print(f"  Frontend Compat: {frontend_compat.get('version', 'MISSING')}")
        print(f"  Timestamp: {health_data.get('timestamp', 'MISSING')}")

    print()


def main():
    """Main validation logic"""
    # Default API URL
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    print(f"🔍 Validating version consistency...")
    print(f"API URL: {api_url}")
    print(f"Working Directory: {os.getcwd()}")

    # Load version file
    version_data, version_error = load_version_file()
    if version_error:
        print(f"❌ ERROR: {version_error}")
        return 1

    # Query API health endpoint
    health_data, health_error = query_health_endpoint(api_url)
    if health_error:
        print(f"❌ ERROR: {health_error}")
        return 1

    # Validate consistency
    success, message = validate_version_consistency(version_data, health_data)

    # Print results
    print_validation_results(success, message, version_data, health_data)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())