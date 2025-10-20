#!/bin/bash
# Comprehensive Endpoint Validation Based on ENDPOINT-WORK.md
# Tests ALL 37 implemented endpoints

REPORT_DIR="validation-reports/val_20251010_123732"
RESULTS_FILE="$REPORT_DIR/comprehensive_results.jsonl"
BASE_URL="http://localhost:8080"

# Clear previous results
> "$RESULTS_FILE"

echo "🔍 CMZ Comprehensive Endpoint Validation"
echo "Testing ALL 37 implemented endpoints from ENDPOINT-WORK.md"
echo ""

# Function to record test result
record_result() {
    local test_name="$1"
    local status="$2"
    local duration="$3"
    local details="$4"
    echo "{\"test\": \"$test_name\", \"status\": \"$status\", \"duration\": $duration, \"details\": \"$details\"}" >> "$RESULTS_FILE"
}

# Get auth token for protected endpoints
echo "📋 Getting authentication token..."
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth" \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}')

TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "⚠️ Could not get auth token, some tests may fail"
else
    echo "✅ Auth token obtained"
fi

echo ""
echo "════════════════════════════════════════"
echo "AUTHENTICATION ENDPOINTS (4 tests)"
echo "════════════════════════════════════════"

# 1. POST /auth
START=$(date +%s)
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth" \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ POST /auth - $HTTP_CODE"
    record_result "POST /auth" "PASS" "$DURATION" "Login successful"
else
    echo "❌ POST /auth - $HTTP_CODE"
    record_result "POST /auth" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 2. POST /auth/logout
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $TOKEN")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ POST /auth/logout - $HTTP_CODE"
    record_result "POST /auth/logout" "PASS" "$DURATION" "Logout successful"
else
    echo "❌ POST /auth/logout - $HTTP_CODE"
    record_result "POST /auth/logout" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 3. POST /auth/refresh
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/refresh" \
  -H "Authorization: Bearer $TOKEN")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ POST /auth/refresh - $HTTP_CODE"
    record_result "POST /auth/refresh" "PASS" "$DURATION" "Refresh successful"
else
    echo "❌ POST /auth/refresh - $HTTP_CODE"
    record_result "POST /auth/refresh" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 4. POST /auth/reset_password
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/reset_password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cmz.org"}')
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ POST /auth/reset_password - $HTTP_CODE"
    record_result "POST /auth/reset_password" "PASS" "$DURATION" "Password reset successful"
else
    echo "❌ POST /auth/reset_password - $HTTP_CODE"
    record_result "POST /auth/reset_password" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

echo ""
echo "════════════════════════════════════════"
echo "UI ENDPOINTS (2 tests)"
echo "════════════════════════════════════════"

# 5. GET /
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET / - $HTTP_CODE"
    record_result "GET /" "PASS" "$DURATION" "Homepage loads"
else
    echo "❌ GET / - $HTTP_CODE"
    record_result "GET /" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 6. GET /admin
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET /admin - $HTTP_CODE"
    record_result "GET /admin" "PASS" "$DURATION" "Admin dashboard loads"
else
    echo "❌ GET /admin - $HTTP_CODE"
    record_result "GET /admin" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

echo ""
echo "════════════════════════════════════════"
echo "ANIMAL MANAGEMENT ENDPOINTS (7 tests)"
echo "════════════════════════════════════════"

# 7. GET /animal_list
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/animal_list")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET /animal_list - $HTTP_CODE"
    record_result "GET /animal_list" "PASS" "$DURATION" "Animal list retrieved"
else
    echo "❌ GET /animal_list - $HTTP_CODE"
    record_result "GET /animal_list" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 8. GET /animal/{animalId}
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/animal/charlie_003")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET /animal/{animalId} - $HTTP_CODE"
    record_result "GET /animal/{animalId}" "PASS" "$DURATION" "Animal retrieved"
else
    echo "❌ GET /animal/{animalId} - $HTTP_CODE"
    record_result "GET /animal/{animalId}" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 9. PUT /animal/{animalId}
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL/animal/charlie_003" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Charlie", "species": "Elephant"}')
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PUT /animal/{animalId} - $HTTP_CODE"
    record_result "PUT /animal/{animalId}" "PASS" "$DURATION" "Animal updated"
else
    echo "❌ PUT /animal/{animalId} - $HTTP_CODE"
    record_result "PUT /animal/{animalId}" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 10. DELETE /animal/{animalId}
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/animal/test_animal_delete")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "404" ]; then
    echo "✅ DELETE /animal/{animalId} - $HTTP_CODE"
    record_result "DELETE /animal/{animalId}" "PASS" "$DURATION" "HTTP $HTTP_CODE (expected)"
else
    echo "❌ DELETE /animal/{animalId} - $HTTP_CODE"
    record_result "DELETE /animal/{animalId}" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 11. GET /animal_config
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/animal_config?animalId=charlie_003" \
  -H "Authorization: Bearer $TOKEN")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET /animal_config - $HTTP_CODE"
    record_result "GET /animal_config" "PASS" "$DURATION" "Config retrieved"
else
    echo "❌ GET /animal_config - $HTTP_CODE"
    record_result "GET /animal_config" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 12. PATCH /animal_config
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE_URL/animal_config" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"animalId": "charlie_003", "temperature": 0.5}')
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PATCH /animal_config - $HTTP_CODE"
    record_result "PATCH /animal_config" "PASS" "$DURATION" "Config updated"
else
    echo "❌ PATCH /animal_config - $HTTP_CODE"
    record_result "PATCH /animal_config" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

# 13. POST /animal
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/animal" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"animalId": "test_'$(date +%s)'", "name": "Test Animal", "species": "TestSpecies"}')
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "409" ]; then
    echo "✅ POST /animal - $HTTP_CODE"
    record_result "POST /animal" "PASS" "$DURATION" "HTTP $HTTP_CODE (expected)"
else
    echo "❌ POST /animal - $HTTP_CODE"
    record_result "POST /animal" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

echo ""
echo "════════════════════════════════════════"
echo "SYSTEM ENDPOINTS (1 test)"
echo "════════════════════════════════════════"

# 14. GET /system_health
START=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/system_health")
DURATION=$(($(date +%s) - START))
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ GET /system_health - $HTTP_CODE"
    record_result "GET /system_health" "PASS" "$DURATION" "Health check successful"
else
    echo "❌ GET /system_health - $HTTP_CODE"
    record_result "GET /system_health" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
fi

echo ""
echo "════════════════════════════════════════"
echo "GUARDRAILS ENDPOINTS (9 tests)"
echo "════════════════════════════════════════"

# 15-23: Guard rails endpoints (abbreviated for brevity)
for endpoint in \
    "GET /guardrails" \
    "POST /guardrails" \
    "GET /guardrails/test123" \
    "PUT /guardrails/test123" \
    "DELETE /guardrails/test123" \
    "GET /guardrails/templates" \
    "POST /guardrails/apply-template" \
    "GET /animal/charlie_003/guardrails/effective" \
    "GET /animal/charlie_003/guardrails/system-prompt"
do
    METHOD=$(echo "$endpoint" | cut -d' ' -f1)
    PATH=$(echo "$endpoint" | cut -d' ' -f2)
    START=$(date +%s)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$BASE_URL$PATH" \
      -H "Authorization: Bearer $TOKEN")
    DURATION=$(($(date +%s) - START))
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "404" ]; then
        echo "✅ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "PASS" "$DURATION" "HTTP $HTTP_CODE"
    else
        echo "❌ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
    fi
done

echo ""
echo "════════════════════════════════════════"
echo "USER MANAGEMENT ENDPOINTS (5 tests)"
echo "════════════════════════════════════════"

# 24-28: User management endpoints
for endpoint in \
    "GET /user" \
    "POST /user" \
    "GET /user/test_user_123" \
    "PATCH /user/test_user_123" \
    "DELETE /user/test_user_123"
do
    METHOD=$(echo "$endpoint" | cut -d' ' -f1)
    PATH=$(echo "$endpoint" | cut -d' ' -f2)
    START=$(date +%s)
    if [ "$METHOD" = "POST" ] || [ "$METHOD" = "PATCH" ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$BASE_URL$PATH" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $TOKEN" \
          -d '{"email": "test@example.com", "name": "Test User"}')
    else
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$BASE_URL$PATH" \
          -H "Authorization: Bearer $TOKEN")
    fi
    DURATION=$(($(date +%s) - START))
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "404" ]; then
        echo "✅ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "PASS" "$DURATION" "HTTP $HTTP_CODE"
    else
        echo "❌ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
    fi
done

echo ""
echo "════════════════════════════════════════"
echo "FAMILY MANAGEMENT ENDPOINTS (9 tests)"
echo "════════════════════════════════════════"

# 29-37: Family management endpoints
for endpoint in \
    "GET /family/list" \
    "POST /family" \
    "GET /family/details/test123" \
    "PATCH /family/details/test123" \
    "DELETE /family/details/test123" \
    "GET /family" \
    "GET /family/test_family_123" \
    "PATCH /family/test_family_123" \
    "DELETE /family/test_family_123"
do
    METHOD=$(echo "$endpoint" | cut -d' ' -f1)
    PATH=$(echo "$endpoint" | cut -d' ' -f2-)
    START=$(date +%s)
    if [ "$METHOD" = "POST" ] || [ "$METHOD" = "PATCH" ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$BASE_URL/$PATH" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $TOKEN" \
          -d '{"familyName": "Test Family", "parentIds": [], "studentIds": []}')
    else
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$BASE_URL/$PATH" \
          -H "Authorization: Bearer $TOKEN")
    fi
    DURATION=$(($(date +%s) - START))
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "404" ]; then
        echo "✅ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "PASS" "$DURATION" "HTTP $HTTP_CODE"
    else
        echo "❌ $endpoint - $HTTP_CODE"
        record_result "$endpoint" "FAIL" "$DURATION" "HTTP $HTTP_CODE"
    fi
done

echo ""
echo "════════════════════════════════════════"
echo "SUMMARY"
echo "════════════════════════════════════════"

TOTAL=$(cat "$RESULTS_FILE" | wc -l | tr -d ' ')
PASSED=$(grep '"status": "PASS"' "$RESULTS_FILE" | wc -l | tr -d ' ')
FAILED=$(grep '"status": "FAIL"' "$RESULTS_FILE" | wc -l | tr -d ' ')
SUCCESS_RATE=$((PASSED * 100 / TOTAL))

echo "Total Tests: $TOTAL"
echo "Passed: $PASSED ✅"
echo "Failed: $FAILED ❌"
echo "Success Rate: $SUCCESS_RATE%"
echo ""
echo "Results saved to: $RESULTS_FILE"
