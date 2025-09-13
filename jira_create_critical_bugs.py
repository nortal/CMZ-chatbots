#!/usr/bin/env python3
"""
Script to create critical bug tickets for CMZ integration issues
Based on validation findings from /validate-frontend-backend-integration
"""

import requests
import base64
import json
import os

# Load environment
JIRA_BASE = "https://nortal.atlassian.net"
JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'kc.stegbauer@nortal.com')
JIRA_TOKEN = os.getenv('JIRA_API_TOKEN')

if not JIRA_TOKEN:
    print("Error: JIRA_API_TOKEN not found in environment")
    print("Run: source .env.local")
    exit(1)

# Authentication
auth_string = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

def create_ticket(summary, description, priority="High", story_points=None):
    """Create a Jira ticket with required custom fields"""

    # Base ticket data - minimal required fields only
    ticket_data = {
        "fields": {
            "project": {"key": "PR003946"},
            "issuetype": {"name": "Bug"},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            },
            "priority": {"name": priority},
            # Required custom field that was causing previous failures
            "customfield_10225": {"value": "Billable"}  # Billable field
        }
    }

    url = f"{JIRA_BASE}/rest/api/3/issue"

    try:
        response = requests.post(url, headers=headers, json=ticket_data)

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created ticket: {result['key']}")
            print(f"   URL: {JIRA_BASE}/browse/{result['key']}")
            return result['key']
        else:
            print(f"❌ Failed to create ticket: {response.status_code}")
            print(f"   Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exception creating ticket: {e}")
        return None

def main():
    print("🎫 Creating Critical Bug Tickets for CMZ Integration Issues")
    print("=" * 60)

    # Ticket 1: API Schema Mapping Issue
    ticket1_summary = "CRITICAL: API Schema Validation Failures Block Frontend Integration"
    ticket1_description = """## Critical Issue
API endpoints fail with HTTP 500 errors due to field name mismatch between DynamoDB storage (snake_case) and OpenAPI specification (camelCase).

## Impact
- Complete frontend-backend integration failure
- All animal configuration functionality blocked after authentication
- User workflow broken at data retrieval step

## Technical Details
- **Error**: 'animalId' is a required property validation failure
- **Root Cause**: DynamoDB stores 'animal_id', OpenAPI expects 'animalId'
- **Affected Endpoints**: /animal_list, all entity data endpoints
- **Solution**: Implement field transformation in impl/utils/dynamo.py

## Reproduction Steps
1. Authenticate: curl -X POST http://localhost:8080/auth -H "Content-Type: application/json" -d '{"username":"test@cmz.org","password":"testpass123"}'
2. Extract JWT token from response
3. Request animal data: curl -H "Authorization: Bearer [TOKEN]" http://localhost:8080/animal_list
4. **Expected**: HTTP 200 with animal array
5. **Actual**: HTTP 500 with 'animalId' is a required property validation error

## Data Evidence
Confirmed real DynamoDB data retrieved successfully:
- animal_id: 'bella_002'
- name: 'Bella the Bear'
- species: 'Ursus americanus'
- status: 'active'

## Definition of Done
- All API endpoints return HTTP 200 responses
- Field names match OpenAPI specification requirements
- Frontend integration validation passes (/validate-frontend-backend-integration)
- No schema validation errors in API responses

## Files Affected
- backend/api/src/main/python/openapi_server/impl/utils/dynamo.py
- backend/api/src/main/python/openapi_server/impl/animals.py
- All entity implementation files in impl/ directory"""

    # Ticket 2: Root Endpoint Implementation Error
    ticket2_summary = "BUG: Root Endpoint Returns Debug String Instead of PublicHome Object"
    ticket2_description = """## Problem Description
Root endpoint (/) returns debug string 'do some magic!' instead of required PublicHome object structure, causing HTTP 500 validation errors.

## Impact
- Frontend cannot verify backend health status
- Root endpoint functionality completely broken
- API spec compliance violation

## Technical Details
- **Endpoint**: GET /
- **Expected Response**: PublicHome object with message/status fields
- **Actual Response**: String 'do some magic!' causing validation error
- **HTTP Status**: 500 Internal Server Error

## Reproduction Steps
1. Request root endpoint: curl http://localhost:8080/
2. **Expected**: HTTP 200 with {"message": "string", "status": "ok|maintenance"}
3. **Actual**: HTTP 500 with "'do some magic!' is not of type 'object'"

## Solution Requirements
1. Update root endpoint implementation to return proper PublicHome object
2. Ensure response matches OpenAPI specification schema
3. Return appropriate status ("ok" or "maintenance") and descriptive message

## Definition of Done
- Root endpoint returns HTTP 200 response
- Response structure matches OpenAPI PublicHome schema
- Frontend can successfully verify backend health status

## Files Affected
- Root endpoint controller implementation
- PublicHome response object structure"""

    print("\n1. Creating API Schema Mapping Bug Ticket...")
    ticket1_key = create_ticket(ticket1_summary, ticket1_description, priority="Highest", story_points=5)

    print("\n2. Creating Root Endpoint Bug Ticket...")
    ticket2_key = create_ticket(ticket2_summary, ticket2_description, priority="High", story_points=2)

    print("\n" + "=" * 60)
    print("🎫 Ticket Creation Summary:")
    if ticket1_key:
        print(f"✅ Schema Mapping Bug: {ticket1_key}")
    if ticket2_key:
        print(f"✅ Root Endpoint Bug: {ticket2_key}")

    print("\n📋 Next Steps:")
    print("1. Apply field mapping fixes in impl/utils/dynamo.py")
    print("2. Update root endpoint implementation")
    print("3. Re-run /validate-frontend-backend-integration")
    print("4. Verify frontend integration works end-to-end")

if __name__ == "__main__":
    main()