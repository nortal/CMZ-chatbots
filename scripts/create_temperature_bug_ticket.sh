#!/bin/bash

# Create Jira ticket for Temperature Controller Bug
# This script creates a bug ticket in the CMZ project for the temperature validation issue

# Load environment variables
if [ -f .env.local ]; then
    source .env.local
fi

# Jira configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
JIRA_EMAIL="${JIRA_EMAIL:-kc.stegbauer@nortal.com}"
PROJECT_KEY="PR003946"

# Validate required environment variables
if [ -z "${JIRA_API_TOKEN}" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    echo "Please set JIRA_API_TOKEN or create a .env.local file with this variable"
    exit 1
fi

# Create Basic Auth header securely
# Use printf instead of echo for better compatibility and security
AUTH_HEADER=$(printf '%s:%s' "${JIRA_EMAIL}" "${JIRA_API_TOKEN}" | base64)

# Create the ticket JSON payload
cat > /tmp/temperature_bug_ticket.json << 'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "Bug: Temperature Controller Validation Error - \"0.7 is not a multiple of 0.1\"",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Problem Statement"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "The temperature controller in Animal Management → Chatbot Personalities → Settings incorrectly validates temperature values, showing error \"Error saving: 0.7 is not a multiple of 0.1 - 'temperature'\" when saving valid temperature values like 0.7."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Business Impact"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Users cannot save valid temperature configurations"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Blocks configuration of AI model parameters"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Frustrating UX with mathematically incorrect errors"}]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Steps to Reproduce"}]
        },
        {
          "type": "orderedList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Login as admin@cmz.org"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Navigate to Animal Management → Chatbot Personalities"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Select any animal and open Settings tab"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Set Temperature to 0.7"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "Click Save - observe error"}]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Root Cause"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Floating-point precision error in validation logic. In JavaScript, 0.7 * 10 = 6.999999999999999 due to IEEE 754 representation."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "✅ All values 0.0-2.0 in 0.1 increments accepted"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "✅ Value 0.7 specifically validated and saved correctly"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "✅ No false validation errors for valid multiples of 0.1"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "✅ Values persist correctly to DynamoDB"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "✅ Unit tests cover all edge cases"}]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Testing Checklist"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Test all values: 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, "
            },
            {
              "type": "text",
              "text": "0.7 (CRITICAL)",
              "marks": [{"type": "strong"}]
            },
            {
              "type": "text",
              "text": ", 0.8, 0.9, 1.0, 1.5, 2.0"
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Related Files"}]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "frontend/src/pages/AnimalConfig.tsx"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "frontend/src/hooks/useSecureFormHandling.ts"}]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{"type": "text", "text": "backend/api/openapi_spec.yaml (temperature definition)"}]
                }
              ]
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Bug"
    },
    "priority": {
      "name": "High"
    },
    "labels": [
      "bug",
      "validation",
      "floating-point",
      "animal-config",
      "user-experience"
    ],
    "customfield_10225": {
      "value": "Billable",
      "id": "10564"
    }
  }
}
EOF

# Create the ticket
echo "Creating Jira ticket for Temperature Controller Bug..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Basic ${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d @/tmp/temperature_bug_ticket.json \
  "${JIRA_BASE_URL}/rest/api/3/issue")

# Check if successful
if echo "${RESPONSE}" | grep -q '"key"'; then
    TICKET_KEY=$(echo "${RESPONSE}" | grep -o '"key":"[^"]*' | cut -d'"' -f4)
    TICKET_ID=$(echo "${RESPONSE}" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

    echo "✅ Successfully created ticket: ${TICKET_KEY}"
    echo "📋 Ticket URL: ${JIRA_BASE_URL}/browse/${TICKET_KEY}"

    # Save ticket info
    echo "${TICKET_KEY}" > /tmp/temperature_bug_ticket_key.txt
    echo "${RESPONSE}" > /tmp/temperature_bug_ticket_response.json

    # Add additional details as comment
    cat > /tmp/temperature_bug_comment.json << 'COMMENT_EOF'
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "Recommended Fix"}]
      },
      {
        "type": "codeBlock",
        "attrs": {"language": "javascript"},
        "content": [
          {
            "type": "text",
            "text": "// Solution: Use epsilon comparison or proper rounding\nconst validateTemperature = (value) => {\n  const rounded = Math.round(value * 10) / 10;\n  return rounded >= 0 && rounded <= 2.0 && rounded === value;\n};"
          }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This issue affects all temperature validations and should be fixed in both frontend and backend validation logic."
          }
        ]
      }
    ]
  }
}
COMMENT_EOF

    # Add comment with fix details
    curl -s -X POST \
      -H "Authorization: Basic ${AUTH_HEADER}" \
      -H "Content-Type: application/json" \
      -d @/tmp/temperature_bug_comment.json \
      "${JIRA_BASE_URL}/rest/api/3/issue/${TICKET_KEY}/comment" > /dev/null

    echo "📝 Added implementation details to ticket"

else
    echo "❌ Failed to create ticket. Response:"
    echo "${RESPONSE}" | jq '.' || echo "${RESPONSE}"
fi

# Cleanup
rm -f /tmp/temperature_bug_ticket.json /tmp/temperature_bug_comment.json