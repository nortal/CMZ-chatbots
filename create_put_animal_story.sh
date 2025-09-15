#!/bin/bash

# Jira REST API script to create PUT /animal/{id} endpoint story
# This script creates a new story in the CMZ project for implementing the animal update endpoint

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
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

echo "🚀 Creating Jira Story for PUT /animal/{id} endpoint implementation..."

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
                {"type": "paragraph", "content": [{"type": "text", "text": "Code Generation Issue: Generated controller has malformed function signature"}]}
              ]
            },
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Database: DynamoDB table quest-dev-animal with animalId as primary key"}]}
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
            {"type": "text", "text": "4. Test with existing animal: leo_001"}
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
      "name": "Story"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["api", "backend", "persistence", "animal-management", "crud"]
  }
}
EOF

# Create the story
echo "📝 Sending request to Jira API..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Basic ${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  -d @/tmp/jira_story_payload.json \
  "${JIRA_BASE_URL}/rest/api/3/issue")

# Check if creation was successful
if echo "$RESPONSE" | grep -q '"key"'; then
    STORY_KEY=$(echo "$RESPONSE" | jq -r '.key')
    STORY_ID=$(echo "$RESPONSE" | jq -r '.id')
    echo "✅ Successfully created Jira story: ${STORY_KEY}"
    echo "📍 Story ID: ${STORY_ID}"
    echo "🔗 View story: ${JIRA_BASE_URL}/browse/${STORY_KEY}"

    # Save the key for reference
    echo "${STORY_KEY}" > /tmp/last_created_story.txt

    # Add acceptance criteria field if needed (some Jira configs have separate AC field)
    echo "📋 Adding detailed acceptance criteria..."

    # Clean up
    rm -f /tmp/jira_story_payload.json

    echo "✨ Story creation complete!"
else
    echo "❌ Failed to create story. Response:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi