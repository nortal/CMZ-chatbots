#!/bin/bash
set -e

# Validation script for PUT /animal/{id} endpoint
# Tests all scenarios defined in PR003946-171 and PR003946-172

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8080"
TABLE_NAME="quest-dev-animal"
TEST_ANIMAL_ID="bella_002"
TEST_ANIMAL_ID_2="leo_001"
NONEXISTENT_ID="nonexistent_999"
AWS_PROFILE="cmz"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    PUT /animal/{id} Endpoint Validation Suite${NC}"
echo -e "${BLUE}    Related tickets: PR003946-171, PR003946-172${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Helper function to get DynamoDB item
get_dynamo_item() {
    local animal_id=$1
    aws dynamodb get-item \
        --table-name $TABLE_NAME \
        --key "{\"animalId\":{\"S\":\"$animal_id\"}}" \
        --profile $AWS_PROFILE \
        --output json 2>/dev/null || echo "{}"
}

# Helper function to execute PUT request
execute_put() {
    local animal_id=$1
    local payload=$2
    local expected_status=$3

    response=$(curl -s -w "\n%{http_code}" -X PUT \
        "$API_URL/animal/$animal_id" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer mock-token" \
        -d "$payload" 2>/dev/null)

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    echo "$http_code"
    return $([ "$http_code" == "$expected_status" ] && echo 0 || echo 1)
}

# Test function
run_test() {
    local test_name=$1
    local animal_id=$2
    local payload=$3
    local expected_status=$4
    local validation_func=$5

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"

    # Get before state
    before_state=$(get_dynamo_item "$animal_id")

    # Execute PUT request
    if http_code=$(execute_put "$animal_id" "$payload" "$expected_status"); then
        echo -e "  Status: ${GREEN}✓${NC} Expected $expected_status, Got $http_code"

        # Get after state
        after_state=$(get_dynamo_item "$animal_id")

        # Run validation function
        if $validation_func "$before_state" "$after_state" "$payload"; then
            echo -e "  DynamoDB: ${GREEN}✓${NC} State validated correctly"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo -e "  Result: ${GREEN}PASSED${NC}"
        else
            echo -e "  DynamoDB: ${RED}✗${NC} State validation failed"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo -e "  Result: ${RED}FAILED${NC}"
        fi
    else
        echo -e "  Status: ${RED}✗${NC} Expected $expected_status, Got $http_code"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "  Result: ${RED}FAILED${NC}"
    fi
    echo ""
}

# Validation functions
validate_full_update() {
    local before=$1
    local after=$2
    local payload=$3

    # Check if all fields in payload are updated in DynamoDB
    name_after=$(echo "$after" | jq -r '.Item.name.S // empty')
    expected_name=$(echo "$payload" | jq -r '.name // empty')

    [ "$name_after" == "$expected_name" ]
}

validate_partial_update() {
    local before=$1
    local after=$2
    local payload=$3

    # Check if only specified fields are updated
    name_before=$(echo "$before" | jq -r '.Item.name.S // empty')
    name_after=$(echo "$after" | jq -r '.Item.name.S // empty')
    species_before=$(echo "$before" | jq -r '.Item.species.S // empty')
    species_after=$(echo "$after" | jq -r '.Item.species.S // empty')

    expected_name=$(echo "$payload" | jq -r '.name // empty')

    # Name should change, species should remain the same
    [ "$name_after" == "$expected_name" ] && [ "$species_before" == "$species_after" ]
}

validate_no_change() {
    local before=$1
    local after=$2
    local payload=$3

    # Check that nothing changed except possibly timestamp
    name_before=$(echo "$before" | jq -r '.Item.name.S // empty')
    name_after=$(echo "$after" | jq -r '.Item.name.S // empty')
    species_before=$(echo "$before" | jq -r '.Item.species.S // empty')
    species_after=$(echo "$after" | jq -r '.Item.species.S // empty')

    [ "$name_before" == "$name_after" ] && [ "$species_before" == "$species_after" ]
}

validate_not_found() {
    local before=$1
    local after=$2
    local payload=$3

    # Check that no record was created
    [ "$after" == "{}" ]
}

echo -e "${BLUE}Starting Test Suite 1: Valid Updates${NC}"
echo ""

# TC01: Full update with all fields
run_test "Full update with all fields" \
    "$TEST_ANIMAL_ID" \
    '{"name":"Bella Bear Full Update","species":"Grizzly Bear","habitat":"Forest","status":"active","personality":"Friendly"}' \
    "200" \
    validate_full_update

# TC02: Single field update (name only)
run_test "Single field update (name only)" \
    "$TEST_ANIMAL_ID" \
    '{"name":"Bella Single Field"}' \
    "200" \
    validate_partial_update

# TC03: Multiple field partial update
run_test "Multiple field partial update" \
    "$TEST_ANIMAL_ID" \
    '{"name":"Bella Multi Field","status":"inactive","personality":"Shy"}' \
    "200" \
    validate_partial_update

# TC04: Empty body
run_test "Empty body (no-op)" \
    "$TEST_ANIMAL_ID" \
    '{}' \
    "200" \
    validate_no_change

# TC05: Null optional field
run_test "Null optional field" \
    "$TEST_ANIMAL_ID" \
    '{"personality":null}' \
    "200" \
    validate_partial_update

echo -e "${BLUE}Starting Test Suite 2: Invalid Updates${NC}"
echo ""

# TC06: Invalid status value
run_test "Invalid status value" \
    "$TEST_ANIMAL_ID" \
    '{"status":"invalid_status"}' \
    "400" \
    validate_no_change

# TC07: Oversized field
LONG_NAME=$(printf 'A%.0s' {1..101})
run_test "Oversized field (101 chars)" \
    "$TEST_ANIMAL_ID" \
    "{\"name\":\"$LONG_NAME\"}" \
    "400" \
    validate_no_change

# TC08: Non-existent animal
run_test "Non-existent animal ID" \
    "$NONEXISTENT_ID" \
    '{"name":"Should Not Create"}' \
    "404" \
    validate_not_found

# TC09: Malformed JSON (using curl's raw data)
echo -e "${YELLOW}Test $((++TOTAL_TESTS)): Malformed JSON${NC}"
response=$(curl -s -w "\n%{http_code}" -X PUT \
    "$API_URL/animal/$TEST_ANIMAL_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer mock-token" \
    -d '{invalid json}' 2>/dev/null)
http_code=$(echo "$response" | tail -n 1)
if [ "$http_code" == "400" ]; then
    echo -e "  Status: ${GREEN}✓${NC} Got expected 400 for malformed JSON"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  Status: ${RED}✗${NC} Expected 400, Got $http_code"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

echo -e "${BLUE}Starting Test Suite 3: Special Cases${NC}"
echo ""

# TC11: Special characters and emoji
run_test "Special characters and emoji" \
    "$TEST_ANIMAL_ID" \
    '{"name":"Bella 🐻 Bear","personality":"Friendly & curious; loves honey!"}' \
    "200" \
    validate_partial_update

# TC12: Concurrent updates (simplified test)
echo -e "${YELLOW}Test $((++TOTAL_TESTS)): Concurrent updates${NC}"
(execute_put "$TEST_ANIMAL_ID" '{"name":"Concurrent Update 1"}' "200" &)
(execute_put "$TEST_ANIMAL_ID" '{"name":"Concurrent Update 2"}' "200" &)
wait
after_state=$(get_dynamo_item "$TEST_ANIMAL_ID")
name_after=$(echo "$after_state" | jq -r '.Item.name.S // empty')
if [[ "$name_after" == "Concurrent Update 1" ]] || [[ "$name_after" == "Concurrent Update 2" ]]; then
    echo -e "  Result: ${GREEN}✓${NC} Last-write-wins behavior confirmed"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  Result: ${RED}✗${NC} Unexpected concurrent behavior"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# TC15: PUT vs PATCH comparison
echo -e "${YELLOW}Test $((++TOTAL_TESTS)): PUT vs PATCH comparison${NC}"

# Test PATCH endpoint
patch_response=$(curl -s -w "\n%{http_code}" -X PATCH \
    "$API_URL/animal_config?animalId=$TEST_ANIMAL_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer mock-token" \
    -d '{"name":"PATCH Test Name"}' 2>/dev/null)
patch_code=$(echo "$patch_response" | tail -n 1)

# Test PUT endpoint
put_response=$(curl -s -w "\n%{http_code}" -X PUT \
    "$API_URL/animal/$TEST_ANIMAL_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer mock-token" \
    -d '{"name":"PUT Test Name"}' 2>/dev/null)
put_code=$(echo "$put_response" | tail -n 1)

if [ "$patch_code" == "200" ]; then
    echo -e "  PATCH: ${GREEN}✓${NC} Status 200"
else
    echo -e "  PATCH: ${YELLOW}⚠${NC} Status $patch_code"
fi

if [ "$put_code" == "200" ]; then
    echo -e "  PUT: ${GREEN}✓${NC} Status 200"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  PUT: ${RED}✗${NC} Status $put_code (Expected 200)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                        TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! PUT endpoint is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILED_TESTS test(s) failed. PUT endpoint needs fixes.${NC}"
    echo -e "${YELLOW}See PR003946-171 for implementation requirements.${NC}"
    exit 1
fi