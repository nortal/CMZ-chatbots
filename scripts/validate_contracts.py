#!/usr/bin/env python3
"""
Contract Validation Script
Systematically validates three-way contract alignment between:
1. OpenAPI specification (source of truth)
2. UI code (frontend API usage)
3. API implementation (backend handlers)

Usage:
    python3 scripts/validate_contracts.py [--endpoint path] [--report-format json|markdown]
"""

import yaml
import json
import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from datetime import datetime
from collections import defaultdict

class ContractValidator:
    def __init__(self, openapi_path: str, ui_dir: str, api_dir: str):
        self.openapi_path = openapi_path
        self.ui_dir = ui_dir
        self.api_dir = api_dir

        self.openapi_spec = {}
        self.openapi_contracts = {}
        self.ui_contracts = defaultdict(dict)
        self.api_contracts = defaultdict(dict)
        self.mismatches = []

        # Statistics
        self.stats = {
            'total_endpoints': 0,
            'aligned': 0,
            'partial': 0,
            'misaligned': 0,
            'handler_issues': {
                'missing_required': 0,
                'no_type_validation': 0,
                'response_mismatch': 0,
                'proper_error_usage': 0
            }
        }

    def parse_openapi(self):
        """Parse OpenAPI specification and extract endpoint contracts"""
        print(f"📖 Parsing OpenAPI spec: {self.openapi_path}")

        with open(self.openapi_path) as f:
            self.openapi_spec = yaml.safe_load(f)

        # Extract endpoint contracts
        for path, methods in self.openapi_spec.get('paths', {}).items():
            for method, details in methods.items():
                if method == 'parameters':  # Skip path-level parameters
                    continue

                endpoint_key = f"{method.upper()} {path}"

                # Extract request schema
                request_fields = set()
                request_schema = None
                if 'requestBody' in details:
                    content = details['requestBody'].get('content', {})
                    if 'application/json' in content:
                        request_schema = content['application/json'].get('schema', {})
                        request_fields = self._extract_schema_fields(request_schema)

                # Extract response schema (200 response)
                response_fields = set()
                response_schema = None
                if '200' in details.get('responses', {}):
                    content = details['responses']['200'].get('content', {})
                    if 'application/json' in content:
                        response_schema = content['application/json'].get('schema', {})
                        response_fields = self._extract_schema_fields(response_schema)

                # Extract parameters
                params = {
                    'query': [],
                    'path': [],
                    'header': []
                }
                for param in details.get('parameters', []):
                    params[param['in']].append({
                        'name': param['name'],
                        'required': param.get('required', False),
                        'type': param.get('schema', {}).get('type')
                    })

                self.openapi_contracts[endpoint_key] = {
                    'request_fields': request_fields,
                    'response_fields': response_fields,
                    'request_schema': request_schema,
                    'response_schema': response_schema,
                    'parameters': params,
                    'operation_id': details.get('operationId', ''),
                    'tags': details.get('tags', [])
                }
                self.stats['total_endpoints'] += 1

        print(f"  Found {self.stats['total_endpoints']} endpoints")

    def _extract_schema_fields(self, schema: Dict[str, Any]) -> Set[str]:
        """Recursively extract field names from schema"""
        fields = set()

        if '$ref' in schema:
            # Resolve reference
            ref_path = schema['$ref'].split('/')
            if ref_path[0] == '#':
                # Internal reference
                component_path = ref_path[1:]  # Skip '#'
                resolved_schema = self.openapi_spec
                for part in component_path:
                    resolved_schema = resolved_schema.get(part, {})
                return self._extract_schema_fields(resolved_schema)

        if 'properties' in schema:
            fields.update(schema['properties'].keys())
            # Recursively extract from nested objects
            for prop_name, prop_schema in schema['properties'].items():
                if isinstance(prop_schema, dict) and 'properties' in prop_schema:
                    nested_fields = self._extract_schema_fields(prop_schema)
                    fields.update(f"{prop_name}.{nf}" for nf in nested_fields)

        if 'allOf' in schema:
            for sub_schema in schema['allOf']:
                fields.update(self._extract_schema_fields(sub_schema))

        if 'items' in schema:
            # Array type - extract fields from items
            fields.update(self._extract_schema_fields(schema['items']))

        return fields

    def scan_ui_code(self):
        """Scan UI code for API calls and field usage patterns"""
        print(f"🔍 Scanning UI code: {self.ui_dir}")

        ui_files = []
        for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
            ui_files.extend(Path(self.ui_dir).rglob(ext))

        print(f"  Found {len(ui_files)} UI files to scan")

        for file_path in ui_files:
            with open(file_path) as f:
                content = f.read()

            # Enhanced pattern to catch wrapper functions like apiRequest()
            # NOTE: Simplified patterns - don't try to capture options with regex
            # Instead, we'll search for options in the code after the match

            # Pattern 1: Direct fetch/axios calls
            pattern1 = r"(?:fetch|axios)\s*\(\s*['\"]([^'\"]+)['\"]"
            # Pattern 2: apiRequest wrapper calls
            pattern2 = r"apiRequest(?:<[^>]+>)?\s*\(\s*['\"]([^'\"]+)['\"]"
            # Pattern 3: API object method calls (authApi.login, etc.) - map to endpoints
            pattern3 = r"(authApi|animalApi|userApi|familyApi)\.(\w+)\s*\("

            # API object method to endpoint mapping
            api_method_to_endpoint = {
                'authApi.login': '/auth',
                'authApi.register': '/auth',
                'authApi.refresh': '/auth/refresh',
                'authApi.resetPassword': '/auth/reset_password',
                'animalApi.getAll': '/animal',
                'animalApi.getAnimalConfig': '/animal_config',
                'animalApi.saveAnimalConfig': '/animal_config',
                'userApi.getAll': '/user',
                'userApi.getById': '/user/{userId}',
                'userApi.update': '/user/{userId}',
                'familyApi.getAll': '/family',
                'familyApi.getById': '/family/{familyId}',
                'familyApi.create': '/family',
                'familyApi.update': '/family/{familyId}',
            }

            # Collect matches from all patterns with their type
            matches_with_type = []
            for match in re.finditer(pattern1, content):
                matches_with_type.append(('fetch', match))
            for match in re.finditer(pattern2, content):
                matches_with_type.append(('apiRequest', match))
            for match in re.finditer(pattern3, content):
                matches_with_type.append(('apiObject', match))

            for pattern_type, match in matches_with_type:
                # Extract endpoint based on pattern type
                if pattern_type == 'apiObject':
                    # For API object calls, map to endpoint
                    api_name = match.group(1)  # 'authApi', 'animalApi', etc.
                    method_name = match.group(2)  # 'login', 'getAll', etc.
                    key = f"{api_name}.{method_name}"
                    endpoint = api_method_to_endpoint.get(key)
                    if not endpoint:
                        # Skip unmapped API methods
                        continue
                    options = ""  # API object calls don't expose options directly
                else:
                    # For fetch and apiRequest patterns
                    endpoint = match.group(1)

                # Normalize endpoint path (remove localhost:port prefix)
                endpoint = re.sub(r'https?://[^/]+', '', endpoint)
                endpoint = re.sub(r':\d+', '', endpoint)  # Remove port

                # Look for options in the code after the match (next 2000 chars)
                pos = match.end()
                next_code = content[pos:pos+2000]

                # Determine HTTP method
                method_match = re.search(r"method:\s*['\"](\w+)['\"]", next_code)
                method = method_match.group(1).upper() if method_match else 'GET'

                endpoint_key = f"{method} {endpoint}"

                # Extract request body fields from JSON.stringify calls
                request_fields = set()
                # Look for body: JSON.stringify({...}) patterns
                body_pattern = r"body:\s*JSON\.stringify\(\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}"
                body_matches = re.finditer(body_pattern, next_code, re.DOTALL)
                for body_match in body_matches:
                    body_content = body_match.group(1)
                    # Find all field names in the body (word followed by colon)
                    field_pattern = r"(\w+)\s*:"
                    request_fields.update(re.findall(field_pattern, body_content))

                # Extract response field usage (look ahead in the code)
                response_fields = set()
                # Find .then(res => res.field) patterns after this fetch call
                pos = match.end()
                next_code = content[pos:pos+500]
                response_pattern = r"\.(?:then|data)\([^)]*(?:=>|function)[^{]*\{[^}]*\.(\w+)"
                response_fields = set(re.findall(response_pattern, next_code))

                if endpoint_key not in self.ui_contracts:
                    self.ui_contracts[endpoint_key] = {
                        'request_fields': request_fields,
                        'response_fields': response_fields,
                        'files': []
                    }
                else:
                    self.ui_contracts[endpoint_key]['request_fields'].update(request_fields)
                    self.ui_contracts[endpoint_key]['response_fields'].update(response_fields)

                self.ui_contracts[endpoint_key]['files'].append(str(file_path))

        print(f"  Found {len(self.ui_contracts)} unique API calls")

    def scan_api_handlers(self):
        """Scan API implementation handlers for parameter extraction"""
        print(f"🔧 Scanning API handlers: {self.api_dir}")

        # CRITICAL FIX: Also scan handlers.py which contains actual implementations
        impl_files = list(Path(self.api_dir).rglob('*.py'))

        # Add handlers.py explicitly if it exists
        handlers_file = Path(self.api_dir) / 'handlers.py'
        if handlers_file.exists() and handlers_file not in impl_files:
            impl_files.append(handlers_file)

        print(f"  Found {len(impl_files)} implementation files (including handlers.py)")

        for file_path in impl_files:
            with open(file_path) as f:
                content = f.read()

            # Find handler functions - handle both handle_* and other function patterns
            # Pattern: def handle_xxx(body: Any) -> Tuple[Any, int]:
            handler_patterns = [
                r"def (handle_\w+)\s*\([^)]*\)\s*(?:->[\w\[\], ]+)?:",
                r"def (\w+_post|\w+_get|\w+_put|\w+_patch|\w+_delete)\s*\([^)]*\)\s*(?:->[\w\[\], ]+)?:",
            ]

            handlers = []
            for pattern in handler_patterns:
                handlers.extend(re.finditer(pattern, content))

            for handler_match in handlers:
                handler_name = handler_match.group(1)

                # Extract function body (simplified - up to next def or end of file)
                func_start = handler_match.end()
                next_def = re.search(r"\ndef ", content[func_start:])
                func_end = func_start + next_def.start() if next_def else len(content)
                func_body = content[func_start:func_end]

                # Find body.get() calls to see what fields are accessed
                request_fields = set(re.findall(r"body\.get\(['\"](\w+)['\"]", func_body))
                request_fields.update(re.findall(r"body\[['\"](\w+)['\"]\]", func_body))

                # Find response fields (fields being set in return dictionaries)
                response_pattern = r"['\"](\w+)['\"]:\s*(?:\w+|['\"][^'\"]*['\"])"
                response_fields = set(re.findall(response_pattern, func_body))

                # Check for required field validation
                has_required_checks = bool(re.search(r"if not.*\.get\(|raise.*required", func_body))

                # Check for type validation
                has_type_validation = bool(re.search(r"isinstance\(|type\(", func_body))

                # Check for Error model usage
                uses_error_model = bool(re.search(r"Error\(code=|error_response\(", func_body))

                self.api_contracts[handler_name] = {
                    'request_fields': request_fields,
                    'response_fields': response_fields,
                    'has_required_checks': has_required_checks,
                    'has_type_validation': has_type_validation,
                    'uses_error_model': uses_error_model,
                    'file': str(file_path)
                }

                # Update handler validation stats
                if not has_required_checks:
                    self.stats['handler_issues']['missing_required'] += 1
                if not has_type_validation:
                    self.stats['handler_issues']['no_type_validation'] += 1
                if uses_error_model:
                    self.stats['handler_issues']['proper_error_usage'] += 1

        print(f"  Found {len(self.api_contracts)} handler functions")

    def _camel_to_snake(self, camel_str: str) -> str:
        """Convert camelCase to snake_case"""
        # Insert underscore before uppercase letters and convert to lowercase
        import re
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake

    def compare_contracts(self):
        """Perform three-way contract comparison and detect mismatches"""
        print(f"🔄 Comparing contracts across all three layers...")

        # Compare each endpoint defined in OpenAPI spec
        for endpoint_key, openapi_contract in self.openapi_contracts.items():
            ui_contract = self.ui_contracts.get(endpoint_key, {})

            # Try to find corresponding handler
            # OpenAPI uses camelCase (authPost) but Python uses snake_case (auth_post)
            operation_id = openapi_contract.get('operation_id', '')
            handler_name = None
            api_contract = {}

            if operation_id:
                # Try snake_case version first
                snake_operation_id = self._camel_to_snake(operation_id)
                handler_name = f"handle_{snake_operation_id}"
                api_contract = self.api_contracts.get(handler_name, {})

                # Fall back to camelCase if snake_case not found
                if not api_contract:
                    handler_name = f"handle_{operation_id}"
                    api_contract = self.api_contracts.get(handler_name, {})

            # Compare request fields
            openapi_req = openapi_contract['request_fields']
            ui_req = ui_contract.get('request_fields', set())
            api_req = api_contract.get('request_fields', set())

            if openapi_req or ui_req or api_req:
                if openapi_req == ui_req == api_req:
                    self.stats['aligned'] += 1
                elif openapi_req == ui_req or openapi_req == api_req:
                    self.stats['partial'] += 1
                    self.mismatches.append({
                        'endpoint': endpoint_key,
                        'type': 'partial_field_mismatch',
                        'severity': 'medium',
                        'layer': 'request',
                        'openapi': list(openapi_req),
                        'ui': list(ui_req),
                        'api': list(api_req),
                        'missing_in_ui': list(openapi_req - ui_req),
                        'extra_in_ui': list(ui_req - openapi_req),
                        'missing_in_api': list(openapi_req - api_req),
                        'extra_in_api': list(api_req - openapi_req)
                    })
                else:
                    self.stats['misaligned'] += 1
                    self.mismatches.append({
                        'endpoint': endpoint_key,
                        'type': 'field_mismatch',
                        'severity': 'high',
                        'layer': 'request',
                        'openapi': list(openapi_req),
                        'ui': list(ui_req),
                        'api': list(api_req),
                        'missing_in_ui': list(openapi_req - ui_req),
                        'extra_in_ui': list(ui_req - openapi_req),
                        'missing_in_api': list(openapi_req - api_req),
                        'extra_in_api': list(api_req - openapi_req)
                    })

            # Compare response fields
            openapi_resp = openapi_contract['response_fields']
            ui_resp = ui_contract.get('response_fields', set())
            api_resp = api_contract.get('response_fields', set())

            if openapi_resp != ui_resp and (openapi_resp or ui_resp):
                self.mismatches.append({
                    'endpoint': endpoint_key,
                    'type': 'response_field_mismatch',
                    'severity': 'medium',
                    'layer': 'response',
                    'openapi': list(openapi_resp),
                    'ui': list(ui_resp),
                    'api': list(api_resp),
                    'missing_in_ui': list(openapi_resp - ui_resp),
                    'extra_in_ui': list(ui_resp - openapi_resp)
                })
                self.stats['handler_issues']['response_mismatch'] += 1

        print(f"  Found {len(self.mismatches)} contract mismatches")
        print(f"  Alignment: {self.stats['aligned']} aligned, {self.stats['partial']} partial, {self.stats['misaligned']} misaligned")

    def generate_report(self, format: str = 'markdown') -> str:
        """Generate comprehensive validation report"""
        print(f"📝 Generating {format} report...")

        if format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_markdown_report()

    def _generate_markdown_report(self) -> str:
        """Generate markdown format report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Calculate success rate
        total = self.stats['total_endpoints']
        success_rate = round((self.stats['aligned'] / total) * 100) if total > 0 else 0

        report = f"""# Contract Validation Report
**Date**: {timestamp}
**Endpoints Validated**: {total}

## Executive Summary
- ✅ Aligned: {self.stats['aligned']}/{total} endpoints ({round(self.stats['aligned']/total*100) if total > 0 else 0}%)
- ⚠️ Partial: {self.stats['partial']}/{total} endpoints ({round(self.stats['partial']/total*100) if total > 0 else 0}%)
- ❌ Misaligned: {self.stats['misaligned']}/{total} endpoints ({round(self.stats['misaligned']/total*100) if total > 0 else 0}%)

## Handler Validation Issues
- ⚠️ Missing required field checks: {self.stats['handler_issues']['missing_required']} handlers
- ⚠️ No type validation: {self.stats['handler_issues']['no_type_validation']} handlers
- ❌ Response structure mismatches: {self.stats['handler_issues']['response_mismatch']} handlers
- ✅ Proper Error model usage: {self.stats['handler_issues']['proper_error_usage']} handlers

"""

        # Group mismatches by severity
        critical = [m for m in self.mismatches if m['severity'] == 'high']
        warnings = [m for m in self.mismatches if m['severity'] == 'medium']

        if critical:
            report += f"## Critical Mismatches ({len(critical)} issues)\n\n"
            for idx, mismatch in enumerate(critical[:10], 1):  # Limit to top 10
                report += f"### {idx}. {mismatch['endpoint']} - {mismatch['type']}\n"
                report += f"**Layer**: {mismatch['layer']}\n\n"
                report += f"| Source | Fields |\n"
                report += f"|--------|--------|\n"
                report += f"| OpenAPI | {', '.join(mismatch.get('openapi', [])) or 'none'} |\n"
                report += f"| UI Code | {', '.join(mismatch.get('ui', [])) or 'none'} |\n"
                report += f"| API Impl | {', '.join(mismatch.get('api', [])) or 'none'} |\n\n"

                if mismatch.get('missing_in_ui'):
                    report += f"**Missing in UI**: {', '.join(mismatch['missing_in_ui'])}\n"
                if mismatch.get('extra_in_ui'):
                    report += f"**Extra in UI**: {', '.join(mismatch['extra_in_ui'])}\n"
                report += "\n"

        if warnings:
            report += f"## Warnings ({len(warnings)} issues)\n\n"
            for idx, mismatch in enumerate(warnings[:10], 1):  # Limit to top 10
                report += f"### {idx}. {mismatch['endpoint']} - {mismatch['type']}\n"
                report += f"**Severity**: {mismatch['severity']}\n\n"

        # Recommendations
        report += "## Recommendations\n\n"
        report += "### High Priority\n"
        if self.stats['misaligned'] > 0:
            report += f"- Fix {self.stats['misaligned']} misaligned endpoints immediately\n"
        if self.stats['handler_issues']['missing_required'] > 5:
            report += f"- Add required field validation to {self.stats['handler_issues']['missing_required']} handlers\n"
        if success_rate < 80:
            report += "- Add contract validation to CI/CD pipeline\n"

        report += "\n### Medium Priority\n"
        if self.stats['partial'] > 0:
            report += f"- Review {self.stats['partial']} partially aligned endpoints\n"
        if self.stats['handler_issues']['no_type_validation'] > 10:
            report += f"- Implement type checking in {self.stats['handler_issues']['no_type_validation']} handlers\n"

        report += "\n### Low Priority\n"
        report += "- Document null handling conventions\n"
        report += "- Add integration tests for each endpoint\n"
        report += "- Consider API versioning strategy\n"

        return report

    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        return json.dumps({
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'mismatches': self.mismatches
        }, indent=2)

    def get_teams_notification_data(self) -> Dict[str, Any]:
        """Prepare data for Teams notification"""
        total = self.stats['total_endpoints']
        critical_mismatches = [
            f"{m['endpoint']} - {m['type']}"
            for m in self.mismatches if m['severity'] == 'high'
        ][:5]  # Top 5 critical issues

        return {
            'total_endpoints': total,
            'aligned': self.stats['aligned'],
            'partial': self.stats['partial'],
            'misaligned': self.stats['misaligned'],
            'handler_issues': self.stats['handler_issues'],
            'critical_mismatches': critical_mismatches
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate API contract alignment')
    parser.add_argument('--openapi', default='backend/api/openapi_spec.yaml',
                        help='Path to OpenAPI specification')
    parser.add_argument('--ui', default='frontend/src',
                        help='Path to UI source directory')
    parser.add_argument('--api', default='backend/api/src/main/python/openapi_server/impl',
                        help='Path to API implementation directory')
    parser.add_argument('--output', default=None,
                        help='Output file path (default: stdout)')
    parser.add_argument('--report-format', choices=['markdown', 'json'], default='markdown',
                        help='Report format')
    parser.add_argument('--endpoint', default=None,
                        help='Validate specific endpoint only')

    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent
    openapi_path = repo_root / args.openapi
    ui_dir = repo_root / args.ui
    api_dir = repo_root / args.api

    validator = ContractValidator(str(openapi_path), str(ui_dir), str(api_dir))

    # Run validation
    validator.parse_openapi()
    validator.scan_ui_code()
    validator.scan_api_handlers()
    validator.compare_contracts()

    # Generate report
    report = validator.generate_report(args.report_format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✅ Report written to: {args.output}")
    else:
        print("\n" + report)

    # Generate Teams notification data for separate script
    teams_data = validator.get_teams_notification_data()
    teams_data_path = repo_root / 'validation-reports' / 'teams_notification_data.json'
    teams_data_path.parent.mkdir(exist_ok=True)
    with open(teams_data_path, 'w') as f:
        json.dump(teams_data, f, indent=2)

    print(f"✅ Teams notification data: {teams_data_path}")

    # Return exit code based on results
    if validator.stats['misaligned'] > 0:
        return 1  # Critical issues found
    elif validator.stats['partial'] > 5:
        return 1  # Too many warnings
    else:
        return 0  # Success


if __name__ == '__main__':
    sys.exit(main())
