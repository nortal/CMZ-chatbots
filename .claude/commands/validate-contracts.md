# Contract Validation Suite

**Purpose**: Validate three-way contract alignment between UI code, API implementation, and OpenAPI specification to detect incompatibilities before they cause runtime failures

**Usage**: `/validate-contracts [--endpoint path] [--fix] [--report-format json|markdown]`

## ⚠️ CRITICAL REQUIREMENTS

**This command validates the contract between three sources of truth:**
1. **OpenAPI Specification** - The absolute source of truth for API contracts
2. **API Implementation** - Backend handlers that process requests and return responses
3. **UI Code** - Frontend code that calls APIs and handles responses

**Goals:**
- Detect field name mismatches (camelCase vs snake_case)
- Find missing required fields
- Identify type mismatches (string vs number, etc.)
- Validate response structure alignment
- Check parameter location correctness (query vs body vs path)
- Verify error response format consistency

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically orchestrate contract validation:

### Phase 1: OpenAPI Specification Parsing

**Extract complete API contract:**

1. **Endpoint Discovery**
   ```bash
   # Parse OpenAPI spec for all endpoints
   cat backend/api/openapi_spec.yaml | yq eval '.paths | keys' -

   # For each endpoint, extract:
   # - HTTP method
   # - Path parameters
   # - Query parameters
   # - Request body schema
   # - Response schemas (200, 400, 500, etc.)
   # - Required vs optional fields
   # - Data types and formats
   ```

2. **Schema Registry Building**
   ```bash
   # Extract all schema definitions
   cat backend/api/openapi_spec.yaml | yq eval '.components.schemas' - > /tmp/openapi_schemas.yaml

   # Build field type mapping for each model:
   # User: {userId: string, email: string, role: string}
   # Family: {familyId: string, familyName: string, parentIds: array}
   # Animal: {animalId: string, name: string, species: string}
   ```

3. **Parameter Location Mapping**
   ```bash
   # For each endpoint, document WHERE parameters go:
   # GET /animal_config?animalId=X -> animalId is QUERY param
   # GET /animal/{animalId} -> animalId is PATH param
   # POST /animal with body -> Animal object is BODY param
   # Authorization: Bearer token -> JWT is HEADER param
   ```

4. **Required Fields Extraction**
   ```bash
   # Document which fields are required vs optional
   # This is CRITICAL for validation
   ```

**Output**: Complete contract specification with all endpoints, schemas, and requirements

### Phase 2: UI Code Analysis

**Scan frontend code for API calls:**

1. **API Call Discovery**
   ```bash
   # Find all fetch/axios calls in UI code
   grep -r "fetch\|axios\|\.get\|\.post\|\.put\|\.patch\|\.delete" \
     frontend/src --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
     > /tmp/ui_api_calls.txt

   # Extract endpoint URLs being called
   grep -oE "(fetch|axios)\(['\"]([^'\"]+)['\"]" /tmp/ui_api_calls.txt
   ```

2. **Request Payload Extraction**
   ```javascript
   // Example UI code patterns to find:

   // POST /family with body
   fetch('/family', {
     method: 'POST',
     body: JSON.stringify({
       familyName: "Test Family",  // ← UI sends familyName
       parentIds: ["parent1"],      // ← UI sends parentIds
       studentIds: ["student1"]     // ← UI sends studentIds
     })
   })

   // GET /animal_config with query params
   fetch(`/animal_config?animalId=${id}`)  // ← UI uses query param

   // PATCH with body
   fetch('/animal_config', {
     method: 'PATCH',
     body: JSON.stringify({
       temperature: 0.7  // ← UI sends temperature in body
     })
   })
   ```

3. **Response Handling Analysis**
   ```javascript
   // Find what fields UI expects in responses:

   fetch('/family')
     .then(res => res.json())
     .then(families => {
       // UI expects array of families
       families.forEach(family => {
         console.log(family.familyId)     // ← expects familyId
         console.log(family.familyName)   // ← expects familyName
         console.log(family.parents)      // ← expects parents array
       })
     })
   ```

4. **Field Name Inventory**
   ```bash
   # Extract all field names used in UI code
   # Look for patterns like:
   # - object.fieldName
   # - { fieldName: value }
   # - response.fieldName

   # Build UI field usage map:
   # POST /family uses: familyName, parentIds, studentIds
   # GET /animal_config uses: animalId (query), expects: temperature, aiModel, voice
   ```

**Output**: Complete inventory of UI API calls with request/response field usage

### Phase 3: API Implementation Analysis

**Parse backend handler implementations:**

1. **Handler Function Discovery**
   ```bash
   # Find all handler functions in impl/
   grep -r "def handle_\|def .*_get\|def .*_post\|def .*_put\|def .*_patch\|def .*_delete" \
     backend/api/src/main/python/openapi_server/impl/ \
     --include="*.py" > /tmp/api_handlers.txt
   ```

2. **Request Parameter Extraction**
   ```python
   # Example handler patterns to analyze:

   def handle_family_details_post(body: Any) -> Tuple[Any, int]:
       # Backend expects body parameter
       family_name = body.get('familyName')  # ← expects familyName
       parent_ids = body.get('parentIds')    # ← expects parentIds

   def handle_animal_config_get(*args, **kwargs) -> Tuple[Any, int]:
       # Backend extracts from query params
       animal_id = kwargs.get('animalId')  # ← expects animalId from query

   def handle_animal_id_put(id_=None, body=None, id=None, **kwargs):
       # Backend handles both id and id_ (Connexion issue)
       actual_id = id_ if id_ is not None else id
   ```

3. **Response Construction Analysis**
   ```python
   # Find what fields API returns:

   def handle_animal_config_get(...):
       return {
           'animalConfigId': config_id,  # ← API returns animalConfigId
           'temperature': 0.4,            # ← API returns temperature
           'aiModel': 'claude-3',         # ← API returns aiModel
           'voice': 'echo'                # ← API returns voice
       }, 200
   ```

4. **Validation Rules Check**
   ```python
   # Check what validation API does:
   # - Required field checks
   # - Type validation
   # - Range validation
   # - Enum validation
   ```

**Output**: Complete API handler inventory with parameter extraction and response building patterns

### Phase 4: Three-Way Contract Comparison

**Systematic mismatch detection:**

1. **Field Name Comparison**
   ```markdown
   ## Endpoint: POST /family

   | Source | Field Names |
   |--------|-------------|
   | OpenAPI | familyName, parentIds, studentIds |
   | UI Code | familyName, parentIds, studentIds |
   | API Impl | familyName, parentIds, studentIds |
   | **Status** | ✅ ALIGNED |

   ## Endpoint: GET /animal_config

   | Source | Query Param | Response Fields |
   |--------|-------------|-----------------|
   | OpenAPI | animalId | animalConfigId, temperature, aiModel |
   | UI Code | animalId | configId, temp, model | ← MISMATCH!
   | API Impl | animalId | animalConfigId, temperature, aiModel |
   | **Status** | ❌ MISALIGNED - UI uses wrong field names |
   ```

2. **Required Fields Validation**
   ```markdown
   ## Endpoint: POST /family

   | Field | OpenAPI | UI Sends | API Expects |
   |-------|---------|----------|-------------|
   | familyName | required | ✅ always | ✅ validates |
   | parentIds | required | ✅ always | ✅ validates |
   | studentIds | required | ⚠️ sometimes empty | ❌ rejects empty |
   | **Issue** | UI sends empty array, OpenAPI requires non-empty |
   ```

3. **Type Mismatch Detection**
   ```markdown
   ## Endpoint: PATCH /animal_config

   | Field | OpenAPI Type | UI Sends | API Expects |
   |-------|--------------|----------|-------------|
   | temperature | number (float 0-1) | string "0.7" | number 0.7 |
   | **Issue** | UI sends string, should send number |
   ```

4. **Parameter Location Validation**
   ```markdown
   ## Endpoint: PATCH /animal_config

   | Parameter | OpenAPI Location | UI Sends | API Expects |
   |-----------|------------------|----------|-------------|
   | animalId | query | ✅ query param | ✅ query param |
   | temperature | body | ✅ body | ✅ body |
   | **Status** | ✅ ALIGNED |

   ## Endpoint: PUT /animal/{animalId}

   | Parameter | OpenAPI Location | UI Sends | API Expects |
   |-----------|------------------|----------|-------------|
   | animalId | path | ✅ path | ✅ path (as id_) |
   | body | body | ✅ body | ✅ body |
   | **Status** | ⚠️ PARTIAL - Connexion renames id to id_ |
   ```

5. **Response Structure Comparison**
   ```markdown
   ## Endpoint: GET /family

   | Source | Response Structure |
   |--------|--------------------|
   | OpenAPI | Array of Family objects |
   | UI Code | Expects array, iterates with .forEach() |
   | API Impl | Returns array directly |
   | **Status** | ✅ ALIGNED |

   ## Endpoint: POST /auth

   | Source | Response Structure |
   |--------|--------------------|
   | OpenAPI | {token: string, user: {email, role}} |
   | UI Code | Expects response.token and response.user.email |
   | API Impl | Returns {token, user: {email, role, name}} |
   | **Status** | ⚠️ PARTIAL - API returns extra 'name' field (harmless) |
   ```

6. **Error Response Validation**
   ```markdown
   ## Error Response Format

   | Source | Error Structure |
   |--------|-----------------|
   | OpenAPI | {code: string, message: string, details: object} |
   | UI Code | Checks response.code and response.message |
   | API Impl | Returns {code, message, details} from Error model |
   | **Status** | ✅ ALIGNED |
   ```

**Output**: Complete mismatch report with severity ratings

### Phase 5: Automated Mismatch Detection

**Create automated validation script:**

```python
#!/usr/bin/env python3
"""
Contract Validation Script
Compares OpenAPI spec, UI code, and API implementation
"""

import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any

class ContractValidator:
    def __init__(self):
        self.openapi_spec = None
        self.ui_contracts = {}
        self.api_contracts = {}
        self.mismatches = []

    def parse_openapi(self, spec_path: str):
        """Parse OpenAPI specification"""
        with open(spec_path) as f:
            self.openapi_spec = yaml.safe_load(f)

        # Extract endpoint contracts
        for path, methods in self.openapi_spec['paths'].items():
            for method, details in methods.items():
                endpoint_key = f"{method.upper()} {path}"

                # Extract request schema
                request_schema = None
                if 'requestBody' in details:
                    request_schema = details['requestBody']['content']['application/json']['schema']

                # Extract response schema
                response_schema = None
                if '200' in details['responses']:
                    response_schema = details['responses']['200']['content']['application/json']['schema']

                # Extract parameters
                params = {
                    'query': [],
                    'path': [],
                    'header': []
                }
                if 'parameters' in details:
                    for param in details['parameters']:
                        params[param['in']].append({
                            'name': param['name'],
                            'required': param.get('required', False),
                            'type': param.get('schema', {}).get('type')
                        })

                self.openapi_spec[endpoint_key] = {
                    'request': request_schema,
                    'response': response_schema,
                    'parameters': params
                }

    def scan_ui_code(self, ui_dir: str):
        """Scan UI code for API calls"""
        ui_files = Path(ui_dir).rglob('*.{js,jsx,ts,tsx}')

        for file_path in ui_files:
            with open(file_path) as f:
                content = f.read()

            # Find fetch/axios calls
            # Pattern: fetch('/endpoint', {method: 'POST', body: JSON.stringify({...})})
            fetch_pattern = r"fetch\(['\"]([^'\"]+)['\"],?\s*({[^}]+})?"
            matches = re.findall(fetch_pattern, content)

            for endpoint, options in matches:
                # Extract request body fields
                body_pattern = r"JSON\.stringify\(({[^}]+})\)"
                body_match = re.search(body_pattern, options)
                if body_match:
                    # Parse field names from body
                    field_pattern = r"(\w+):"
                    fields = re.findall(field_pattern, body_match.group(1))
                    self.ui_contracts[endpoint] = {'request_fields': fields}

    def scan_api_handlers(self, impl_dir: str):
        """Scan API implementation handlers"""
        impl_files = Path(impl_dir).rglob('*.py')

        for file_path in impl_files:
            with open(file_path) as f:
                content = f.read()

            # Find handler functions
            # Pattern: def handle_xxx(body: Any) -> Tuple[Any, int]:
            handler_pattern = r"def (handle_\w+)\([^)]*\):"
            handlers = re.findall(handler_pattern, content)

            for handler in handlers:
                # Find body.get() calls to see what fields are accessed
                field_pattern = rf"{handler}.*?body\.get\(['\"](\w+)['\"]"
                fields = re.findall(field_pattern, content, re.DOTALL)
                self.api_contracts[handler] = {'request_fields': fields}

    def compare_contracts(self) -> List[Dict[str, Any]]:
        """Compare all three contract sources"""
        mismatches = []

        # For each endpoint in OpenAPI spec
        for endpoint, openapi_contract in self.openapi_spec.items():
            ui_contract = self.ui_contracts.get(endpoint, {})
            # Map endpoint to handler... (complex logic here)

            # Compare field names
            openapi_fields = set(openapi_contract.get('request_fields', []))
            ui_fields = set(ui_contract.get('request_fields', []))

            if openapi_fields != ui_fields:
                mismatches.append({
                    'endpoint': endpoint,
                    'type': 'field_mismatch',
                    'severity': 'high',
                    'openapi': list(openapi_fields),
                    'ui': list(ui_fields),
                    'missing_in_ui': list(openapi_fields - ui_fields),
                    'extra_in_ui': list(ui_fields - openapi_fields)
                })

        return mismatches

    def generate_report(self, output_format: str = 'markdown') -> str:
        """Generate mismatch report"""
        if output_format == 'json':
            return json.dumps(self.mismatches, indent=2)
        else:
            # Generate markdown report
            report = "# Contract Validation Report\n\n"

            if not self.mismatches:
                report += "✅ All contracts aligned! No mismatches detected.\n"
            else:
                report += f"❌ Found {len(self.mismatches)} mismatches\n\n"

                for mismatch in self.mismatches:
                    report += f"## {mismatch['endpoint']}\n"
                    report += f"**Type**: {mismatch['type']}\n"
                    report += f"**Severity**: {mismatch['severity']}\n\n"

                    if mismatch['type'] == 'field_mismatch':
                        report += f"- OpenAPI fields: {mismatch['openapi']}\n"
                        report += f"- UI fields: {mismatch['ui']}\n"
                        report += f"- Missing in UI: {mismatch['missing_in_ui']}\n"
                        report += f"- Extra in UI: {mismatch['extra_in_ui']}\n\n"

            return report

# Usage
if __name__ == '__main__':
    validator = ContractValidator()
    validator.parse_openapi('backend/api/openapi_spec.yaml')
    validator.scan_ui_code('frontend/src')
    validator.scan_api_handlers('backend/api/src/main/python/openapi_server/impl')
    mismatches = validator.compare_contracts()
    print(validator.generate_report())
```

### Phase 6: Handler Logic Validation

**Validate business logic validates structures correctly:**

1. **Check Handler Validation Code**
   ```bash
   # Scan handlers for validation logic
   grep -r "required\|validate\|isinstance\|get(" \
     backend/api/src/main/python/openapi_server/impl/ \
     --include="*.py" > /tmp/handler_validation.txt
   ```

2. **Verify Required Field Checks**
   ```python
   # Example handler patterns to find:

   # GOOD: Checks required fields
   def handle_family_post(body):
       if not body.get('familyName'):
           return error_response("familyName is required"), 400
       if not body.get('parentIds'):
           return error_response("parentIds is required"), 400

   # BAD: No validation, assumes fields exist
   def handle_family_post(body):
       family_name = body['familyName']  # ❌ May raise KeyError
   ```

3. **Check Type Validation**
   ```python
   # Look for type checking patterns:

   # GOOD: Validates types
   def handle_config_patch(body):
       temp = body.get('temperature')
       if temp is not None and not isinstance(temp, (int, float)):
           return error_response("temperature must be a number"), 400

   # BAD: No type checking
   def handle_config_patch(body):
       temp = body.get('temperature', 0.5)  # ❌ Could be string "0.5"
   ```

4. **Verify Response Structure Building**
   ```python
   # Check handlers build responses matching OpenAPI:

   # GOOD: Matches OpenAPI schema
   def handle_get_family(family_id):
       family = get_from_db(family_id)
       return {
           'familyId': family.id,      # ✅ Uses OpenAPI field name
           'familyName': family.name,  # ✅ Uses OpenAPI field name
           'parentIds': family.parents # ✅ Uses OpenAPI field name
       }, 200

   # BAD: Different field names than OpenAPI
   def handle_get_family(family_id):
       family = get_from_db(family_id)
       return {
           'id': family.id,           # ❌ OpenAPI says familyId
           'name': family.name,       # ❌ OpenAPI says familyName
           'parents': family.parents  # ❌ OpenAPI says parentIds
       }, 200
   ```

5. **Check Error Response Consistency**
   ```bash
   # Verify all handlers use Error model from OpenAPI
   grep -r "Error(" backend/api/src/main/python/openapi_server/impl/ \
     --include="*.py" | grep -v "import\|#"

   # Should see consistent usage:
   # Error(code="...", message="...", details={...})
   ```

**Output**: Handler validation report identifying missing validation logic

### Phase 7: Report Generation

**Generate comprehensive validation report:**

```markdown
# Contract Validation Report
**Date**: 2025-10-10
**Commit**: abc123def
**Endpoints Validated**: 37

## Executive Summary
- ✅ Aligned: 28/37 endpoints (76%)
- ⚠️ Partial: 6/37 endpoints (16%)
- ❌ Misaligned: 3/37 endpoints (8%)

## Handler Validation Issues
- ⚠️ Missing required field checks: 5 handlers
- ⚠️ No type validation: 8 handlers
- ❌ Response structure mismatches: 3 handlers
- ✅ Proper Error model usage: 25/37 handlers (68%)

## Critical Mismatches (Immediate Fix Required)

### 1. POST /family - studentIds Validation
**Severity**: HIGH
**Issue**: OpenAPI requires non-empty studentIds array, but UI sometimes sends empty array

| Source | Behavior |
|--------|----------|
| OpenAPI | Requires minItems: 1 for studentIds |
| UI Code | Sends [] when no students selected |
| API Impl | Validates and rejects empty array |

**Impact**: Family creation fails when no students added
**Fix**: Either remove minItems requirement OR update UI to require at least one student

### 2. GET /animal_config - Response Field Names
**Severity**: MEDIUM
**Issue**: UI expects different field names than API returns

| Field | OpenAPI | API Returns | UI Expects |
|-------|---------|-------------|------------|
| Config ID | animalConfigId | animalConfigId | configId |
| Model | aiModel | aiModel | model |
| Temperature | temperature | temperature | temp |

**Impact**: UI cannot read config values correctly
**Fix**: Update UI to use correct field names from OpenAPI spec

### 3. PATCH /animal_config - Type Mismatch
**Severity**: LOW
**Issue**: UI sends temperature as string, OpenAPI expects number

**Impact**: May cause validation errors or incorrect values
**Fix**: Update UI to send numeric values: `temperature: 0.7` not `temperature: "0.7"`

## Warnings (Review Recommended)

### 1. Parameter Location - Connexion id Renaming
**Endpoints**: PUT /animal/{id}, DELETE /animal/{id}
**Issue**: Connexion renames `id` parameter to `id_` to avoid Python builtin conflict

**Current Workaround**: API handlers accept both `id` and `id_` parameters
**Recommendation**: Use specific names in OpenAPI (animalId, familyId) instead of generic id

### 2. Extra Fields in Response
**Endpoint**: POST /auth
**Issue**: API returns extra `name` field not in OpenAPI spec

**Impact**: None (extra fields ignored by UI)
**Recommendation**: Update OpenAPI spec to document all returned fields

## Edge Cases Detected

### 1. Empty Array Handling
- GET /family returns `[]` when no families exist
- UI handles empty array correctly
- ✅ Compatible

### 2. Null vs Undefined
- OpenAPI defines some fields as nullable
- UI JavaScript treats null and undefined differently
- ⚠️ Potential issue: Check null handling in edge cases

### 3. Date Format
- OpenAPI specifies ISO 8601 format
- API uses datetime.utcnow().isoformat()
- UI uses new Date(value)
- ✅ Compatible

## Recommendations

1. **High Priority**:
   - Fix POST /family studentIds validation issue
   - Align GET /animal_config field names
   - Add contract validation to CI/CD pipeline

2. **Medium Priority**:
   - Rename generic `id` parameters to specific names
   - Update OpenAPI spec for all extra response fields
   - Add type checking to UI API calls (TypeScript)

3. **Low Priority**:
   - Document null handling conventions
   - Add integration tests for each endpoint
   - Consider API versioning strategy

## Incompatibilities That Remain After Static Validation

Even with perfect contract alignment, these runtime issues may still occur:

1. **Type Coercion**: JavaScript "0.7" coerced to 0.7 at runtime
2. **Validation Timing**: OpenAPI validates structure, business logic validates content
3. **Race Conditions**: Concurrent PATCH requests may conflict
4. **Size Limits**: Large payloads may exceed server limits
5. **Encoding**: Unicode/emoji handling differences
6. **Timezone**: Date interpretation differences
7. **Floating Point**: Rounding differences (0.1 + 0.2 ≠ 0.3)
8. **Array Ordering**: Order not guaranteed unless specified
9. **Case Sensitivity**: Email comparisons may be case-sensitive
10. **Whitespace**: Trimming behavior may differ
```

### Phase 8: Teams Notification

**Send contract validation results to Teams:**

1. **Read Teams Webhook Documentation**
   ```bash
   # Review Teams notification format requirements
   cat TEAMS-WEBHOOK-ADVICE.md

   # Key requirement: Must use Adaptive Card format, not plain text
   ```

2. **Generate Teams Notification Script**
   ```python
   #!/usr/bin/env python3
   """
   Send contract validation results to Teams
   Reads validation results and formats as Adaptive Card
   """
   import os
   import requests
   import json
   from datetime import datetime

   def send_contract_validation_to_teams(
       total_endpoints,
       aligned,
       partial,
       misaligned,
       handler_issues,
       critical_mismatches
   ):
       """Send contract validation results to Teams using Adaptive Card format"""

       webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
       if not webhook_url:
           print("⚠️ TEAMS_WEBHOOK_URL not set, skipping Teams notification")
           return

       # Determine overall status color
       if misaligned > 0:
           color = "Attention"  # Red
           status_emoji = "❌"
       elif partial > 5:
           color = "Warning"  # Yellow
           status_emoji = "⚠️"
       else:
           color = "Good"  # Green
           status_emoji = "✅"

       # Calculate success rate
       success_rate = round((aligned / total_endpoints) * 100) if total_endpoints > 0 else 0

       # Build adaptive card body
       body = [
           {
               "type": "TextBlock",
               "text": f"{status_emoji} Contract Validation Report",
               "size": "Large",
               "weight": "Bolder",
               "wrap": True,
               "color": color
           },
           {
               "type": "TextBlock",
               "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
               "size": "Small",
               "isSubtle": True,
               "wrap": True
           },
           {
               "type": "TextBlock",
               "text": "📊 Contract Alignment Summary",
               "size": "Medium",
               "weight": "Bolder",
               "wrap": True,
               "spacing": "Medium"
           },
           {
               "type": "FactSet",
               "facts": [
                   {"title": "Total Endpoints", "value": str(total_endpoints)},
                   {"title": "✅ Fully Aligned", "value": f"{aligned} ({round(aligned/total_endpoints*100)}%)"},
                   {"title": "⚠️ Partially Aligned", "value": f"{partial} ({round(partial/total_endpoints*100)}%)"},
                   {"title": "❌ Misaligned", "value": f"{misaligned} ({round(misaligned/total_endpoints*100)}%)"},
                   {"title": "Success Rate", "value": f"{success_rate}%"}
               ]
           },
           {
               "type": "TextBlock",
               "text": "🔍 Handler Validation Issues",
               "size": "Medium",
               "weight": "Bolder",
               "wrap": True,
               "spacing": "Medium"
           },
           {
               "type": "FactSet",
               "facts": [
                   {"title": "Missing Required Checks", "value": str(handler_issues.get('missing_required', 0))},
                   {"title": "No Type Validation", "value": str(handler_issues.get('no_type_validation', 0))},
                   {"title": "Response Mismatches", "value": str(handler_issues.get('response_mismatch', 0))},
                   {"title": "Proper Error Usage", "value": handler_issues.get('error_usage', 'Unknown')}
               ]
           }
       ]

       # Add critical mismatches section if any
       if critical_mismatches:
           body.append({
               "type": "TextBlock",
               "text": "🔴 Critical Issues",
               "size": "Medium",
               "weight": "Bolder",
               "wrap": True,
               "spacing": "Medium",
               "color": "Attention"
           })

           issues_text = "\n".join([f"• {issue}" for issue in critical_mismatches[:5]])
           body.append({
               "type": "TextBlock",
               "text": issues_text,
               "wrap": True,
               "spacing": "Small"
           })

       # Add recommendations
       body.append({
           "type": "TextBlock",
           "text": "💡 Recommendations",
           "size": "Medium",
           "weight": "Bolder",
           "wrap": True,
           "spacing": "Medium"
       })

       recommendations = []
       if misaligned > 0:
           recommendations.append("Fix misaligned endpoints immediately")
       if handler_issues.get('missing_required', 0) > 0:
           recommendations.append("Add required field validation to handlers")
       if handler_issues.get('no_type_validation', 0) > 0:
           recommendations.append("Implement type checking in handlers")
       if success_rate < 80:
           recommendations.append("Add contract validation to CI/CD pipeline")

       recs_text = "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
       body.append({
           "type": "TextBlock",
           "text": recs_text or "No critical recommendations",
           "wrap": True,
           "spacing": "Small"
       })

       # Create adaptive card
       card = {
           "type": "message",
           "attachments": [
               {
                   "contentType": "application/vnd.microsoft.card.adaptive",
                   "content": {
                       "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                       "type": "AdaptiveCard",
                       "version": "1.4",
                       "body": body
                   }
               }
           ]
       }

       # Send to Teams
       print("Sending contract validation report to Teams...")
       response = requests.post(
           webhook_url,
           json=card,
           headers={"Content-Type": "application/json"}
       )

       if response.status_code == 202:
           print("✅ Teams notification sent successfully")
           return 0
       else:
           print(f"❌ Failed to send Teams notification: {response.status_code}")
           print(response.text)
           return 1

   if __name__ == "__main__":
       # Example usage - replace with actual validation results
       send_contract_validation_to_teams(
           total_endpoints=37,
           aligned=28,
           partial=6,
           misaligned=3,
           handler_issues={
               'missing_required': 5,
               'no_type_validation': 8,
               'response_mismatch': 3,
               'error_usage': '25/37 (68%)'
           },
           critical_mismatches=[
               "POST /family - studentIds validation mismatch",
               "GET /animal_config - Response field names differ",
               "PATCH /animal_config - Type mismatch for temperature"
           ]
       )
   ```

3. **Integrate into Validation Script**
   ```bash
   # After validation completes, send to Teams
   python3 "$REPORT_DIR/send_to_teams.py"
   ```

**Output**: Adaptive Card notification sent to Teams channel with validation results

## Implementation

```bash
#!/bin/bash
# validate_contracts.sh

SESSION_ID="contract_val_$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="validation-reports/$SESSION_ID"
mkdir -p "$REPORT_DIR"

echo "=== Contract Validation Suite ==="
echo "Session: $SESSION_ID"

# Run Python validation script
python3 scripts/validate_contracts.py \
  --openapi backend/api/openapi_spec.yaml \
  --ui frontend/src \
  --api backend/api/src/main/python/openapi_server/impl \
  --output "$REPORT_DIR/contract_report.md" \
  --teams-script "$REPORT_DIR/send_to_teams.py"

echo "Report generated: $REPORT_DIR/contract_report.md"

# Send results to Teams
if [ -f "$REPORT_DIR/send_to_teams.py" ]; then
  echo "Sending results to Teams..."
  python3 "$REPORT_DIR/send_to_teams.py"
fi
```

## Command Options

**--endpoint**: Validate specific endpoint only
```bash
/validate-contracts --endpoint "POST /family"
```

**--fix**: Auto-generate fixes where possible
```bash
/validate-contracts --fix
# Creates fix_suggestions.md with code changes
```

**--report-format**: Output format (json or markdown)
```bash
/validate-contracts --report-format json > contracts.json
```

## Integration Points
- OpenAPI specification at `backend/api/openapi_spec.yaml`
- UI code in `frontend/src`
- API implementation in `backend/api/src/main/python/openapi_server/impl`
- Contract tests in `tests/contract/`

## Success Criteria
- [ ] All endpoints have OpenAPI definitions
- [ ] UI uses exact field names from OpenAPI
- [ ] API handlers match OpenAPI parameter locations
- [ ] Response structures align across all three layers
- [ ] No high-severity mismatches detected
- [ ] Contract validation passes in CI/CD

## References
- `VALIDATE-CONTRACTS-ADVICE.md` - Best practices and troubleshooting
- OpenAPI 3.0 Specification
- CMZ contract testing documentation
