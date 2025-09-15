#!/bin/bash

# Create Jira ticket for Frontend-Backend Regression Prevention System
# Based on successful pattern from create_environment_config_tickets.sh

set -e

# Check if required environment variables are set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    exit 1
fi

if [ -z "$JIRA_EMAIL" ]; then
    echo "Error: JIRA_EMAIL environment variable is not set"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"

# Create base64 encoded credentials for Basic Auth
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🎯 Creating Frontend-Backend Regression Prevention System ticket..."

# Test API connectivity first
echo "🔌 Testing API connectivity..."
test_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic $JIRA_CREDENTIALS" \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/myself")

test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)

if [ "$test_http_status" != "200" ]; then
    echo "❌ API connectivity test failed"
    exit 1
fi

echo "✅ API connectivity confirmed"

# Function to add a simple comment
add_simple_comment() {
    local ticket_id=$1
    local comment_text="$2"

    echo "💬 Adding comment to $ticket_id..."

    # Create temp file with simple comment
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{
    "body": {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "$comment_text"
                    }
                ]
            }
        ]
    }
}
EOF

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data @"$temp_file" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    rm -f "$temp_file"

    if [ "$http_status" = "201" ]; then
        echo "✅ Successfully added comment to $ticket_id"
    else
        echo "❌ Failed to add comment to $ticket_id (HTTP $http_status)"
    fi
}

# Create the main ticket
echo "🎫 Creating ticket: Implement Comprehensive Frontend-Backend Regression Prevention System"

# Create temp file with ticket JSON
temp_file=$(mktemp)
cat > "$temp_file" <<'EOF'
{
    "fields": {
        "project": {
            "key": "PR003946"
        },
        "summary": "Implement Comprehensive Frontend-Backend Regression Prevention System",
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
                            "text": "The CMZ platform experiences recurring critical issues that break development workflow:"
                        }
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "OpenAPI Code Generation Destroys Implementations (30+ occurrences per regeneration)",
                                            "marks": [{"type": "strong"}]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Frontend-Backend Contract Drift - Frontend calls endpoints that don't exist",
                                            "marks": [{"type": "strong"}]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Lost Development Time - 1-2 hours per incident to diagnose and fix",
                                            "marks": [{"type": "strong"}]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Solution Components"}]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Post-Generation Validation Script (scripts/post_generation_validation.py)"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Automatic Controller Fixer (scripts/fix_controller_signatures.py)"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Contract Testing Script (scripts/frontend_backend_contract_test.py)"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Makefile Integration (make post-generate, make validate-api)"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "CLAUDE.md CRITICAL validation note update"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Re-Opening Criteria"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This ticket should be RE-OPENED if ANY of the following occur:",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Any occurrence of 'do some magic!' in generated controllers"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Missing body parameters after running make post-generate"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "404 errors for endpoints that should exist"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Validation taking > 30 seconds"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "Task"
        },
        "customfield_10225": {
            "value": "Billable",
            "id": "10564"
        },
        "customfield_10014": "PR003946-61",
        "priority": {
            "name": "Critical"
        },
        "labels": ["technical-debt", "regression-prevention", "api-validation", "critical-infrastructure"]
    }
}
EOF

response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic $JIRA_CREDENTIALS" \
    -H "Content-Type: application/json" \
    --data @"$temp_file" \
    "$JIRA_BASE_URL/rest/api/3/issue")

http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

rm -f "$temp_file"

if [ "$http_status" = "201" ]; then
    ticket_key=$(echo "$response" | sed '/HTTP_STATUS:/d' | jq -r '.key')
    echo "✅ Successfully created ticket: $ticket_key"

    # Add story points comment
    sleep 2
    add_simple_comment "$ticket_key" "Story Points: 8 — This is a critical infrastructure improvement that will save hours of development time"

    # Add acceptance criteria as a comment
    sleep 2
    add_simple_comment "$ticket_key" "ACCEPTANCE CRITERIA:
Basic Functionality:
- Post-generation validation script identifies all controller signature issues
- Automatic fixer corrects all problems without manual intervention
- Contract tester detects all frontend API calls and validates against backend
- Makefile targets work correctly: make validate-api and make post-generate
- CLAUDE.md updated with CRITICAL note about mandatory validation

Stress Testing (5 scenarios):
1. Body Parameter Handling - Add endpoint with request body, verify controller has body parameter
2. Multiple Parameter Types - Add endpoint with path/query/body params, verify all present
3. Frontend-Backend Mismatch Detection - Add invalid frontend call, verify detection
4. Regeneration Preservation - Generate 3x, verify implementation still works
5. Bulk Endpoint Addition - Add 10 endpoints at once, verify all generate correctly

Performance:
- Validation completes in < 10 seconds
- Fixing completes in < 5 seconds
- Contract testing completes in < 30 seconds"

    # Add test instructions as a comment
    sleep 2
    add_simple_comment "$ticket_key" "TEST INSTRUCTIONS:
1. Run: make post-generate (should complete without errors)
2. Add endpoint with body to OpenAPI spec
3. Run: make generate-api (without validation)
4. Verify issues present
5. Run: make validate-api
6. Verify issues detected and reported
7. Run: make post-generate
8. Verify issues fixed automatically
9. Test all 5 stress scenarios from acceptance criteria
10. Verify no regression issues for 30 days post-implementation"

    # Add success metrics as a comment
    sleep 2
    add_simple_comment "$ticket_key" "SUCCESS METRICS:
- Zero controller generation failures in 30 days
- 100% of MRs pass validation checks
- Zero production incidents from frontend-backend mismatches
- 50% reduction in time spent fixing generation issues
- 90% team satisfaction with new workflow

CRITICAL: If any regression returns, re-open this ticket immediately with failure details"

    # Display ticket URL
    echo ""
    echo "📋 Ticket created successfully!"
    echo "🔗 View ticket: $JIRA_BASE_URL/browse/$ticket_key"
    echo ""
    echo "📄 Full documentation available in:"
    echo "   - jira-ticket-prevent-regressions.md"
    echo "   - PREVENT-REGRESSIONS-SOLUTION.md"
    echo ""
    echo "⚠️  CRITICAL: Update CLAUDE.md with mandatory validation note after implementation"

else
    echo "❌ Failed to create ticket (HTTP $http_status)"
    echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
    exit 1
fi