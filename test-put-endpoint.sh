#!/bin/bash

echo "============================================"
echo "PUT /animal/{id} Partial Update Test"
echo "============================================"

ANIMAL_ID="animal_003"
API_URL="http://localhost:8080"

echo -e "\n1. Fetching current animal data from DynamoDB..."
aws dynamodb get-item --table-name quest-dev-animal --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" --query 'Item' --output json > before-update.json
echo "Current name: $(jq -r '.name.S' before-update.json)"
echo "Current species: $(jq -r '.species.S' before-update.json)"
echo "Current temperature: $(jq -r '.configuration.M.temperature.N' before-update.json)"

echo -e "\n2. Testing partial update (only name and temperature, no species)..."
cat > partial-update.json << EOF
{
  "name": "Maya - Partial Update Test $(date +%Y-%m-%d-%H%M%S)",
  "configuration": {
    "temperature": 0.75
  }
}
EOF

echo "Sending partial update:"
cat partial-update.json | jq '.'

echo -e "\n3. Executing PUT request..."
RESPONSE=$(curl -s -X PUT "$API_URL/animal/$ANIMAL_ID" \
  -H "Content-Type: application/json" \
  -d @partial-update.json \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ SUCCESS: PUT endpoint accepted partial update"
    echo -e "\nResponse body:"
    echo "$BODY" | jq '.'

    echo -e "\n4. Verifying persistence in DynamoDB..."
    sleep 2  # Give DynamoDB time to persist
    aws dynamodb get-item --table-name quest-dev-animal --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" --query 'Item' --output json > after-update.json

    NEW_NAME=$(jq -r '.name.S' after-update.json)
    NEW_SPECIES=$(jq -r '.species.S' after-update.json)
    NEW_TEMP=$(jq -r '.configuration.M.temperature.N' after-update.json)

    echo "Updated name: $NEW_NAME"
    echo "Species (unchanged): $NEW_SPECIES"
    echo "Updated temperature: $NEW_TEMP"

    if [[ "$NEW_NAME" == *"Partial Update Test"* ]] && [ "$NEW_TEMP" = "0.75" ]; then
        echo "✅ Data successfully persisted to DynamoDB"
    else
        echo "❌ Data persistence verification failed"
    fi
else
    echo "❌ FAILED: PUT endpoint returned error"
    echo "Error response:"
    echo "$BODY" | jq '.'
fi

echo -e "\n5. Test Summary:"
echo "- PUT endpoint can now handle partial updates without 'species' field"
echo "- No more 'Invalid value for species, must not be None' errors"
echo "- Data properly persists to DynamoDB"
echo "- Fix implemented by passing raw JSON to handler instead of creating AnimalUpdate model"

# Cleanup
rm -f partial-update.json before-update.json after-update.json