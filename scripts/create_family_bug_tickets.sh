#!/bin/bash

# Create Jira tickets for Family Groups bugs
set -e

# Source credentials from .env.local
if [ -f .env.local ]; then
    export $(grep -v '^#' .env.local | xargs)
fi

# Check required environment variables
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_EMAIL and JIRA_API_TOKEN must be set in .env.local"
    exit 1
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)
PROJECT_KEY="PR003946"

echo "=================================================="
echo "Creating Jira tickets for Family Groups bugs"
echo "=================================================="
echo ""

# Ticket 1: Add New Family button
echo "Creating ticket for 'Add New Family' button issue..."

TICKET1_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "Family Groups - Add New Family button not working",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Issue Description"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "The 'Add New Family' button in the Family Groups > Manage Families section is not functioning. When clicked, no action occurs and the new family form/dialog does not appear."
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
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to the CMZ application frontend (http://localhost:3001)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Login with valid credentials (e.g., parent1@test.cmz.org / testpass123)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to 'Family Groups' section from the main navigation"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click on 'Manage Families' subsection"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Locate and click the 'Add New Family' button"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Observe that nothing happens - no form, modal, or new page appears"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Expected Behavior"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Clicking 'Add New Family' button should open a form or modal dialog"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The form should allow entering: Family name, Primary contact information, Student members, Parent/guardian information"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "User should be able to save the new family"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "After saving, the new family should appear in the families list"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Actual Behavior"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Button click produces no visible response"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "No form or modal appears"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Button may lack proper onClick handler or routing"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Clicking 'Add New Family' button opens a form/modal"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Form includes all required fields with proper validation"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Form submission calls POST /family endpoint"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Successful creation shows in families list immediately"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Proper error handling and loading states"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Technical Context"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Frontend: React/TypeScript with Vite | API endpoints: POST /family, GET /family_list | Component: frontend/src/components/FamilyManagement/"
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
    "labels": ["family-management", "frontend", "bug", "ui-interaction"],
    "customfield_10225": {
      "value": "Billable"
    }
  }
}
EOF
)

RESPONSE1=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET1_BODY")

TICKET1_KEY=$(echo "$RESPONSE1" | jq -r '.key')
if [ "$TICKET1_KEY" != "null" ] && [ -n "$TICKET1_KEY" ]; then
    echo "✅ Created ticket: $TICKET1_KEY - Add New Family button issue"
    echo "   URL: https://nortal.atlassian.net/browse/$TICKET1_KEY"
else
    echo "❌ Failed to create ticket 1"
    echo "   Response: $RESPONSE1"
fi

echo ""

# Ticket 2: Edit Family Details button
echo "Creating ticket for 'Edit Family Details' button issue..."

TICKET2_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "Family Groups - Edit Family Details button not working",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Issue Description"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "The 'Edit Family Details' button in the Family Groups > Manage Families > View Details section is not functioning. When clicked, the edit form/mode does not activate."
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
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to the CMZ application frontend (http://localhost:3001)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Login with valid credentials (e.g., parent1@test.cmz.org / testpass123)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to 'Family Groups' section from the main navigation"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click on 'Manage Families' subsection"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click 'View Details' on any existing family"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click the 'Edit Family Details' button"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Observe that the form does not become editable"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Expected Behavior"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Clicking 'Edit Family Details' button should enable edit mode"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "All family fields should become editable (text inputs, dropdowns, etc.)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Save and Cancel buttons should appear"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "User should be able to modify family information and save changes"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Actual Behavior"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Button click produces no visible response"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Form remains in read-only mode"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "No edit controls appear"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "User cannot modify family information"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Clicking 'Edit Family Details' enables edit mode"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "All appropriate fields become editable with proper input types"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Save button calls PUT /family/{familyId} endpoint"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Cancel button reverts changes and exits edit mode"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Validation errors display properly"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Successful save updates display immediately"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Technical Context"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Frontend: React/TypeScript with Vite | API endpoints: PUT /family/{familyId}, GET /family_details | Component: frontend/src/components/FamilyManagement/FamilyDetails"
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
    "labels": ["family-management", "frontend", "bug", "ui-interaction"],
    "customfield_10225": {
      "value": "Billable"
    }
  }
}
EOF
)

RESPONSE2=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET2_BODY")

TICKET2_KEY=$(echo "$RESPONSE2" | jq -r '.key')
if [ "$TICKET2_KEY" != "null" ] && [ -n "$TICKET2_KEY" ]; then
    echo "✅ Created ticket: $TICKET2_KEY - Edit Family Details button issue"
    echo "   URL: https://nortal.atlassian.net/browse/$TICKET2_KEY"
else
    echo "❌ Failed to create ticket 2"
    echo "   Response: $RESPONSE2"
fi

echo ""
echo "=================================================="
echo "Summary:"
echo "Family Groups bug tickets creation completed"
echo "=================================================="