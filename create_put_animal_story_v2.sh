#!/bin/bash

# Jira REST API script to create PUT /animal/{id} endpoint story
# Based on working pattern from create_environment_config_tickets.sh

# Load environment variables
if [ -f .env.local ]; then
    source .env.local
fi

# Validate required environment variables
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Error: Missing JIRA_EMAIL or JIRA_API_TOKEN in .env.local"
    exit 1
fi

# Jira configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
PROJECT_KEY="PR003946"
JIRA_CREDENTIALS=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

echo "🚀 Creating Jira Task for PUT /animal/{id} endpoint implementation..."

# Test API connectivity first
echo "🔌 Testing API connectivity..."
test_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic $JIRA_CREDENTIALS" \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/myself")

test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)

if [ "$test_http_status" != "200" ]; then
    echo "❌ API connectivity test failed (HTTP $test_http_status)"
    echo "Please check your JIRA_EMAIL and JIRA_API_TOKEN environment variables"
    exit 1
fi

echo "✅ API connectivity confirmed"

# Create the story JSON payload
cat > /tmp/jira_story_payload.json <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "Implement PUT /animal/{id} Endpoint for Animal Management",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Story: Enable Admin and Zookeeper Animal Information Updates"}]
        },
        {
          "type": "paragraph",
          "content": [
            {"type": "text", "text": "As an administrator or zookeeper, I want to update animal information (name, species, and status) through the API so that I can maintain accurate animal records without needing direct database access."}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Background"}]
        },
        {
          "type": "paragraph",
          "content": [
            {"type": "text", "text": "The Animal Config dialog in the frontend attempts to update both Animal basic information (name, species, status) and Animal Configuration (personality, AI settings) when saving. Currently, the PUT /animal/{id} endpoint is not implemented, causing animal name and species updates to fail with a 500 error."}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Technical Context"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Current State: Endpoint defined in OpenAPI spec but returns 501 Not Implemented"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Code Generation Issue: Generated controller has malformed function signature (missing comma)"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Database: DynamoDB table quest-dev-animal with animalId as primary key"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Frontend Integration: Frontend already calls this endpoint via updateAnimal() function"}]}
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Field Specifications"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "name: string, 1-100 characters, optional for partial updates"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "species: string, 1-100 characters, optional for partial updates"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "status: enum ['active', 'hidden'], optional for partial updates"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "animalId: IMMUTABLE, cannot be changed via PUT"}
                ]}
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC1: Endpoint updates only provided fields and returns 200 with updated Animal object"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC2: Field validation returns 422 for invalid data (empty strings, >100 chars)"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC3: Supports partial updates (can update single field)"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC4: AnimalId remains immutable (path parameter used, body field ignored)"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC5: Returns 404 for non-existent animals"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC6: Updates audit trail (modified.at timestamp)"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC7: Validates status enum values"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC8: Integrates with Animal Config dialog (values persist after save)"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC9: Handles concurrent updates without data corruption"}
                ]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [
                  {"type": "text", "text": "AC10: Empty request body returns 200 with unchanged data (no-op)"}
                ]}
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Implementation Notes"}]
        },
        {
          "type": "paragraph",
          "content": [
            {"type": "text", "text": "1. Fix controller signature: def animal_id_put(id, animal_update)\n"},
            {"type": "text", "text": "2. Implement in /backend/api/src/main/python/openapi_server/impl/animals.py\n"},
            {"type": "text", "text": "3. Use existing DynamoDB utilities from impl/utils/dynamo.py\n"},
            {"type": "text", "text": "4. Test with existing animal: leo_001\n"},
            {"type": "text", "text": "5. Story Points: 5 (1 fix + 2 implement + 1 test + 1 integration)"}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Definition of Done"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Endpoint implementation complete"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "All acceptance criteria pass"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Unit tests achieve >90% coverage"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Frontend Animal Config dialog successfully updates"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Code reviewed and approved"}]}
              ]
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["api", "backend", "persistence", "animal-management", "crud"],
    "customfield_10225": {
      "value": "Billable",
      "id": "10564"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF

# Create the story
echo "📝 Sending request to Jira API..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -H "Authorization: Basic ${JIRA_CREDENTIALS}" \
  -H "Content-Type: application/json" \
  -d @/tmp/jira_story_payload.json \
  "${JIRA_BASE_URL}/rest/api/3/issue")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS:")

# Check if creation was successful
if [ "$HTTP_STATUS" = "201" ]; then
    STORY_KEY=$(echo "$RESPONSE_BODY" | jq -r '.key')
    STORY_ID=$(echo "$RESPONSE_BODY" | jq -r '.id')
    echo "✅ Successfully created Jira task: ${STORY_KEY}"
    echo "📍 Task ID: ${STORY_ID}"
    echo "🔗 View task: ${JIRA_BASE_URL}/browse/${STORY_KEY}"

    # Save the key for reference
    echo "${STORY_KEY}" > /tmp/last_created_story.txt

    # Clean up
    rm -f /tmp/jira_story_payload.json

    echo "✨ Task creation complete!"
    echo ""
    echo "📋 Summary:"
    echo "   - Implement PUT /animal/{id} endpoint"
    echo "   - Fix code generation issue"
    echo "   - Enable Animal Name and Species updates"
    echo "   - Story Points: 5"
    echo "   - Priority: High"
    echo "   - Billable: Yes"
else
    echo "❌ Failed to create task (HTTP ${HTTP_STATUS})"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
    rm -f /tmp/jira_story_payload.json
    exit 1
fi