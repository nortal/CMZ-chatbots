#!/bin/bash

# Create Playwright Validation Tickets Script
# Creates 3 tickets for comprehensive Playwright validation
# Follows successful authentication pattern from create_environment_config_tickets.sh

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

echo "🎯 Creating Playwright Validation tickets..."

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

# Arrays to store created ticket keys
declare -a CREATED_TICKETS=()

# Variables to store individual ticket keys
DYNAMODB_VALIDATION_KEY=""
FILE_VALIDATION_KEY=""
COMPREHENSIVE_TEST_KEY=""

# Function to add a simple comment
add_simple_comment() {
    local ticket_id=$1
    local comment_text="$2"

    echo "💬 Adding comment to $ticket_id..."

    # Create temp file with comment JSON
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

# Function to create a Jira ticket
create_ticket() {
    local summary="$1"
    local description="$2"
    local story_points="$3"
    local issue_type="$4"
    local ticket_name="$5"

    echo "🎫 Creating ticket: $summary"

    # Create temp file with ticket JSON
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{
    "fields": {
        "project": {
            "key": "PR003946"
        },
        "summary": "$summary",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "$description"
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "$issue_type"
        },
        "customfield_10225": {
            "value": "Billable",
            "id": "10564"
        },
        "customfield_10014": "PR003946-61"
    }
}
EOF

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data @"$temp_file" \
        "$JIRA_BASE_URL/rest/api/3/issue")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    rm -f "$temp_file"

    if [ "$http_status" = "201" ]; then
        local ticket_key=$(echo "$response" | sed '/HTTP_STATUS:/d' | jq -r '.key')
        echo "✅ Successfully created ticket: $ticket_key"
        CREATED_TICKETS+=("$ticket_key")

        # Store ticket key in appropriate variable
        case "$ticket_name" in
            "dynamodb_validation") DYNAMODB_VALIDATION_KEY="$ticket_key" ;;
            "file_validation") FILE_VALIDATION_KEY="$ticket_key" ;;
            "comprehensive_test") COMPREHENSIVE_TEST_KEY="$ticket_key" ;;
        esac

        # Add story points as a comment
        echo "💬 Adding story points comment to $ticket_key..."
        sleep 1
        add_simple_comment "$ticket_key" "Story Points (soft estimate): $story_points — 1 point = 0.5 day"

        return 0
    else
        echo "❌ Failed to create ticket: $summary (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
        return 1
    fi
}

# Create Ticket 1: DynamoDB Playwright Validation
create_ticket \
    "Validate Playwright E2E Tests with DynamoDB Persistence" \
    "As a developer, I want comprehensive validation of Playwright end-to-end tests using DynamoDB as the persistence layer to ensure data integrity and proper CRUD operations during browser automation testing. AC1: Login Flow DynamoDB Persistence - Given a Playwright test runs login for parent1@test.cmz.org When authentication succeeds and user accesses dashboard Then verify user record exists in quest-dev-users table with correct JWT token hash And verify login timestamp is recorded in DynamoDB within 5 seconds of test execution Test: aws dynamodb get-item --table-name quest-dev-users --key userId parent1@test.cmz.org. AC2: Family CRUD Operations Persistence - Given a Playwright test creates a new family via the family management UI When family data is submitted with familyName Test Family E2E Then verify family record exists in quest-dev-family table with generated familyId And verify created.at and modified.at timestamps are ISO format and within test execution time Test: aws dynamodb scan --table-name quest-dev-family --filter-expression familyName equals Test Family E2E. AC3: Animal Configuration Persistence - Given a Playwright test modifies animal chatbot settings for Luna the Lion When configuration changes are saved Then verify updated animal record in quest-dev-animals table matches UI changes And verify configuration version number incremented by 1 Test: aws dynamodb get-item --table-name quest-dev-animals --key animalId luna-lion and compare config fields. AC4: Conversation History Persistence - Given a Playwright test conducts a chat conversation with 3+ message exchanges When each message is sent and received in the chat interface Then verify complete conversation thread exists in quest-dev-conversations table And verify message timestamps are sequential and within test execution window Test: aws dynamodb query --table-name quest-dev-conversations --key-condition-expression sessionId. AC5: Cross-Browser DynamoDB Consistency - Given Playwright tests run across all 6 browser configurations When each browser performs identical login family creation animal interaction sequence Then verify DynamoDB contains 6 distinct user sessions with unique sessionIds And verify no data corruption or race conditions between concurrent browser sessions Test: Count distinct sessionIds in quest-dev-conversations for test timeframe must equal 6. AC6: Test Data Isolation and Cleanup - Given Playwright test suite runs with workers=2 When tests complete successfully or fail Then verify test data is prefixed with test- or e2e- for identification And verify automated cleanup removes all test records within 60 seconds of test completion Test: aws dynamodb scan returns 0 items with test- prefix post-cleanup. AC7: DynamoDB Error Handling Validation - Given DynamoDB table is temporarily unavailable When Playwright test attempts family creation Then verify UI displays Data service temporarily unavailable error message And verify test doesnt crash and can recover when service restored Test: Mock DynamoDB failure verify error UI element exists restore service verify recovery" \
    "8" \
    "Task" \
    "dynamodb_validation"

sleep 2

# Create Ticket 2: File Persistence Mode Validation
create_ticket \
    "Validate Playwright E2E Tests with Local File Persistence Mode" \
    "As a developer, I want comprehensive validation of Playwright end-to-end tests using local file persistence mode (PERSISTENCE_MODE=file) to ensure data integrity and proper CRUD operations during browser automation testing in offline/development scenarios. AC1: File-Based Login Persistence - Given API runs with PERSISTENCE_MODE=file and Playwright test performs login When parent1@test.cmz.org authenticates successfully Then verify user data file exists at ./data/users/parent1@test.cmz.org.json And verify file contains valid JWT token hash and login timestamp Test: cat ./data/users/parent1@test.cmz.org.json | jq .lastLogin returns timestamp within 5 seconds. AC2: File-Based Family CRUD Operations - Given PERSISTENCE_MODE=file and Playwright test creates family File Test Family When family creation form is submitted via UI Then verify family file exists at ./data/families/{generated-uuid}.json And verify file contains familyName File Test Family and ISO timestamps Test: find ./data/families -name *.json -exec grep -l File Test Family {} semicolon returns exactly 1 file. AC3: File-Based Animal Configuration - Given PERSISTENCE_MODE=file and Playwright test modifies Lunas chatbot settings When personality changes from Friendly to Educational via UI Then verify ./data/animals/luna-lion.json contains personality Educational And verify configVersion incremented and modifiedAt updated Test: cat ./data/animals/luna-lion.json | jq .personality equals Educational. AC4: File-Based Conversation Storage - Given PERSISTENCE_MODE=file and Playwright test conducts 5-message conversation When each message exchange completes in chat interface Then verify conversation file exists at ./data/conversations/{sessionId}.json And verify file contains array of 5 message objects with sequential timestamps Test: cat ./data/conversations/{sessionId}.json | jq .messages | length equals 5. AC5: Cross-Browser File Consistency - Given PERSISTENCE_MODE=file and 3 concurrent browser sessions perform identical operations When each browser creates family with same name Concurrent Test Family Then verify 3 separate family files exist with unique UUIDs And verify no file corruption or incomplete writes Test: find ./data/families -name *.json -exec grep -l Concurrent Test Family {} semicolon | wc -l equals 3. AC6: File System Error Handling - Given PERSISTENCE_MODE=file and data directory is read-only When Playwright test attempts to create family Then verify UI displays Unable to save data error message And verify error logged contains Permission denied or similar file system error Test: Set chmod 444 ./data/families before test verify error UI element exists. AC7: File-Based Test Cleanup - Given PERSISTENCE_MODE=file and Playwright test suite completes When cleanup phase executes Then verify all files with test- prefix are removed from all data directories And verify production data files remain unchanged Test: find ./data -name *test-* | wc -l equals 0 after cleanup. AC8: DynamoDB-to-File Mode Compatibility - Given API switches from DynamoDB to PERSISTENCE_MODE=file mid-test When existing session continues with file-based operations Then verify same API responses and UI behavior as DynamoDB mode And verify session continuity maintained across persistence mode switch Test: Compare API response schemas between modes verify identical structure. AC9: File Performance Under Load - Given PERSISTENCE_MODE=file and 6 concurrent Playwright sessions When each session performs 10 rapid CRUD operations Then verify all 60 operations complete within 30 seconds And verify no file locking conflicts or partial writes Test: Measure operation completion time verify all expected files exist and are valid JSON" \
    "5" \
    "Task" \
    "file_validation"

sleep 2

# Create Ticket 3: Comprehensive Test Suite Update
create_ticket \
    "Synchronize All Test Suites with Current Jira Epic Tasks" \
    "As a developer, I want all test suites (functional, UI, unit, integration) to be synchronized with current Jira epic tasks and comprehensively validate persistence layer behavior to ensure complete test coverage across all implementation states (done, in-progress, to-do). AC1: Jira Task Discovery and Mapping - Given the Jira epic PR003946-61 contains tasks in Done In Progress and To Do states When test discovery script executes against Jira API Then generate complete mapping of all subtasks with current status And identify which tasks have corresponding test coverage Test: python scripts/discover_jira_tasks.py --epic PR003946-61 produces JSON mapping with status assignee completion date Verification: jq .tasks | group_by(.status) | map({status: .[0].status, count: length}) task_mapping.json shows counts for each status. AC2: Unit Test Synchronization - Given Jira tasks marked as Done have implemented functionality When unit test suite runs against all Done task implementations Then verify 100% of Done tasks have corresponding unit tests that pass And verify In Progress tasks have failing/skipped tests with TODO markers And verify To Do tasks have placeholder tests marked with @pytest.mark.skip Test: pytest --collect-only tests/unit/ | grep -c test_.*PR003946 equals total task count Verification: pytest tests/unit/ -v --tb=no | grep -E (PASSED|FAILED|SKIPPED) | sort | uniq -c shows expected distribution. AC3: Integration Test API Coverage - Given API endpoints exist for Done and In Progress Jira tasks When integration test suite executes against all endpoints Then verify Done endpoints return 200/201 responses with valid data And verify In Progress endpoints either work or return proper error responses And verify To Do endpoints return 404/501 with Not Implemented messages Test: curl -s http://localhost:8080/api/v1/{endpoint} | jq .code for each endpoint mapped to Jira tasks Verification: python tests/integration/validate_jira_alignment.py returns 0 exit code with coverage report. AC4: Persistence Layer Validation - DynamoDB Mode - Given API runs with default DynamoDB persistence and Jira tasks involve data operations When integration tests execute CRUD operations for each Done task Then verify data persists correctly to appropriate DynamoDB tables And verify audit timestamps (created.at modified.at) are populated And verify data retrieval matches what was stored Test: aws dynamodb scan --table-name quest-dev-{domain} --select COUNT before/after each test Verification: python tests/persistence/validate_dynamodb_state.py --mode integration confirms data integrity. AC5: Persistence Layer Validation - File Mode - Given API runs with PERSISTENCE_MODE=file and same Jira task operations When integration tests execute identical CRUD operations Then verify data persists to local JSON files with same structure as DynamoDB And verify file-based operations maintain referential integrity And verify concurrent operations dont corrupt files Test: find ./data -name *.json -exec jq keys {} semicolon | sort | uniq matches expected schema Verification: python tests/persistence/validate_file_state.py --mode integration confirms file integrity. AC6: UI Test Playwright Synchronization - Given Playwright tests exist for user-facing functionality When UI test suite runs against features mapped to Jira tasks Then verify Done tasks have working UI flows across all 6 browsers And verify In Progress tasks either work or show appropriate Coming Soon messages And verify To Do tasks show placeholder UI or are hidden from users Test: FRONTEND_URL=http://localhost:3001 npx playwright test --list | grep -c PR003946 equals UI-relevant task count Verification: FRONTEND_URL=http://localhost:3001 npx playwright test --grep PR003946 --reporter=json shows expected pass/fail/skip distribution." \
    "13" \
    "Task" \
    "comprehensive_test"

echo ""
echo "🎉 Successfully created all Playwright validation tickets!"
echo ""
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for ticket in "${CREATED_TICKETS[@]}"; do
    echo "✅ $ticket - https://nortal.atlassian.net/browse/$ticket"
done
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 All tickets are linked to Parent Epic: PR003946-61"
echo "💰 All tickets are marked as Billable"
echo "📝 Story points added as comments for estimation"
echo ""
echo "Next steps:"
echo "1. Review tickets in Jira for accuracy"
echo "2. Assign tickets to appropriate team members"
echo "3. Move tickets to appropriate workflow status"
echo "4. Begin implementation following acceptance criteria"